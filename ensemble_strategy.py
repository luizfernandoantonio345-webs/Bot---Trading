"""
Ensemble Trading System
Combina múltiplas estratégias, indicadores e padrões
para gerar sinais com alta confiança
"""
import numpy as np
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

from advanced_indicators import IndicatorAnalyzer
from pattern_recognition import PatternRecognitionEngine
from trading_strategy import SimpleMovingAverageStrategy, RSIStrategy

logger = logging.getLogger(__name__)


@dataclass
class MarketRegime:
    """Regime de mercado detectado"""
    regime: str  # 'trending', 'ranging', 'volatile', 'quiet'
    strength: float  # 0-100
    direction: str  # 'bullish', 'bearish', 'neutral'


class RegimeDetector:
    """
    Detecta regime de mercado atual
    """
    
    def detect(self, prices: np.ndarray, window: int = 50) -> MarketRegime:
        """
        Detecta regime de mercado
        
        Returns:
            MarketRegime object
        """
        if len(prices) < window:
            return MarketRegime('unknown', 0, 'neutral')
        
        recent_prices = prices[-window:]
        
        # Calcular métricas
        returns = np.diff(recent_prices) / recent_prices[:-1]
        volatility = np.std(returns)
        trend_strength = abs(np.corrcoef(np.arange(len(recent_prices)), recent_prices)[0, 1])
        
        # Detectar regime
        if volatility > 0.03:  # High volatility
            regime = 'volatile'
            strength = min(volatility * 100, 100)
        elif volatility < 0.01:  # Low volatility
            regime = 'quiet'
            strength = (1 - volatility * 100)
        elif trend_strength > 0.7:  # Strong trend
            regime = 'trending'
            strength = trend_strength * 100
        else:  # Range-bound
            regime = 'ranging'
            strength = (1 - trend_strength) * 100
        
        # Detectar direção
        if np.mean(returns) > 0.001:
            direction = 'bullish'
        elif np.mean(returns) < -0.001:
            direction = 'bearish'
        else:
            direction = 'neutral'
        
        logger.info(f"Market regime: {regime} ({strength:.1f}%), direction: {direction}")
        
        return MarketRegime(regime, strength, direction)


