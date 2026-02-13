"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI ENGINE #7: REGIME SHIFT DETECTOR
AI ENGINE #8: CONFIDENCE DECAY ENGINE
AI ENGINE #9: SESSION MEMORY ENGINE
AI ENGINE #10: CONTRAFACTUAL ANALYZER
AI ENGINE #11: CAPITAL PRESERVATION ADVISOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Remaining specialized AI engines for institutional system.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque


# ═══════════════════════════════════════════════════════
# ENGINE #7: REGIME SHIFT DETECTOR
# ═══════════════════════════════════════════════════════

@dataclass
class RegimeAnalysis:
    """Regime shift analysis result"""
    regime_stable: bool
    shift_detected: bool
    shift_magnitude: float
    veto: bool
    veto_reason: str
    current_regime: str
    regime_duration: int


class RegimeShiftDetector:
    """
    Detects sudden market regime changes.
    
    PRINCIPLES:
    - Pause trading during regime transitions
    - Regime shifts = increased uncertainty
    - Wait for regime to stabilize
    """
    
    MIN_REGIME_STABILITY_PERIODS = 5  # Need 5 periods of stable regime
    
    def __init__(self):
        self.name = "RegimeShiftDetector"
        self.regime_history = deque(maxlen=20)
    
    def analyze(self, df_h1: pd.DataFrame, current_regime: str) -> Dict:
        """Analyze for regime shifts"""
        
        # Record current regime
        self.regime_history.append({
            'timestamp': datetime.now(),
            'regime': current_regime
        })
        
        # Check regime stability
        if len(self.regime_history) < self.MIN_REGIME_STABILITY_PERIODS:
            return {
                'regime_stable': False,
                'shift_detected': False,
                'veto': True,
                'veto_reason': "Insufficient regime history - warming up",
                'current_regime': current_regime,
                'regime_duration': len(self.regime_history)
            }
        
        # Check if regime changed recently
        recent_regimes = [r['regime'] for r in list(self.regime_history)[-self.MIN_REGIME_STABILITY_PERIODS:]]
        regime_changes = sum(1 for i in range(len(recent_regimes)-1) if recent_regimes[i] != recent_regimes[i+1])
        
        if regime_changes > 0:
            return {
                'regime_stable': False,
                'shift_detected': True,
                'veto': True,
                'veto_reason': f"Regime shift detected - {regime_changes} changes in last {self.MIN_REGIME_STABILITY_PERIODS} periods",
                'current_regime': current_regime,
                'regime_duration': 0
            }
        
        # Regime stable
        return {
            'regime_stable': True,
            'shift_detected': False,
            'veto': False,
            'veto_reason': "",
            'current_regime': current_regime,
            'regime_duration': len(self.regime_history)
        }
    
    def get_status(self) -> dict:
        """Get engine status"""
        return {
            'name': self.name,
            'active': True,
            'regime_history_length': len(self.regime_history)
        }


# ═══════════════════════════════════════════════════════
# ENGINE #8: CONFIDENCE DECAY ENGINE
# ═══════════════════════════════════════════════════════

class ConfidenceDecayEngine:
    """
    Models confidence decay over time.
    
    PRINCIPLES:
    - Confidence degrades as time passes
    - Old signals less reliable
    - Refresh analysis regularly
    """
    
    MAX_SIGNAL_AGE_MINUTES = 15  # Signal stale after 15min
    
    def __init__(self):
        self.name = "ConfidenceDecayEngine"
        self.signal_timestamp = None
        self.initial_confidence = 0.0
    
    def set_signal(self, confidence: float):
        """Record new signal with timestamp"""
        self.signal_timestamp = datetime.now()
        self.initial_confidence = confidence
    
    def get_current_confidence(self) -> Dict:
        """Calculate current confidence with decay"""
        
        if self.signal_timestamp is None:
            return {
                'confidence': 0.0,
                'veto': True,
                'veto_reason': "No active signal",
                'age_minutes': 0
            }
        
        age = (datetime.now() - self.signal_timestamp).total_seconds() / 60
        
        # Exponential decay
        decay_factor = np.exp(-age / self.MAX_SIGNAL_AGE_MINUTES)
        current_confidence = self.initial_confidence * decay_factor
        
        if age > self.MAX_SIGNAL_AGE_MINUTES:
            return {
                'confidence': current_confidence,
                'veto': True,
                'veto_reason': f"Signal too old ({age:.1f} minutes)",
                'age_minutes': age
            }
        
        if current_confidence < 0.5:
            return {
                'confidence': current_confidence,
                'veto': True,
                'veto_reason': f"Confidence decayed below threshold ({current_confidence:.2f})",
                'age_minutes': age
            }
        
        return {
            'confidence': current_confidence,
            'veto': False,
            'veto_reason': "",
            'age_minutes': age
        }
    
    def get_status(self) -> dict:
        """Get engine status"""
        return {
            'name': self.name,
            'active': True,
            'signal_age_max_minutes': self.MAX_SIGNAL_AGE_MINUTES
        }


