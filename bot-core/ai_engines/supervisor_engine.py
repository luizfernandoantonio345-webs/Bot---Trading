"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI ENGINE #6: SUPERVISOR ENGINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESPONSIBILITY:
Monitor bot health and operational status.
Trigger pause when conditions deteriorate.

CAN VETO IF:
- Performance degradation detected
- Unusual behavior pattern
- Error rate elevated
- System health compromised

CANNOT:
- Force trades
- Override other engine vetos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from safety import get_safety_monitor


@dataclass
class SupervisorStatus:
    """Supervisor assessment"""
    should_pause: bool
    reason: str
    health_score: float
    warnings: List[str]
    recommendations: List[str]


class SupervisorEngine:
    """
    Monitors system health and performance.
    
    PRINCIPLES:
    - Stop bot when performance degrades
    - Detect unusual patterns
    - Prevent cascade failures
    - Preserve capital over continuity
    """
    
    # Thresholds
    MAX_CONSECUTIVE_LOSSES = 3
    MAX_DAILY_LOSS_PCT = 5.0  # 5% of starting capital
    MIN_WIN_RATE_WINDOW = 0.30  # 30% minimum over 10 trades
    MAX_ERROR_RATE = 0.10  # 10% error rate
    
    def __init__(self):
        self.name = "SupervisorEngine"
        self.version = "1.0.0"
        self.safety = get_safety_monitor()
        self.recent_trades = []
        self.recent_errors = []
    
    def assess(
        self,
        recent_performance: Dict,
        error_count: int,
        total_operations: int
    ) -> SupervisorStatus:
        """
        Assess if bot should continue or pause.
        
        Returns SupervisorStatus with pause recommendation if needed.
        """
        
        warnings = []
        recommendations = []
        
        # 1. Check safety monitor
        safety_status = self.safety.get_status()
        if not safety_status['can_trade']:
            return SupervisorStatus(
                should_pause=True,
                reason=f"Safety limit: {safety_status['block_reason']}",
                health_score=0.0,
                warnings=["Safety monitor blocked trading"],
                recommendations=["Review safety limits", "Check daily counters"]
            )
        
        # 2. Check consecutive losses
        consecutive_losses = safety_status['consecutive_losses']
        if consecutive_losses >= self.MAX_CONSECUTIVE_LOSSES:
            return SupervisorStatus(
                should_pause=True,
                reason=f"{consecutive_losses} consecutive losses - cooling off period needed",
                health_score=0.3,
                warnings=[f"Losing streak: {consecutive_losses} in a row"],
                recommendations=["Review strategy", "Check market conditions", "Consider reducing position size"]
            )
        
        # 3. Check daily loss
        daily_loss = safety_status['daily_loss']
        if daily_loss > 0:
            warnings.append(f"Daily loss: ${daily_loss:.2f}")
            if daily_loss >= self.safety.limits.MAX_DAILY_LOSS * 0.8:
                warnings.append("Approaching daily loss limit")
        
        # 4. Check win rate (if enough data)
        if 'win_rate' in recent_performance and 'trade_count' in recent_performance:
            if recent_performance['trade_count'] >= 10:
                win_rate = recent_performance['win_rate']
                if win_rate < self.MIN_WIN_RATE_WINDOW:
                    return SupervisorStatus(
                        should_pause=True,
                        reason=f"Win rate too low ({win_rate:.1%}) - strategy reassessment needed",
                        health_score=0.4,
                        warnings=[f"Win rate: {win_rate:.1%} over {recent_performance['trade_count']} trades"],
                        recommendations=["Review strategy parameters", "Check market regime compatibility"]
                    )
        
        # 5. Check error rate
        if total_operations > 10:
            error_rate = error_count / total_operations
            if error_rate > self.MAX_ERROR_RATE:
                return SupervisorStatus(
                    should_pause=True,
                    reason=f"Error rate too high ({error_rate:.1%})",
                    health_score=0.2,
                    warnings=[f"Errors: {error_count}/{total_operations} operations"],
                    recommendations=["Check logs", "Verify MT5 connection", "Review code for bugs"]
                )
            elif error_rate > 0.05:
                warnings.append(f"Elevated error rate: {error_rate:.1%}")
        
        # 6. Calculate health score
        health_score = self._calculate_health_score(
            consecutive_losses,
            daily_loss,
            recent_performance.get('win_rate', 0.5),
            error_count / max(total_operations, 1)
        )
        
        # 7. Generate recommendations
        if consecutive_losses > 0:
            recommendations.append("Monitor next trade closely")
        if daily_loss > self.safety.limits.MAX_DAILY_LOSS * 0.5:
            recommendations.append("Consider reducing position size")
        if health_score < 0.7:
            recommendations.append("Increased vigilance recommended")
        
        return SupervisorStatus(
            should_pause=False,
            reason="",
            health_score=health_score,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def _calculate_health_score(
        self,
        consecutive_losses: int,
        daily_loss: float,
        win_rate: float,
        error_rate: float
    ) -> float:
        """Calculate overall system health score (0-1)"""
        
        # Loss penalty
        loss_score = max(0, 1.0 - (consecutive_losses / self.MAX_CONSECUTIVE_LOSSES))
        
        # Daily loss penalty
        daily_loss_score = max(0, 1.0 - (daily_loss / self.safety.limits.MAX_DAILY_LOSS))
        
        # Win rate score
        win_rate_score = win_rate
        
        # Error rate score
        error_score = max(0, 1.0 - (error_rate / self.MAX_ERROR_RATE))
        
        # Weighted average
        health = (
            loss_score * 0.3 +
            daily_loss_score * 0.3 +
            win_rate_score * 0.2 +
            error_score * 0.2
        )
        
        return health
    
    def record_trade(self, profit: float, success: bool):
        """Record trade result for supervision"""
        self.recent_trades.append({
            'timestamp': datetime.now(),
            'profit': profit,
            'success': success
        })
        
        # Keep last 20 trades
        if len(self.recent_trades) > 20:
            self.recent_trades = self.recent_trades[-20:]
    
    def record_error(self, error_type: str, error_msg: str):
        """Record error for supervision"""
        self.recent_errors.append({
            'timestamp': datetime.now(),
            'type': error_type,
            'message': error_msg
        })
        
        # Keep last 50 errors
        if len(self.recent_errors) > 50:
            self.recent_errors = self.recent_errors[-50:]
    
    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            'name': self.name,
            'version': self.version,
            'active': True,
            'recent_trade_count': len(self.recent_trades),
            'recent_error_count': len(self.recent_errors)
        }
