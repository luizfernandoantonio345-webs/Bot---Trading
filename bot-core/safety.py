"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRODUCTION SAFETY LAYER — CAPITAL REAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HARDENING FOR LIVE TRADING WITH REAL CAPITAL.

ABSOLUTE RULES:
- Bot pauses on ANY error
- Limits are NEVER exceeded
- Human maintains final control
- No unexpected behavior
- State is always explicit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import os
from datetime import datetime, date
from enum import Enum
from typing import Optional
from dataclasses import dataclass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BOT STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BotState(str, Enum):
    """Explicit bot operational state"""
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"
    STOPPED = "STOPPED"


class TradingMode(str, Enum):
    """Trading execution modes"""
    HYBRID = "HYBRID"      # Score >= 65%: recommend, human confirms
    AUTO = "AUTO"          # Score >= 90%: auto execute
    NO_TRADE = "NO_TRADE"  # All trading disabled


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SAFETY LIMITS (ABSOLUTE)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class SafetyLimits:
    """Absolute safety limits for live trading"""
    
    # Daily limits
    MAX_DAILY_LOSS: float = 100.0           # ABSOLUTE daily loss limit (USD)
    MAX_DAILY_TRADES: int = 5               # Maximum trades per day
    MAX_CONSECUTIVE_LOSSES: int = 3         # Auto-pause after N losses
    
    # Position limits
    MAX_POSITION_SIZE: float = 0.01         # Maximum lot size
    MAX_SIMULTANEOUS_POSITIONS: int = 1     # Only 1 position at a time
    
    # Execution limits
    EXECUTION_TIMEOUT_SECONDS: int = 10     # Order execution timeout
    MIN_SCORE_HYBRID: float = 65.0          # Minimum score for HYBRID recommendation
    MIN_SCORE_AUTO: float = 90.0            # Minimum score for AUTO execution
    
    # Risk limits
    MAX_SLIPPAGE_POINTS: float = 5.0        # Maximum allowed slippage
    MIN_STOP_LOSS_POINTS: float = 10.0      # Minimum SL distance


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# KILL SWITCH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class KillSwitch:
    """
    Global kill switch for emergency stop.
    
    Can be triggered by:
    - Manual command
    - Error detection
    - Limit breach
    - App request
    """
    
    _instance = None
    _kill_switch_file = "KILL_SWITCH.lock"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._activated = False
        return cls._instance
    
    def activate(self, reason: str):
        """Activate kill switch - stops all trading"""
        self._activated = True
        
        # Create lock file
        with open(self._kill_switch_file, 'w') as f:
            json.dump({
                'activated': True,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"🛑 KILL SWITCH ACTIVATED: {reason}")
    
    def deactivate(self):
        """Deactivate kill switch - manual only"""
        self._activated = False
        
        if os.path.exists(self._kill_switch_file):
            os.remove(self._kill_switch_file)
        
        print("✅ Kill switch deactivated")
    
    def is_active(self) -> bool:
        """Check if kill switch is active"""
        # Check memory
        if self._activated:
            return True
        
        # Check file (survives restarts)
        if os.path.exists(self._kill_switch_file):
            self._activated = True
            return True
        
        return False
    
    def get_reason(self) -> Optional[str]:
        """Get activation reason"""
        if os.path.exists(self._kill_switch_file):
            try:
                with open(self._kill_switch_file, 'r') as f:
                    data = json.load(f)
                    return data.get('reason')
            except:
                return "Unknown"
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SAFETY MONITOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SafetyMonitor:
    """
    Monitors all safety limits and enforces rules.
    Pauses bot on ANY breach.
    """
    
    def __init__(self, limits: SafetyLimits):
        self.limits = limits
        self.kill_switch = KillSwitch()
        self.state = BotState.STOPPED
        self.mode = TradingMode.HYBRID
        
        # Daily counters
        self.daily_loss = 0.0
        self.daily_profit = 0.0
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.last_reset_date = date.today()
        
        # State file
        self.state_file = "safety_state.json"
        self._load_state()
    
    def _load_state(self):
        """Load state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    
                    # Check if date changed
                    saved_date = date.fromisoformat(data.get('date', str(date.today())))
                    if saved_date != date.today():
                        self._reset_daily_counters()
                    else:
                        self.daily_loss = data.get('daily_loss', 0.0)
                        self.daily_profit = data.get('daily_profit', 0.0)
                        self.daily_trades = data.get('daily_trades', 0)
                        self.consecutive_losses = data.get('consecutive_losses', 0)
                        self.state = BotState(data.get('state', 'STOPPED'))
                        self.mode = TradingMode(data.get('mode', 'HYBRID'))
            except:
                self._reset_daily_counters()
    
    def _save_state(self):
        """Save state to file"""
        data = {
            'date': str(date.today()),
            'daily_loss': self.daily_loss,
            'daily_profit': self.daily_profit,
            'daily_trades': self.daily_trades,
            'consecutive_losses': self.consecutive_losses,
            'state': self.state.value,
            'mode': self.mode.value,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _reset_daily_counters(self):
        """Reset daily counters (new trading day)"""
        self.daily_loss = 0.0
        self.daily_profit = 0.0
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.last_reset_date = date.today()
        self._save_state()
    
    def can_trade(self) -> tuple[bool, Optional[str]]:
        """
        Check if trading is allowed.
        Returns (allowed, reason_if_not)
        """
        
        # Check kill switch first
        if self.kill_switch.is_active():
            return False, f"KILL_SWITCH: {self.kill_switch.get_reason()}"
        
        # Check bot state
        if self.state != BotState.RUNNING:
            return False, f"BOT_STATE: {self.state.value}"
        
        # Check mode
        if self.mode == TradingMode.NO_TRADE:
            return False, "MODE: NO_TRADE"
        
        # Check daily loss limit
        if self.daily_loss >= self.limits.MAX_DAILY_LOSS:
            self.pause("MAX_DAILY_LOSS_REACHED")
            return False, f"DAILY_LOSS: {self.daily_loss:.2f} >= {self.limits.MAX_DAILY_LOSS}"
        
        # Check daily trades limit
        if self.daily_trades >= self.limits.MAX_DAILY_TRADES:
            self.pause("MAX_DAILY_TRADES_REACHED")
            return False, f"DAILY_TRADES: {self.daily_trades} >= {self.limits.MAX_DAILY_TRADES}"
        
        # Check consecutive losses
        if self.consecutive_losses >= self.limits.MAX_CONSECUTIVE_LOSSES:
            self.pause("MAX_CONSECUTIVE_LOSSES")
            return False, f"CONSECUTIVE_LOSSES: {self.consecutive_losses}"
        
        return True, None
    
    def validate_trade(self, score: float, lot_size: float) -> tuple[bool, Optional[str]]:
        """Validate trade parameters before execution"""
        
        # Check score threshold
        if self.mode == TradingMode.HYBRID:
            if score < self.limits.MIN_SCORE_HYBRID:
                return False, f"SCORE_TOO_LOW: {score:.1f} < {self.limits.MIN_SCORE_HYBRID}"
        
        elif self.mode == TradingMode.AUTO:
            if score < self.limits.MIN_SCORE_AUTO:
                return False, f"SCORE_TOO_LOW_AUTO: {score:.1f} < {self.limits.MIN_SCORE_AUTO}"
        
        # Check lot size
        if lot_size > self.limits.MAX_POSITION_SIZE:
            return False, f"LOT_SIZE_EXCEEDED: {lot_size} > {self.limits.MAX_POSITION_SIZE}"
        
        return True, None
    
    def record_trade_result(self, profit: float):
        """Record trade result and update counters"""
        
        self.daily_trades += 1
        
        if profit < 0:
            self.daily_loss += abs(profit)
            self.consecutive_losses += 1
        else:
            self.daily_profit += profit
            self.consecutive_losses = 0  # Reset on win
        
        self._save_state()
        
        # Check if limits breached
        can_trade, reason = self.can_trade()
        if not can_trade:
            print(f"⚠️ Limit breached: {reason}")
    
    def start(self):
        """Start bot (from STOPPED)"""
        if self.kill_switch.is_active():
            print(f"❌ Cannot start: Kill switch active ({self.kill_switch.get_reason()})")
            return False
        
        self.state = BotState.RUNNING
        self._save_state()
        print("✅ Bot started")
        return True
    
    def pause(self, reason: str):
        """Pause bot"""
        self.state = BotState.PAUSED
        self._save_state()
        print(f"⏸️ Bot paused: {reason}")
    
    def resume(self):
        """Resume bot (from PAUSED)"""
        if self.kill_switch.is_active():
            print(f"❌ Cannot resume: Kill switch active ({self.kill_switch.get_reason()})")
            return False
        
        self.state = BotState.RUNNING
        self._save_state()
        print("▶️ Bot resumed")
        return True
    
    def error(self, error_msg: str):
        """Set error state and pause"""
        self.state = BotState.ERROR
        self._save_state()
        print(f"❌ Bot error: {error_msg}")
        
        # Auto-pause on error
        self.pause(f"ERROR: {error_msg}")
    
    def set_mode(self, mode: TradingMode):
        """Change trading mode"""
        self.mode = mode
        self._save_state()
        print(f"🔄 Mode changed: {mode.value}")
    
    def get_status(self) -> dict:
        """Get current safety status"""
        return {
            'state': self.state.value,
            'mode': self.mode.value,
            'kill_switch_active': self.kill_switch.is_active(),
            'kill_switch_reason': self.kill_switch.get_reason(),
            'daily_loss': self.daily_loss,
            'daily_profit': self.daily_profit,
            'daily_trades': self.daily_trades,
            'consecutive_losses': self.consecutive_losses,
            'limits': {
                'max_daily_loss': self.limits.MAX_DAILY_LOSS,
                'max_daily_trades': self.limits.MAX_DAILY_TRADES,
                'max_consecutive_losses': self.limits.MAX_CONSECUTIVE_LOSSES
            },
            'can_trade': self.can_trade()[0],
            'block_reason': self.can_trade()[1]
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GLOBAL INSTANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_safety_monitor = None


def get_safety_monitor() -> SafetyMonitor:
    """Get global safety monitor instance"""
    global _safety_monitor
    if _safety_monitor is None:
        _safety_monitor = SafetyMonitor(SafetyLimits())
    return _safety_monitor


def emergency_stop(reason: str):
    """Emergency stop - activates kill switch"""
    kill_switch = KillSwitch()
    kill_switch.activate(reason)
    
    monitor = get_safety_monitor()
    monitor.pause(f"EMERGENCY_STOP: {reason}")
