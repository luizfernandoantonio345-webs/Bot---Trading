"""
═══════════════════════════════════════════════════════════════════
CAMADA 13: ENSEMBLE DE ESTRATÉGIAS
═══════════════════════════════════════════════════════════════════
O bot usa múltiplas estratégias especializadas por regime.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import numpy as np
from core.logger import get_logger


class StrategyType(Enum):
    """Tipos de estratégias"""
    TREND_FOLLOWER = "trend_following"
    MEAN_REVERTER = "mean_reversion"
    BREAKOUT_HUNTER = "breakout"
    VOLATILITY_PLAYER = "volatility"
    COUNTER_TREND = "counter_trend"


@dataclass
class StrategyPerformance:
    """Performance de uma estratégia"""
    strategy_type: StrategyType
    win_rate: float
    expectancy: float
    sharpe_ratio: float
    max_drawdown: float
    trades: int
    last_updated: str
    active: bool


class StrategyEnsemble:
    """
    Sistema que seleciona qual estratégia usar baseado no regime de mercado.
    """
    
    def __init__(self):
        self.logger = get_logger()
        
        # Performance de cada estratégia
        self.strategy_performance = {
            StrategyType.TREND_FOLLOWER: StrategyPerformance(
                strategy_type=StrategyType.TREND_FOLLOWER,
                win_rate=0.55,
                expectancy=0.5,
                sharpe_ratio=1.2,
                max_drawdown=0.12,
                trades=0,
                last_updated="",
                active=True
            ),
            StrategyType.MEAN_REVERTER: StrategyPerformance(
                strategy_type=StrategyType.MEAN_REVERTER,
                win_rate=0.60,
                expectancy=0.3,
                sharpe_ratio=1.0,
                max_drawdown=0.15,
                trades=0,
                last_updated="",
                active=True
            ),
            StrategyType.BREAKOUT_HUNTER: StrategyPerformance(
                strategy_type=StrategyType.BREAKOUT_HUNTER,
                win_rate=0.48,
                expectancy=0.8,
                sharpe_ratio=1.3,
                max_drawdown=0.18,
                trades=0,
                last_updated="",
                active=True
            ),
            StrategyType.VOLATILITY_PLAYER: StrategyPerformance(
                strategy_type=StrategyType.VOLATILITY_PLAYER,
                win_rate=0.52,
                expectancy=0.4,
                sharpe_ratio=0.9,
                max_drawdown=0.20,
                trades=0,
                last_updated="",
                active=True
            )
        }
        
        # Mapeamento regime -> estratégia ideal
        self.regime_strategy_mapping = {
            "strong_uptrend": StrategyType.TREND_FOLLOWER,
            "strong_downtrend": StrategyType.TREND_FOLLOWER,
            "sideways": StrategyType.MEAN_REVERTER,
            "breakout_setup": StrategyType.BREAKOUT_HUNTER,
            "high_volatility": StrategyType.VOLATILITY_PLAYER,
            "low_volatility": StrategyType.MEAN_REVERTER,
            "counter_trend_setup": StrategyType.COUNTER_TREND
        }
    
    def select_strategy(self, market_analysis: Dict) -> Tuple[StrategyType, float]:
        """
        Seleciona melhor estratégia para o regime atual.
        Retorna (estratégia, confiança)
        """
        # Determinar regime
        regime = self._determine_regime(market_analysis)
        
        # Estratégia ideal para este regime
        ideal_strategy = self.regime_strategy_mapping.get(regime, StrategyType.TREND_FOLLOWER)
        
        # Se estratégia está inativa ou com performance ruim, procurar alternativa
        if not self.strategy_performance[ideal_strategy].active:
            ideal_strategy = self._find_best_active_strategy()
        
        # Calcular confiança
        perf = self.strategy_performance[ideal_strategy]
        confidence = (perf.win_rate * 0.4 + perf.sharpe_ratio / 2 * 0.3) * 100
        
        self.logger.log_system_event(
            "STRATEGY_SELECTED",
            f"Regime: {regime} -> {ideal_strategy.value} (Confiança: {confidence:.0f}%)"
        )
        
        return ideal_strategy, confidence
    
    def _determine_regime(self, market_analysis: Dict) -> str:
        """Determina regime de mercado para seleção de estratégia"""
        trend = market_analysis.get("trend", {})
        volatility = market_analysis.get("volatility", {})
        structure = market_analysis.get("structure", {})
        
        trend_dir = trend.get("consensus", {}).get("direction", "NEUTRAL")
        trend_strength = trend.get("consensus", {}).get("strength", 50)
        vol_class = volatility.get("classification", "NORMAL")
        
        # Lógica de classificação
        if trend_strength > 75:
            return "strong_uptrend" if trend_dir == "BULLISH" else "strong_downtrend"
        elif trend_strength < 25:
            if vol_class == "HIGH":
                return "breakout_setup"
            else:
                return "sideways"
        
        if vol_class == "HIGH":
            return "high_volatility"
        elif vol_class == "LOW":
            return "low_volatility"
        
        return "sideways"  # Default
    
    def _find_best_active_strategy(self) -> StrategyType:
        """Encontra estratégia ativa com melhor performance"""
        active_strategies = [
            s for s in self.strategy_performance.values()
            if s.active
        ]
        
        if not active_strategies:
            return StrategyType.TREND_FOLLOWER
        
        best = max(active_strategies, key=lambda s: s.win_rate * 0.5 + s.sharpe_ratio * 0.5)
        return best.strategy_type
    
    def deactivate_underperforming_strategy(self, strategy_type: StrategyType):
        """Desativa estratégia com performance ruim"""
        perf = self.strategy_performance[strategy_type]
        
        if perf.win_rate < 0.40 or perf.max_drawdown > 0.25:
            perf.active = False
            self.logger.log_system_event(
                "STRATEGY_DEACTIVATED",
                f"{strategy_type.value} desativada por performance ruim "
                f"(WR: {perf.win_rate:.0%}, DD: {perf.max_drawdown:.0%})"
            )
    
    def reactivate_recovered_strategy(self, strategy_type: StrategyType):
        """Reativa estratégia que melhorou"""
        perf = self.strategy_performance[strategy_type]
        
        if perf.win_rate > 0.50 and perf.max_drawdown < 0.15:
            perf.active = True
            self.logger.log_system_event(
                "STRATEGY_REACTIVATED",
                f"{strategy_type.value} reativada com performance boa "
                f"(WR: {perf.win_rate:.0%}, DD: {perf.max_drawdown:.0%})"
            )
    
    def get_strategy_report(self) -> Dict:
        """Relatório de performance de estratégias"""
        return {
            "strategies": {
                s.strategy_type.value: {
                    "active": s.active,
                    "win_rate": s.win_rate,
                    "expectancy": s.expectancy,
                    "sharpe_ratio": s.sharpe_ratio,
                    "max_drawdown": s.max_drawdown,
                    "trades": s.trades
                }
                for s in self.strategy_performance.values()
            },
            "active_count": sum(1 for s in self.strategy_performance.values() if s.active)
        }


from typing import Tuple

"""
═══════════════════════════════════════════════════════════════════
CAMADA 14: DETECÇÃO DE ANOMALIAS
═══════════════════════════════════════════════════════════════════
O bot detecta comportamentos anormais do mercado.
"""


class AnomalyDetector:
    """
    Detecção de anomalias de mercado para proteção.
    """
    
    def __init__(self):
        self.logger = get_logger()
        
        # Thresholds de anomalia
        self.spike_threshold = 3.0  # Desvios padrão
        self.volume_spike_threshold = 5.0
        self.gap_threshold = 0.02  # 2% de gap
    
    def detect_fake_breakout(self, df, current_price: float, support_resistance: Dict) -> bool:
        """
        Detecta fake breakouts (spike que volta rapidamente).
        """
        if len(df) < 10:
            return False
        
        # Verificar se há spike além de support/resistance
        recent_high = df["high"].tail(5).max()
        recent_low = df["low"].tail(5).min()
        
        resistance = support_resistance.get("resistance", [recent_high])[0]
        support = support_resistance.get("support", [recent_low])[0]
        
        # Se spike saiu mais de 1% além do nível, pode ser fake
        if recent_high > resistance * 1.01:
            # Verificar se voltou rápido
            tail_close = df["close"].tail(1).values[0]
            if tail_close < recent_high * 0.99:
                return True
        
        return False
    
    def detect_artificial_liquidity(self, df, volume_history: List[float]) -> bool:
        """
        Detecta liquidez artificial/falsa (grande volume sem movimento de preço).
        """
        if len(df) < 2:
            return False
        
        recent_volume = df["volume"].iloc[-1]
        avg_volume = np.mean(volume_history[-20:]) if len(volume_history) >= 20 else np.mean(volume_history)
        
        price_change = abs(df["close"].iloc[-1] - df["open"].iloc[-1]) / df["open"].iloc[-1]
        
        # Alto volume mas baixo movement = liquidity suspeita
        if recent_volume > avg_volume * 2 and price_change < 0.005:
            return True
        
        return False
    
    def detect_market_microstructure_issue(self, df) -> bool:
        """
        Detecta problemas de microestrutura (bid-ask issues, etc).
        """
        if len(df) < 5:
            return False
        
        # Verificar wick extremos (possível slippage)
        wick_size = []
        for i in range(-5, 0):
            h = df["high"].iloc[i]
            l = df["low"].iloc[i]
            c = df["close"].iloc[i]
            o = df["open"].iloc[i]
            
            body = abs(c - o)
            total_range = h - l
            
            if total_range > 0:
                wick_ratio = body / total_range
                wick_size.append(wick_ratio)
        
        # Se wicks muito pequenos (price pegou em um ponto e não saiu), pode ser issue
        if wick_size and np.mean(wick_size) < 0.1:
            return True
        
        return False
    
    def detect_sentiment_extreme(self, market_analysis: Dict) -> bool:
        """
        Detecta extremo de sentimento (muito otimista ou pessimista).
        """
        momentum = market_analysis.get("momentum", {})
        momentum_score = momentum.get("score", 50)
        
        # Score muito extremo (>85 ou <15) pode indicar sentimento extremo
        if momentum_score > 85 or momentum_score < 15:
            return True
        
        return False
    
    def get_anomaly_report(self, df, market_analysis: Dict, support_resistance: Dict) -> Dict:
        """Relatório completo de anomalias"""
        current_price = df["close"].iloc[-1]
        volume_history = df["volume"].tail(50).tolist()
        
        anomalies = []
        
        if self.detect_fake_breakout(df, current_price, support_resistance):
            anomalies.append("FAKE_BREAKOUT")
        
        if self.detect_artificial_liquidity(df, volume_history):
            anomalies.append("ARTIFICIAL_LIQUIDITY")
        
        if self.detect_market_microstructure_issue(df):
            anomalies.append("MICROSTRUCTURE_ISSUE")
        
        if self.detect_sentiment_extreme(market_analysis):
            anomalies.append("SENTIMENT_EXTREME")
        
        return {
            "detected_anomalies": anomalies,
            "is_clean_market": len(anomalies) == 0,
            "anomaly_count": len(anomalies)
        }


"""
═══════════════════════════════════════════════════════════════════
CAMADA 15: CONTROLE TEMPORAL AVANÇADO
═══════════════════════════════════════════════════════════════════
O bot sabe quando NÃO operar.
"""


from datetime import datetime, time


class TemporalController:
    """
    Controle avançado baseado em análise temporal.
    """
    
    def __init__(self, memory_engine=None):
        self.logger = get_logger()
        self.memory = memory_engine
        
        # Horários com melhor performance histórica
        self.best_hours = {
            "LONDON": [9, 10, 11, 12],  # Early London
            "NY": [14, 15, 16],  # Early NY
            "ASIA": [1, 2, 3]  # Early Asia
        }
        
        # Horários piores
        self.worst_hours = {
            "LONDON": [7, 8],  # Pré-abertura
            "NY": [23, 0],  # Pós-fechamento
            "ASIA": [4, 5, 6]  # Fim da sessão
        }
    
    def is_optimal_trading_time(self, current_hour: int, session: str) -> bool:
        """Verifica se é hora ótima para operar"""
        if session not in self.best_hours:
            return True  # Default se desconhecido
        
        return current_hour in self.best_hours[session]
    
    def is_forbidden_time(self, current_hour: int, session: str) -> bool:
        """Verifica se é hora proibida para operar"""
        if session not in self.worst_hours:
            return False
        
        return current_hour in self.worst_hours[session]
    
    def get_time_quality_score(self, current_hour: int, session: str) -> float:
        """
        Score de qualidade do tempo (0-100).
        """
        if self.is_forbidden_time(current_hour, session):
            return 20.0
        elif self.is_optimal_trading_time(current_hour, session):
            return 90.0
        else:
            return 60.0  # Neutro
    
    def adjust_stops_by_time(self, entry_price: float, volatility: float, trade_duration_hours: int) -> float:
        """
        Ajusta stop loss baseado no tempo esperado da operação.
        Operações mais longas precisam de stops mais amplos.
        """
        base_stop = volatility * 2
        
        # Multiplier por duração esperada
        duration_multiplier = 1.0 + (trade_duration_hours / 24) * 0.5
        
        return entry_price - (base_stop * duration_multiplier)
    
    def adjust_targets_by_time(self, entry_price: float, volatility: float, trade_duration_hours: int) -> float:
        """
        Ajusta take profit baseado no tempo esperado.
        """
        base_target = volatility * 3
        
        # Multiplier por duração (trades mais curtos podem ter targets maiores)
        duration_multiplier = 2.0 - (trade_duration_hours / 24)
        
        return entry_price + (base_target * duration_multiplier)
    
    def get_temporal_report(self, current_session: str) -> Dict:
        """Relatório temporal"""
        now = datetime.now()
        hour = now.hour
        
        return {
            "current_hour": hour,
            "current_session": current_session,
            "is_optimal": self.is_optimal_trading_time(hour, current_session),
            "is_forbidden": self.is_forbidden_time(hour, current_session),
            "time_quality_score": self.get_time_quality_score(hour, current_session),
            "recommendation": "DO_NOT_TRADE" if self.is_forbidden_time(hour, current_session) else "OK_TO_TRADE"
        }