class EnsembleStrategy:
    """
    Sistema Ensemble que combina múltiplas estratégias
    """
    
    def __init__(self):
        # Componentes
        self.indicator_analyzer = IndicatorAnalyzer()
        self.pattern_engine = PatternRecognitionEngine()
        self.regime_detector = RegimeDetector()
        
        # Estratégias tradicionais
        self.sma_strategy = SimpleMovingAverageStrategy(fast_period=9, slow_period=21)
        self.rsi_strategy = RSIStrategy(period=14)
        
        # Pesos para ensemble (total = 1.0)
        self.weights = {
            'indicators': 0.25,
            'candlestick_patterns': 0.15,
            'chart_patterns': 0.15,
            'sma_strategy': 0.15,
            'rsi_strategy': 0.10,
            'regime_adaptation': 0.10,
            'volume_confirmation': 0.10
        }
    
    def analyze(self, market_data: Dict[str, np.ndarray]) -> Dict[str, any]:
        """
        Análise completa usando ensemble
        
        Args:
            market_data: Dict com 'open', 'high', 'low', 'close', 'volume'
        
        Returns:
            Dict com análise completa e sinal final
        """
        results = {
            'components': {},
            'regime': None,
            'final_signal': 'NEUTRAL',
            'final_score': 0,
            'confidence': 0,
            'recommendations': []
        }
        
        try:
            close = market_data['close']
            
            # 1. Detectar regime de mercado
            regime = self.regime_detector.detect(close)
            results['regime'] = {
                'type': regime.regime,
                'strength': regime.strength,
                'direction': regime.direction
            }
            
            # 2. Análise de indicadores técnicos
            indicators = self.indicator_analyzer.analyze_all(market_data)
            indicator_signals = self.indicator_analyzer.generate_signals(indicators)
            results['components']['indicators'] = indicator_signals
            
            # 3. Padrões de candlestick
            candlestick_patterns = self.pattern_engine.analyze_candlestick_patterns(market_data)
            candlestick_score = self.pattern_engine.get_pattern_score(candlestick_patterns)
            results['components']['candlestick_patterns'] = {
                'patterns': candlestick_patterns,
                'score': candlestick_score
            }
            
            # 4. Padrões de gráfico
            chart_patterns = self.pattern_engine.analyze_chart_patterns(close)
            chart_score = self.pattern_engine.get_pattern_score(chart_patterns)
            results['components']['chart_patterns'] = {
                'patterns': chart_patterns,
                'score': chart_score
            }
            
            # 5. Estratégia SMA
            sma_analysis = self.sma_strategy.analyze(close.tolist())
            results['components']['sma_strategy'] = sma_analysis
            
            # 6. Estratégia RSI
            rsi_analysis = self.rsi_strategy.analyze(close.tolist())
            results['components']['rsi_strategy'] = rsi_analysis
            
            # 7. Calcular score ensemble
            final_score, final_signal = self._calculate_ensemble_score(results, regime)
            
            results['final_score'] = final_score
            results['final_signal'] = final_signal
            results['confidence'] = self._calculate_confidence(results)
            
            # 8. Gerar recomendações
            results['recommendations'] = self._generate_recommendations(results, regime)
            
            logger.info(
                f"Ensemble Analysis: {final_signal} | "
                f"Score: {final_score:.1f} | "
                f"Confidence: {results['confidence']:.1f}% | "
                f"Regime: {regime.regime}"
            )
            
        except Exception as e:
            logger.error(f"Erro na análise ensemble: {e}")
            results['error'] = str(e)
        
        return results
    
    def _calculate_ensemble_score(self, results: Dict, regime: MarketRegime) -> tuple[float, str]:
        """
        Calcula score final usando votação ponderada
        
        Returns:
            (score, signal)
        """
        scores = {
            'BUY': 0,
            'SELL': 0,
            'NEUTRAL': 0
        }
        
        # 1. Indicadores técnicos
        ind_signal = results['components']['indicators'].get('signal', 'NEUTRAL')
        ind_conf = results['components']['indicators'].get('confidence', 0) / 100
        scores[ind_signal] += self.weights['indicators'] * ind_conf
        
        # 2. Padrões de candlestick
        cand_signal = results['components']['candlestick_patterns']['score'].get('signal', 'NEUTRAL')
        cand_conf = results['components']['candlestick_patterns']['score'].get('confidence', 0) / 100
        scores[cand_signal] += self.weights['candlestick_patterns'] * cand_conf
        
        # 3. Padrões de gráfico
        chart_signal = results['components']['chart_patterns']['score'].get('signal', 'NEUTRAL')
        chart_conf = results['components']['chart_patterns']['score'].get('confidence', 0) / 100
        scores[chart_signal] += self.weights['chart_patterns'] * chart_conf
        
        # 4. Estratégia SMA
        sma_signal = results['components']['sma_strategy'].get('signal', 'WAIT')
        if sma_signal != 'WAIT':
            sma_score = results['components']['sma_strategy'].get('score', 0) / 100
            scores[sma_signal] += self.weights['sma_strategy'] * sma_score
        
        # 5. Estratégia RSI
        rsi_signal = results['components']['rsi_strategy'].get('signal', 'WAIT')
        if rsi_signal != 'WAIT':
            rsi_score = results['components']['rsi_strategy'].get('score', 0) / 100
            scores[rsi_signal] += self.weights['rsi_strategy'] * rsi_score
        
        # 6. Ajuste por regime de mercado
        regime_multiplier = self._get_regime_multiplier(regime)
        
        # Aplicar multiplicador do regime
        if regime.direction == 'bullish':
            scores['BUY'] *= regime_multiplier
        elif regime.direction == 'bearish':
            scores['SELL'] *= regime_multiplier
        
        # Determinar sinal final
        max_signal = max(scores, key=scores.get)
        max_score = scores[max_signal]
        
        # Converter para score 0-100
        final_score = max_score * 100
        
        # Apenas retornar sinal se confiança suficiente
        if final_score < 50:
            return final_score, 'NEUTRAL'
        
        return final_score, max_signal
    
    def _get_regime_multiplier(self, regime: MarketRegime) -> float:
        """
        Ajusta pesos baseado no regime de mercado
        """
        if regime.regime == 'trending':
            return 1.2  # Favorecer trend following
        elif regime.regime == 'ranging':
            return 0.8  # Reduzir agressividade
        elif regime.regime == 'volatile':
            return 0.7  # Ser mais conservador
        elif regime.regime == 'quiet':
            return 1.0  # Normal
        else:
            return 1.0
    
    def _calculate_confidence(self, results: Dict) -> float:
        """
        Calcula nível de confiança geral (0-100)
        """
        confidence_scores = []
        
        # Confiança dos indicadores
        if 'indicators' in results['components']:
            conf = results['components']['indicators'].get('confidence', 0)
            confidence_scores.append(conf)
        
        # Confiança dos padrões
        if 'candlestick_patterns' in results['components']:
            conf = results['components']['candlestick_patterns']['score'].get('confidence', 0)
            confidence_scores.append(conf)
        
        if 'chart_patterns' in results['components']:
            conf = results['components']['chart_patterns']['score'].get('confidence', 0)
            confidence_scores.append(conf)
        
        # Confiança das estratégias
        if 'sma_strategy' in results['components']:
            score = results['components']['sma_strategy'].get('score', 0)
            confidence_scores.append(score)
        
        if 'rsi_strategy' in results['components']:
            score = results['components']['rsi_strategy'].get('score', 0)
            confidence_scores.append(score)
        
        if confidence_scores:
            return np.mean(confidence_scores)
        
        return 0
    
    def _generate_recommendations(self, results: Dict, regime: MarketRegime) -> List[str]:
        """
        Gera recomendações baseadas na análise
        """
        recommendations = []
        
        final_signal = results['final_signal']
        final_score = results['final_score']
        confidence = results['confidence']
        
        # Recomendação principal
        if final_signal == 'BUY':
            if confidence > 75:
                recommendations.append(f"✅ STRONG BUY - Score: {final_score:.1f}, Confidence: {confidence:.1f}%")
            elif confidence > 60:
                recommendations.append(f"✅ BUY - Score: {final_score:.1f}, Confidence: {confidence:.1f}%")
            else:
                recommendations.append(f"⚠️ WEAK BUY - Score: {final_score:.1f}, Confidence: {confidence:.1f}%")
        
        elif final_signal == 'SELL':
            if confidence > 75:
                recommendations.append(f"❌ STRONG SELL - Score: {final_score:.1f}, Confidence: {confidence:.1f}%")
            elif confidence > 60:
                recommendations.append(f"❌ SELL - Score: {final_score:.1f}, Confidence: {confidence:.1f}%")
            else:
                recommendations.append(f"⚠️ WEAK SELL - Score: {final_score:.1f}, Confidence: {confidence:.1f}%")
        
        else:
            recommendations.append(f"⏸️ NEUTRAL - Wait for better setup")
        
        # Recomendações baseadas no regime
        if regime.regime == 'volatile':
            recommendations.append("⚠️ High volatility detected - Consider smaller position sizes")
        elif regime.regime == 'ranging':
            recommendations.append("📊 Range-bound market - Consider mean reversion strategies")
        elif regime.regime == 'trending':
            recommendations.append("📈 Strong trend detected - Trend following recommended")
        
        # Alertas de padrões importantes
        candlestick_patterns = results['components']['candlestick_patterns']['patterns']
        for pattern in candlestick_patterns:
            if pattern.get('confidence', 0) > 80:
                recommendations.append(f"🔔 Strong pattern: {pattern['pattern']} ({pattern['signal']})")
        
        chart_patterns = results['components']['chart_patterns']['patterns']
        for pattern in chart_patterns:
            if pattern.get('signal') and pattern['signal'] != 'NEUTRAL':
                recommendations.append(f"📊 Chart pattern: {pattern['pattern']} ({pattern['signal']})")
        
        # Recomendações de gestão de risco
        if confidence < 60:
            recommendations.append("⚠️ Low confidence - Use tight stop loss")
        
        if final_score > 80:
            recommendations.append("💪 Strong signal - Consider scaling into position")
        
        return recommendations
    
    def should_execute_trade(self, analysis: Dict, min_confidence: float = 70) -> bool:
        """
        Decide se deve executar trade baseado na análise
        
        Args:
            analysis: Resultado da análise ensemble
            min_confidence: Confiança mínima requerida (0-100)
        
        Returns:
            True se deve executar
        """
        if analysis['final_signal'] == 'NEUTRAL':
            return False
        
        if analysis['confidence'] < min_confidence:
            logger.info(
                f"Trade não executado: Confiança {analysis['confidence']:.1f}% "
                f"< mínimo {min_confidence}%"
            )
            return False
        
        if analysis['final_score'] < 60:
            logger.info(
                f"Trade não executado: Score {analysis['final_score']:.1f} muito baixo"
            )
            return False
        
        return True
    
    def get_position_size_multiplier(self, analysis: Dict) -> float:
        """
        Retorna multiplicador para tamanho de posição baseado na confiança
        
        Returns:
            Multiplicador (0.5 - 1.5)
        """
        confidence = analysis['confidence']
        
        if confidence > 85:
            return 1.5  # Aumentar posição em sinais muito fortes
        elif confidence > 75:
            return 1.2
        elif confidence > 65:
            return 1.0  # Tamanho normal
        elif confidence > 55:
            return 0.8
        else:
            return 0.5  # Reduzir posição em sinais fracos


# Factory function
def create_ensemble_strategy() -> EnsembleStrategy:
    """
    Cria instância do ensemble strategy
    """
    return EnsembleStrategy()
