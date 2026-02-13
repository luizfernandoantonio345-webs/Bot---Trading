"""
Estratégia de Trading Simples - Cruzamento de Médias Móveis
"""
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SimpleMovingAverageStrategy:
    """
    Estratégia de cruzamento de médias móveis
    
    Sinais:
    - COMPRA: MA rápida cruza acima da MA lenta
    - VENDA: MA rápida cruza abaixo da MA lenta
    """
    
    def __init__(
        self,
        fast_period: int = 9,
        slow_period: int = 21,
        min_score: float = 70.0
    ):
        """
        Args:
            fast_period: Período da MA rápida
            slow_period: Período da MA lenta
            min_score: Score mínimo para executar trade
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.min_score = min_score
        
        self.last_signal = None
        self.last_ma_fast = None
        self.last_ma_slow = None
    
    def calculate_sma(self, prices: List[float], period: int) -> float:
        """Calcula Simple Moving Average"""
        if len(prices) < period:
            return None
        return np.mean(prices[-period:])
    
    def analyze(self, prices: List[float]) -> Dict:
        """
        Analisa preços e retorna sinal
        
        Args:
            prices: Lista de preços (do mais antigo ao mais recente)
            
        Returns:
            Dict com sinal, score e detalhes
        """
        if len(prices) < self.slow_period + 1:
            return {
                'signal': 'WAIT',
                'score': 0,
                'reason': f'Dados insuficientes (precisa {self.slow_period + 1} períodos)',
                'ma_fast': None,
                'ma_slow': None
            }
        
        # Calcular MAs atuais
        ma_fast = self.calculate_sma(prices, self.fast_period)
        ma_slow = self.calculate_sma(prices, self.slow_period)
        
        # Calcular MAs anteriores
        ma_fast_prev = self.calculate_sma(prices[:-1], self.fast_period)
        ma_slow_prev = self.calculate_sma(prices[:-1], self.slow_period)
        
        # Inicializar resultado
        result = {
            'signal': 'WAIT',
            'score': 0,
            'reason': '',
            'ma_fast': round(ma_fast, 2),
            'ma_slow': round(ma_slow, 2),
            'ma_fast_prev': round(ma_fast_prev, 2),
            'ma_slow_prev': round(ma_slow_prev, 2),
            'current_price': round(prices[-1], 2)
        }
        
        # Detectar cruzamentos
        # COMPRA: MA rápida cruza acima da MA lenta
        if ma_fast > ma_slow and ma_fast_prev <= ma_slow_prev:
            result['signal'] = 'BUY'
            result['reason'] = f'Cruzamento de alta: MA{self.fast_period} cruza acima de MA{self.slow_period}'
            result['score'] = self._calculate_score(prices, ma_fast, ma_slow, 'BUY')
        
        # VENDA: MA rápida cruza abaixo da MA lenta
        elif ma_fast < ma_slow and ma_fast_prev >= ma_slow_prev:
            result['signal'] = 'SELL'
            result['reason'] = f'Cruzamento de baixa: MA{self.fast_period} cruza abaixo de MA{self.slow_period}'
            result['score'] = self._calculate_score(prices, ma_fast, ma_slow, 'SELL')
        
        # Nenhum cruzamento
        else:
            if ma_fast > ma_slow:
                result['reason'] = f'Tendência de alta, aguardando oportunidade'
            else:
                result['reason'] = f'Tendência de baixa, aguardando oportunidade'
            result['score'] = 0
        
        # Salvar estado
        self.last_ma_fast = ma_fast
        self.last_ma_slow = ma_slow
        self.last_signal = result['signal']
        
        # Log
        if result['signal'] != 'WAIT':
            logger.info(
                f"Sinal detectado: {result['signal']} | "
                f"Score: {result['score']:.1f} | "
                f"MA{self.fast_period}: {ma_fast:.2f}, MA{self.slow_period}: {ma_slow:.2f}"
            )
        
        return result
    
    def _calculate_score(
        self,
        prices: List[float],
        ma_fast: float,
        ma_slow: float,
        signal: str
    ) -> float:
        """
        Calcula score de confiança do sinal (0-100)
        
        Baseado em:
        - Distância entre as MAs (quanto maior, mais forte o sinal)
        - Momentum recente
        - Volatilidade
        """
        score = 50.0  # Base
        
        # 1. Força da separação das MAs (0-25 pontos)
        ma_diff = abs(ma_fast - ma_slow)
        ma_diff_pct = (ma_diff / ma_slow) * 100
        
        if ma_diff_pct > 2.0:
            score += 25
        elif ma_diff_pct > 1.0:
            score += 15
        elif ma_diff_pct > 0.5:
            score += 10
        else:
            score += 5
        
        # 2. Momentum (0-15 pontos)
        recent_prices = prices[-5:]
        if len(recent_prices) >= 5:
            momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
            
            if signal == 'BUY' and momentum > 0:
                score += min(15, momentum * 1000)
            elif signal == 'SELL' and momentum < 0:
                score += min(15, abs(momentum) * 1000)
        
        # 3. Volatilidade controlada (0-10 pontos)
        if len(prices) >= 20:
            volatility = np.std(prices[-20:]) / np.mean(prices[-20:])
            
            # Preferir volatilidade moderada
            if 0.01 < volatility < 0.05:
                score += 10
            elif volatility < 0.01:
                score += 5  # Muito baixa
            else:
                score += 2  # Muito alta
        
        return min(100, max(0, score))
    
    def should_execute(self, analysis: Dict) -> bool:
        """
        Decide se deve executar o trade baseado na análise
        
        Returns:
            True se deve executar
        """
        if analysis['signal'] == 'WAIT':
            return False
        
        if analysis['score'] < self.min_score:
            logger.info(
                f"Sinal {analysis['signal']} ignorado: "
                f"Score {analysis['score']:.1f} < {self.min_score}"
            )
            return False
        
        return True
    
    def get_stop_loss(self, entry_price: float, signal: str) -> float:
        """
        Calcula stop loss baseado na estratégia
        
        Args:
            entry_price: Preço de entrada
            signal: BUY ou SELL
            
        Returns:
            Preço do stop loss
        """
        # Stop loss de 2% para esta estratégia
        stop_loss_pct = 0.02
        
        if signal == 'BUY':
            # Stop abaixo do preço de entrada
            return entry_price * (1 - stop_loss_pct)
        else:  # SELL
            # Stop acima do preço de entrada
            return entry_price * (1 + stop_loss_pct)
    
    def get_take_profit(self, entry_price: float, signal: str) -> float:
        """
        Calcula take profit baseado na estratégia
        
        Args:
            entry_price: Preço de entrada
            signal: BUY ou SELL
            
        Returns:
            Preço do take profit
        """
        # Take profit de 4% (R:R de 1:2)
        take_profit_pct = 0.04
        
        if signal == 'BUY':
            # Target acima do preço de entrada
            return entry_price * (1 + take_profit_pct)
        else:  # SELL
            # Target abaixo do preço de entrada
            return entry_price * (1 - take_profit_pct)


class RSIStrategy:
    """
    Estratégia baseada em RSI (Relative Strength Index)
    
    Sinais:
    - COMPRA: RSI < 30 (oversold)
    - VENDA: RSI > 70 (overbought)
    """
    
    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def calculate_rsi(self, prices: List[float]) -> Optional[float]:
        """Calcula RSI"""
        if len(prices) < self.period + 1:
            return None
        
        deltas = np.diff(prices[-self.period-1:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def analyze(self, prices: List[float]) -> Dict:
        """Analisa preços e retorna sinal"""
        rsi = self.calculate_rsi(prices)
        
        if rsi is None:
            return {
                'signal': 'WAIT',
                'score': 0,
                'reason': f'Dados insuficientes (precisa {self.period + 1} períodos)',
                'rsi': None
            }
        
        result = {
            'signal': 'WAIT',
            'score': 0,
            'reason': '',
            'rsi': round(rsi, 2),
            'current_price': round(prices[-1], 2)
        }
        
        if rsi < self.oversold:
            result['signal'] = 'BUY'
            result['reason'] = f'RSI oversold: {rsi:.1f} < {self.oversold}'
            result['score'] = 70 + (self.oversold - rsi)  # Score aumenta quanto mais oversold
        
        elif rsi > self.overbought:
            result['signal'] = 'SELL'
            result['reason'] = f'RSI overbought: {rsi:.1f} > {self.overbought}'
            result['score'] = 70 + (rsi - self.overbought)
        
        else:
            result['reason'] = f'RSI neutro: {rsi:.1f}'
        
        logger.info(f"RSI: {rsi:.2f} | Sinal: {result['signal']} | Score: {result['score']:.1f}")
        
        return result


# Factory function
def create_strategy(strategy_type: str = 'sma', **kwargs) -> object:
    """
    Cria uma estratégia
    
    Args:
        strategy_type: 'sma' ou 'rsi'
        **kwargs: Parâmetros específicos da estratégia
        
    Returns:
        Instância da estratégia
    """
    if strategy_type == 'sma':
        return SimpleMovingAverageStrategy(**kwargs)
    elif strategy_type == 'rsi':
        return RSIStrategy(**kwargs)
    else:
        raise ValueError(f"Estratégia desconhecida: {strategy_type}")