# ═══════════════════════════════════════════════════════
# ENGINE #9: SESSION MEMORY ENGINE
# ═══════════════════════════════════════════════════════

class SessionMemoryEngine:
    """
    Remembers recent performance patterns.
    
    PRINCIPLES:
    - Learn from recent outcomes
    - If pattern failing, stop repeating it
    - Adaptive behavior
    """
    
    MIN_SAMPLE_SIZE = 5
    MAX_MEMORY_TRADES = 50
    
    def __init__(self):
        self.name = "SessionMemoryEngine"
        self.memory = deque(maxlen=self.MAX_MEMORY_TRADES)
    
    def record_trade(
        self,
        setup_type: str,
        regime: str,
        score: float,
        outcome: bool,
        profit: float
    ):
        """Record trade outcome"""
        self.memory.append({
            'timestamp': datetime.now(),
            'setup_type': setup_type,
            'regime': regime,
            'score': score,
            'outcome': outcome,
            'profit': profit
        })
    
    def analyze_pattern(
        self,
        proposed_setup_type: str,
        proposed_regime: str,
        proposed_score: float
    ) -> Dict:
        """Analyze if similar patterns have been successful"""
        
        if len(self.memory) < self.MIN_SAMPLE_SIZE:
            return {
                'sufficient_data': False,
                'veto': False,
                'veto_reason': "",
                'similar_trades': 0
            }
        
        # Find similar trades
        similar = [
            t for t in self.memory
            if t['setup_type'] == proposed_setup_type
            and t['regime'] == proposed_regime
            and abs(t['score'] - proposed_score) < 15  # Within 15 points
        ]
        
        if len(similar) < self.MIN_SAMPLE_SIZE:
            return {
                'sufficient_data': False,
                'veto': False,
                'veto_reason': "",
                'similar_trades': len(similar)
            }
        
        # Calculate success rate
        success_rate = sum(1 for t in similar if t['outcome']) / len(similar)
        avg_profit = sum(t['profit'] for t in similar) / len(similar)
        
        # Recent pattern failing?
        if success_rate < 0.3 and len(similar) >= 5:
            return {
                'sufficient_data': True,
                'success_rate': success_rate,
                'avg_profit': avg_profit,
                'similar_trades': len(similar),
                'veto': True,
                'veto_reason': f"Similar setups failing recently (win rate: {success_rate:.1%} over {len(similar)} trades)"
            }
        
        return {
            'sufficient_data': True,
            'success_rate': success_rate,
            'avg_profit': avg_profit,
            'similar_trades': len(similar),
            'veto': False,
            'veto_reason': ""
        }
    
    def get_status(self) -> dict:
        """Get engine status"""
        return {
            'name': self.name,
            'active': True,
            'memory_size': len(self.memory),
            'max_memory': self.MAX_MEMORY_TRADES
        }


# ═══════════════════════════════════════════════════════
# ENGINE #10: CONTRAFACTUAL ANALYZER
# ═══════════════════════════════════════════════════════

