"""
═══════════════════════════════════════════════════════════════════
CAMADA 11: MODELO DE ATENÇÃO CONTEXTUAL
═══════════════════════════════════════════════════════════════════
O bot aprende o que REALMENTE importa em cada momento.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import numpy as np
from core.logger import get_logger


class AttentionFocus(Enum):
    """Focos de atenção do bot"""
    TREND_FOLLOWING = "trend"
    MEAN_REVERSION = "reversion"
    BREAKOUT = "breakout"
    VOLATILITY_PLAY = "volatility"
    COUNTER_TREND = "counter_trend"


@dataclass
class AttentionWeights:
    """Pesos de atenção para diferentes sinais"""
    trend_alignment: float  # 0-1
    momentum_strength: float
    support_resistance: float
    volatility_regime: float
    session_quality: float
    liquidity: float
    volume_confirmation: float


class ContextualAttentionModel:
    """
    Modelo dinâmico de atenção que adapta o foco conforme o contexto.
    
    Princípio: Dar mais peso ao que REALMENTE importa agora.
    """
    
    def __init__(self):
        self.logger = get_logger()
        
        # Pesos base por regime
        self.attention_profiles = {
            "strong_trend": {
                "trend_alignment": 0.40,
                "momentum_strength": 0.25,
                "support_resistance": 0.15,
                "volatility_regime": 0.10,
                "session_quality": 0.05,
                "liquidity": 0.03,
                "volume_confirmation": 0.02
            },
            "sideways": {
                "trend_alignment": 0.15,
                "momentum_strength": 0.10,
                "support_resistance": 0.35,
                "volatility_regime": 0.15,
                "session_quality": 0.10,
                "liquidity": 0.10,
                "volume_confirmation": 0.05
            },
            "high_volatility": {
                "trend_alignment": 0.20,
                "momentum_strength": 0.15,
                "support_resistance": 0.20,
                "volatility_regime": 0.30,
                "session_quality": 0.05,
                "liquidity": 0.08,
                "volume_confirmation": 0.02
            },
            "low_volatility": {
                "trend_alignment": 0.30,
                "momentum_strength": 0.20,
                "support_resistance": 0.25,
                "volatility_regime": 0.05,
                "session_quality": 0.10,
                "liquidity": 0.07,
                "volume_confirmation": 0.03
            },
            "calm_session": {
                "trend_alignment": 0.25,
                "momentum_strength": 0.20,
                "support_resistance": 0.20,
                "volatility_regime": 0.10,
                "session_quality": 0.15,
                "liquidity": 0.07,
                "volume_confirmation": 0.03
            },
            "volatile_session": {
                "trend_alignment": 0.15,
                "momentum_strength": 0.25,
                "support_resistance": 0.15,
                "volatility_regime": 0.25,
                "session_quality": 0.05,
                "liquidity": 0.10,
                "volume_confirmation": 0.05
            }
        }
        
        # Foco atual
        self.current_focus = AttentionFocus.TREND_FOLLOWING
        self.current_weights = AttentionWeights(**self.attention_profiles["strong_trend"])
    
    def determine_market_regime(self, market_analysis: Dict) -> str:
        """
        Determina o regime de mercado para ajustar atenção.
        """
        volatility = market_analysis.get("volatility", {})
        trend = market_analysis.get("trend", {})
        
        vol_class = volatility.get("classification", "NORMAL")
        trend_strength = trend.get("consensus", {}).get("strength", 50)
        
        # Lógica de classificação
        if trend_strength > 70:
            if vol_class == "HIGH":
                return "strong_trend"  # Tendência forte com volatilidade
            else:
                return "strong_trend"
        
        elif trend_strength < 30:
            return "sideways"
        
        if vol_class == "HIGH":
            return "high_volatility"
        elif vol_class == "LOW":
            return "low_volatility"
        
        return "strong_trend"  # Default
    
    def determine_session_regime(self, market_analysis: Dict) -> str:
        """
        Determina regime da sessão de mercado.
        """
        session = market_analysis.get("session", {})
        volatility = market_analysis.get("volatility", {})
        
        vol_class = volatility.get("classification", "NORMAL")
        
        # Sessões de NY e Londres tendem a ser mais voláteis
        current_session = session.get("current", "OFF")
        
        if current_session in ["LONDON", "NY"] and vol_class == "HIGH":
            return "volatile_session"
        elif current_session == "ASIA" or vol_class == "LOW":
            return "calm_session"
        
        return "calm_session"  # Default
    
    def compute_attention_weights(self, market_analysis: Dict) -> AttentionWeights:
        """
        Computa pesos de atenção adaptados ao contexto atual.
        """
        # Determinar regime
        market_regime = self.determine_market_regime(market_analysis)
        session_regime = self.determine_session_regime(market_analysis)
        
        # Selecionar perfil
        if market_regime in self.attention_profiles:
            base_profile = self.attention_profiles[market_regime]
        else:
            base_profile = self.attention_profiles["strong_trend"]
        
        # Ajustar por sessão
        session_adjustment = self._get_session_adjustment(session_regime)
        
        # Mesclar
        weights_dict = {}
        for key, value in base_profile.items():
            adjustment = session_adjustment.get(key, 1.0)
            weights_dict[key] = value * adjustment
        
        # Normalizar
        total = sum(weights_dict.values())
        weights_dict = {k: v/total for k, v in weights_dict.items()}
        
        self.current_weights = AttentionWeights(**weights_dict)
        
        return self.current_weights
    
    def _get_session_adjustment(self, session_regime: str) -> Dict:
        """Ajustes por tipo de sessão"""
        adjustments = {
            "calm_session": {
                "trend_alignment": 1.10,
                "session_quality": 1.30,
                "volatility_regime": 0.80
            },
            "volatile_session": {
                "volatility_regime": 1.40,
                "session_quality": 0.70,
                "trend_alignment": 0.90
            }
        }
        
        default_adj = {key: 1.0 for key in [
            "trend_alignment", "momentum_strength", "support_resistance",
            "volatility_regime", "session_quality", "liquidity", "volume_confirmation"
        ]}
        
        return adjustments.get(session_regime, default_adj)
    
    def prioritize_signals(self, available_signals: Dict) -> List[tuple]:
        """
        Prioriza sinais baseado em atenção atual.
        
        Retorna: [(sinal, prioridade), ...]
        """
        signal_scores = []
        
        # Score cada sinal baseado no peso de atenção
        if "trend_signal" in available_signals:
            score = available_signals["trend_signal"] * self.current_weights.trend_alignment
            signal_scores.append(("trend", score))
        
        if "momentum_signal" in available_signals:
            score = available_signals["momentum_signal"] * self.current_weights.momentum_strength
            signal_scores.append(("momentum", score))
        
        if "support_resistance" in available_signals:
            score = available_signals["support_resistance"] * self.current_weights.support_resistance
            signal_scores.append(("support_resistance", score))
        
        if "volatility_signal" in available_signals:
            score = available_signals["volatility_signal"] * self.current_weights.volatility_regime
            signal_scores.append(("volatility", score))
        
        if "volume_signal" in available_signals:
            score = available_signals["volume_signal"] * self.current_weights.volume_confirmation
            signal_scores.append(("volume", score))
        
        # Ordenar por prioridade
        signal_scores.sort(key=lambda x: x[1], reverse=True)
        
        return signal_scores
    
    def reduce_noise(self, indicators: Dict) -> Dict:
        """
        Filtra indicadores que são menos relevantes no momento.
        """
        # Indicadores com baixo peso de atenção são reduzidos
        filtered = {}
        
        for key, value in indicators.items():
            if key == "trend_alignment" and self.current_weights.trend_alignment < 0.20:
                filtered[key] = value * 0.5  # Reduzir influência
            elif key == "momentum" and self.current_weights.momentum_strength < 0.15:
                filtered[key] = value * 0.5
            elif key == "support_resistance" and self.current_weights.support_resistance < 0.20:
                filtered[key] = value * 0.5
            else:
                filtered[key] = value
        
        return filtered
    
    def adapt_focus_for_trade(self, market_analysis: Dict, pattern_type: str) -> AttentionFocus:
        """
        Adapta foco de atenção para o padrão detectado.
        """
        volatility = market_analysis.get("volatility", {})
        vol_class = volatility.get("classification", "NORMAL")
        
        # Lógica de seleção de foco
        if "breakout" in pattern_type.lower():
            self.current_focus = AttentionFocus.BREAKOUT
        elif "reversal" in pattern_type.lower():
            self.current_focus = AttentionFocus.MEAN_REVERSION
        elif vol_class == "HIGH":
            self.current_focus = AttentionFocus.VOLATILITY_PLAY
        else:
            self.current_focus = AttentionFocus.TREND_FOLLOWING
        
        self.logger.log_system_event(
            "ATTENTION_FOCUS_CHANGED",
            f"Foco ajustado para: {self.current_focus.value}"
        )
        
        return self.current_focus
    
    def get_attention_report(self) -> Dict:
        """Retorna relatório de atenção atual"""
        return {
            "current_focus": self.current_focus.value,
            "weights": {
                "trend_alignment": self.current_weights.trend_alignment,
                "momentum_strength": self.current_weights.momentum_strength,
                "support_resistance": self.current_weights.support_resistance,
                "volatility_regime": self.current_weights.volatility_regime,
                "session_quality": self.current_weights.session_quality,
                "liquidity": self.current_weights.liquidity,
                "volume_confirmation": self.current_weights.volume_confirmation
            },
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
