"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI ENGINE #1: SCORE ENGINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESPONSIBILITY:
Evaluate opportunity QUALITY (not profitability).
Assess technical setup strength.

CAN VETO IF:
- Score below minimum threshold
- Setup quality insufficient
- Conflicting signals detected

CANNOT:
- Promise profit
- Force trades
- Ignore other engines
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class ScoreResult:
    """Score evaluation result"""
    score: float  # 0-100
    quality: str  # ELITE, HIGH, MODERATE, LOW, POOR
    components: Dict[str, float]
    veto: bool
    veto_reason: str
    confidence: float


class ScoreEngine:
    """
    Evaluates opportunity quality based on technical setup.
    
    PRINCIPLES:
    - High score = High quality setup (NOT profit guarantee)
    - Evaluates confluence of factors
    - Conservative by default
    - Quality over quantity
    """
    
    # Thresholds
    MIN_SCORE_RECOMMEND = 65.0
    MIN_SCORE_HIGH_QUALITY = 80.0
    MIN_SCORE_ELITE = 90.0
    
    def __init__(self):
        self.name = "ScoreEngine"
        self.version = "1.0.0"
    
    def evaluate(
        self,
        trend_alignment: float,
        momentum_strength: float,
        volatility_context: str,
        volume_confirmation: float,
        support_resistance_proximity: float,
        session_timing: str
    ) -> ScoreResult:
        """
        Evaluate opportunity quality.
        
        Returns ScoreResult with veto if quality insufficient.
        """
        
        components = {}
        
        # 1. Trend Alignment (0-30 points)
        components['trend'] = self._score_trend(trend_alignment)
        
        # 2. Momentum Strength (0-25 points)
        components['momentum'] = self._score_momentum(momentum_strength)
        
        # 3. Volatility Context (0-15 points)
        components['volatility'] = self._score_volatility(volatility_context)
        
        # 4. Volume Confirmation (0-15 points)
        components['volume'] = self._score_volume(volume_confirmation)
        
        # 5. Support/Resistance (0-10 points)
        components['structure'] = self._score_structure(support_resistance_proximity)
        
        # 6. Session Timing (0-5 points)
        components['timing'] = self._score_timing(session_timing)
        
        # Total score
        total_score = sum(components.values())
        
        # Confidence based on component agreement
        confidence = self._calculate_confidence(components)
        
        # Quality classification
        if total_score >= self.MIN_SCORE_ELITE:
            quality = "ELITE"
        elif total_score >= self.MIN_SCORE_HIGH_QUALITY:
            quality = "HIGH"
        elif total_score >= self.MIN_SCORE_RECOMMEND:
            quality = "MODERATE"
        elif total_score >= 50:
            quality = "LOW"
        else:
            quality = "POOR"
        
        # Veto decision
        veto = False
        veto_reason = ""
        
        if total_score < self.MIN_SCORE_RECOMMEND:
            veto = True
            veto_reason = f"Score below minimum ({total_score:.1f} < {self.MIN_SCORE_RECOMMEND})"
        elif confidence < 0.6:
            veto = True
            veto_reason = f"Low confidence in setup ({confidence:.2f})"
        
        return ScoreResult(
            score=total_score,
            quality=quality,
            components=components,
            veto=veto,
            veto_reason=veto_reason,
            confidence=confidence
        )
    
    def _score_trend(self, alignment: float) -> float:
        """Score trend alignment (0-30)"""
        # alignment: -1.0 (strong down) to +1.0 (strong up)
        abs_alignment = abs(alignment)
        
        if abs_alignment >= 0.8:
            return 30.0
        elif abs_alignment >= 0.6:
            return 22.0
        elif abs_alignment >= 0.4:
            return 15.0
        elif abs_alignment >= 0.2:
            return 8.0
        else:
            return 0.0
    
    def _score_momentum(self, strength: float) -> float:
        """Score momentum strength (0-25)"""
        # strength: 0.0 (weak) to 1.0 (strong)
        if strength >= 0.8:
            return 25.0
        elif strength >= 0.6:
            return 18.0
        elif strength >= 0.4:
            return 12.0
        elif strength >= 0.2:
            return 6.0
        else:
            return 0.0
    
    def _score_volatility(self, context: str) -> float:
        """Score volatility context (0-15)"""
        volatility_scores = {
            'OPTIMAL': 15.0,      # Ideal volatility
            'MODERATE': 12.0,     # Acceptable
            'LOW': 8.0,           # Less opportunity
            'HIGH': 5.0,          # Higher risk
            'EXTREME': 0.0        # Too dangerous
        }
        return volatility_scores.get(context, 5.0)
    
    def _score_volume(self, confirmation: float) -> float:
        """Score volume confirmation (0-15)"""
        # confirmation: 0.0 (weak) to 1.0 (strong)
        if confirmation >= 0.8:
            return 15.0
        elif confirmation >= 0.6:
            return 11.0
        elif confirmation >= 0.4:
            return 7.0
        elif confirmation >= 0.2:
            return 3.0
        else:
            return 0.0
    
    def _score_structure(self, proximity: float) -> float:
        """Score support/resistance structure (0-10)"""
        # proximity: 0.0 (at level) to 1.0 (far from level)
        # Prefer entries near support/resistance
        if proximity <= 0.1:
            return 10.0
        elif proximity <= 0.2:
            return 7.0
        elif proximity <= 0.3:
            return 5.0
        elif proximity <= 0.5:
            return 3.0
        else:
            return 0.0
    
    def _score_timing(self, session: str) -> float:
        """Score session timing (0-5)"""
        session_scores = {
            'LONDON': 5.0,
            'NY': 5.0,
            'LONDON_NY_OVERLAP': 5.0,
            'ASIA': 3.0,
            'OFF_HOURS': 0.0
        }
        return session_scores.get(session, 2.0)
    
    def _calculate_confidence(self, components: Dict[str, float]) -> float:
        """
        Calculate confidence based on component agreement.
        High confidence when all components agree.
        """
        # Normalize components to 0-1
        normalized = []
        max_values = {
            'trend': 30.0,
            'momentum': 25.0,
            'volatility': 15.0,
            'volume': 15.0,
            'structure': 10.0,
            'timing': 5.0
        }
        
        for key, value in components.items():
            max_val = max_values.get(key, 1.0)
            normalized.append(value / max_val if max_val > 0 else 0)
        
        # Confidence = how similar the components are
        # Low variance = high confidence
        if len(normalized) > 0:
            mean = np.mean(normalized)
            variance = np.var(normalized)
            confidence = 1.0 - min(variance * 2, 0.5)  # Cap reduction at 0.5
            return confidence
        
        return 0.5
    
    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            'name': self.name,
            'version': self.version,
            'min_score_recommend': self.MIN_SCORE_RECOMMEND,
            'min_score_elite': self.MIN_SCORE_ELITE,
            'active': True
        }