class ContrafactualAnalyzer:
    """
    Analyzes "what if" scenarios from past decisions.
    
    PRINCIPLES:
    - Learn from past mistakes
    - If similar trade failed before, reconsider
    - Pattern recognition across outcomes
    """
    
    def __init__(self):
        self.name = "ContrafactualAnalyzer"
        self.trade_history = deque(maxlen=100)
    
    def record_outcome(
        self,
        entry_conditions: Dict,
        outcome: bool,
        profit: float,
        exit_reason: str
    ):
        """Record trade outcome for analysis"""
        self.trade_history.append({
            'timestamp': datetime.now(),
            'conditions': entry_conditions,
            'outcome': outcome,
            'profit': profit,
            'exit_reason': exit_reason
        })
    
    def analyze_proposal(self, proposed_conditions: Dict) -> Dict:
        """Analyze if similar conditions led to losses"""
        
        if len(self.trade_history) < 10:
            return {
                'veto': False,
                'veto_reason': "",
                'similar_outcomes': []
            }
        
        # Find similar past trades
        similar = []
        for trade in self.trade_history:
            similarity = self._calculate_similarity(
                proposed_conditions,
                trade['conditions']
            )
            if similarity > 0.7:  # 70% similar
                similar.append({
                    'similarity': similarity,
                    'outcome': trade['outcome'],
                    'profit': trade['profit']
                })
        
        if len(similar) < 3:
            return {
                'veto': False,
                'veto_reason': "",
                'similar_outcomes': similar
            }
        
        # Check outcomes
        failures = sum(1 for t in similar if not t['outcome'])
        failure_rate = failures / len(similar)
        
        if failure_rate > 0.7:  # 70% of similar trades failed
            return {
                'veto': True,
                'veto_reason': f"Similar setups have {failure_rate:.0%} failure rate ({failures}/{len(similar)} trades)",
                'similar_outcomes': similar
            }
        
        return {
            'veto': False,
            'veto_reason': "",
            'similar_outcomes': similar
        }
    
    def get_status(self) -> dict:
        """Get engine status"""
        return {
            'name': self.name,
            'active': True,
            'trade_history_size': len(self.trade_history),
            'max_history': self.trade_history.maxlen
        }
    
    def _calculate_similarity(self, conditions1: Dict, conditions2: Dict) -> float:
        """Calculate similarity between two condition sets"""
        # Simplified similarity metric
        # In production: use more sophisticated matching
        
        matching_keys = 0
        total_keys = len(set(list(conditions1.keys()) + list(conditions2.keys())))
        
        for key in conditions1:
            if key in conditions2:
                if isinstance(conditions1[key], (int, float)):
                    # Numeric comparison
                    if abs(conditions1[key] - conditions2[key]) < 0.1:
                        matching_keys += 1
                else:
                    # Exact match
                    if conditions1[key] == conditions2[key]:
                        matching_keys += 1
        
        return matching_keys / total_keys if total_keys > 0 else 0


# ═══════════════════════════════════════════════════════
# ENGINE #11: CAPITAL PRESERVATION ADVISOR
# ═══════════════════════════════════════════════════════

class CapitalPreservationAdvisor:
    """
    Advises on capital preservation strategies.
    
    PRINCIPLES:
    - Preservation > Growth
    - Compound long-term > Short-term gains
    - Drawdown control critical
    - Size down in adversity
    """
    
    MAX_ACCEPTABLE_DRAWDOWN_PCT = 15.0
    REDUCTION_TRIGGER_DRAWDOWN_PCT = 10.0
    
    def __init__(self):
        self.name = "CapitalPreservationAdvisor"
        self.peak_balance = 0.0
    
    def advise(
        self,
        current_balance: float,
        daily_loss: float,
        consecutive_losses: int,
        open_risk: float
    ) -> Dict:
        """Provide capital preservation advice"""
        
        # Update peak
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
        
        # Calculate drawdown
        if self.peak_balance > 0:
            current_dd_pct = ((self.peak_balance - current_balance) / self.peak_balance * 100)
            potential_dd_pct = ((self.peak_balance - (current_balance - open_risk)) / self.peak_balance * 100)
        else:
            self.peak_balance = current_balance
            current_dd_pct = 0
            potential_dd_pct = 0
        
        # Veto if approaching max drawdown
        if potential_dd_pct > self.MAX_ACCEPTABLE_DRAWDOWN_PCT:
            return {
                'veto': True,
                'veto_reason': f"Potential drawdown {potential_dd_pct:.1f}% exceeds maximum {self.MAX_ACCEPTABLE_DRAWDOWN_PCT}%",
                'current_drawdown_pct': current_dd_pct,
                'recommendation': "STOP_TRADING",
                'position_size_adjustment': 0.0
            }
        
        # Recommend reduction if in drawdown
        if current_dd_pct > self.REDUCTION_TRIGGER_DRAWDOWN_PCT:
            reduction_factor = 0.5  # Reduce size by 50%
            return {
                'veto': False,
                'veto_reason': "",
                'current_drawdown_pct': current_dd_pct,
                'recommendation': "REDUCE_SIZE",
                'position_size_adjustment': reduction_factor,
                'message': f"In {current_dd_pct:.1f}% drawdown - reducing position size to {reduction_factor:.0%}"
            }
        
        # All clear
        return {
            'veto': False,
            'veto_reason': "",
            'current_drawdown_pct': current_dd_pct,
            'recommendation': "CONTINUE",
            'position_size_adjustment': 1.0
        }
    
    def get_status(self) -> dict:
        """Get engine status"""
        return {
            'name': self.name,
            'active': True,
            'peak_balance': self.peak_balance,
            'max_drawdown_allowed_pct': self.MAX_ACCEPTABLE_DRAWDOWN_PCT
        }
