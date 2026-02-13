"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI ENGINE #2: RISK ENGINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESPONSIBILITY:
Enforce risk limits and capital preservation.
Calculate position sizing and risk/reward.

CAN VETO IF:
- Risk/reward ratio insufficient
- Position size exceeds limits
- Risk exposure too high
- Capital preservation rules violated

CANNOT:
- Ignore safety limits
- Allow excessive risk
- Override capital preservation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Optional
from dataclasses import dataclass
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from safety import get_safety_monitor


@dataclass
class RiskAssessment:
    """Risk evaluation result"""
    approved: bool
    position_size: float
    risk_reward_ratio: float
    risk_amount: float
    veto: bool
    veto_reason: str
    warnings: list


class RiskEngine:
    """
    Enforces risk limits and capital preservation.
    
    PRINCIPLES:
    - Capital preservation > Opportunity capture
    - Risk/reward minimum 1:2
    - Position sizing based on risk tolerance
    - Multiple safety checks
    """
    
    # Risk parameters
    MIN_RISK_REWARD_RATIO = 2.0  # Minimum 1:2
    MAX_RISK_PER_TRADE_PCT = 1.0  # 1% max risk per trade
    IDEAL_RISK_PER_TRADE_PCT = 0.5  # 0.5% ideal
    
    def __init__(self):
        self.name = "RiskEngine"
        self.version = "1.0.0"
        self.safety_monitor = get_safety_monitor()
    
    def assess(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        account_balance: float,
        direction: str
    ) -> RiskAssessment:
        """
        Assess trade risk and calculate position size.
        
        Returns RiskAssessment with veto if risk unacceptable.
        """
        
        warnings = []
        
        # 1. Calculate risk/reward ratio
        if direction == "BUY":
            risk_points = entry_price - stop_loss
            reward_points = take_profit - entry_price
        else:  # SELL
            risk_points = stop_loss - entry_price
            reward_points = entry_price - take_profit
        
        if risk_points <= 0:
            return RiskAssessment(
                approved=False,
                position_size=0.0,
                risk_reward_ratio=0.0,
                risk_amount=0.0,
                veto=True,
                veto_reason="Invalid stop loss placement",
                warnings=["Stop loss must be placed beyond entry"]
            )
        
        risk_reward_ratio = reward_points / risk_points if risk_points > 0 else 0
        
        # 2. Check minimum R:R
        if risk_reward_ratio < self.MIN_RISK_REWARD_RATIO:
            return RiskAssessment(
                approved=False,
                position_size=0.0,
                risk_reward_ratio=risk_reward_ratio,
                risk_amount=0.0,
                veto=True,
                veto_reason=f"Risk/reward too low ({risk_reward_ratio:.2f} < {self.MIN_RISK_REWARD_RATIO})",
                warnings=["Insufficient profit potential vs risk"]
            )
        
        # 3. Calculate position size based on risk tolerance
        risk_amount = account_balance * (self.IDEAL_RISK_PER_TRADE_PCT / 100)
        
        # Position size = Risk Amount / Risk in Points
        # For forex: lot size calculation
        # Simplified: risk_amount / risk_points
        position_size = min(
            risk_amount / risk_points / 10,  # Simplified forex calculation
            self.safety_monitor.limits.MAX_POSITION_SIZE
        )
        
        # 4. Safety monitor checks
        can_trade, reason = self.safety_monitor.can_trade()
        if not can_trade:
            return RiskAssessment(
                approved=False,
                position_size=0.0,
                risk_reward_ratio=risk_reward_ratio,
                risk_amount=0.0,
                veto=True,
                veto_reason=f"Safety limit: {reason}",
                warnings=["Safety monitor blocked trade"]
            )
        
        # 5. Check if within position size limits
        if position_size > self.safety_monitor.limits.MAX_POSITION_SIZE:
            warnings.append(f"Position size reduced to max limit ({self.safety_monitor.limits.MAX_POSITION_SIZE})")
            position_size = self.safety_monitor.limits.MAX_POSITION_SIZE
        
        # 6. Warn if risk/reward could be better
        if risk_reward_ratio < 3.0:
            warnings.append(f"Consider improving R:R (current: {risk_reward_ratio:.2f}, ideal: 3.0+)")
        
        return RiskAssessment(
            approved=True,
            position_size=position_size,
            risk_reward_ratio=risk_reward_ratio,
            risk_amount=risk_amount,
            veto=False,
            veto_reason="",
            warnings=warnings
        )
    
    def validate_position_size(self, lot_size: float) -> tuple[bool, Optional[str]]:
        """Validate position size against limits"""
        valid, reason = self.safety_monitor.validate_trade(
            score=100,  # Score not relevant for size validation
            lot_size=lot_size
        )
        return valid, reason
    
    def calculate_drawdown_risk(
        self,
        current_balance: float,
        peak_balance: float,
        open_risk: float
    ) -> Dict:
        """Calculate current drawdown and risk"""
        
        current_drawdown_pct = ((peak_balance - current_balance) / peak_balance * 100) if peak_balance > 0 else 0
        potential_drawdown_pct = ((peak_balance - (current_balance - open_risk)) / peak_balance * 100) if peak_balance > 0 else 0
        
        return {
            'current_drawdown_pct': current_drawdown_pct,
            'potential_drawdown_pct': potential_drawdown_pct,
            'open_risk': open_risk,
            'warning': potential_drawdown_pct > 10.0,  # Warn if potential DD > 10%
            'critical': potential_drawdown_pct > 20.0  # Critical if potential DD > 20%
        }
    
    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            'name': self.name,
            'version': self.version,
            'min_risk_reward': self.MIN_RISK_REWARD_RATIO,
            'max_risk_per_trade_pct': self.MAX_RISK_PER_TRADE_PCT,
            'ideal_risk_per_trade_pct': self.IDEAL_RISK_PER_TRADE_PCT,
            'active': True
        }
