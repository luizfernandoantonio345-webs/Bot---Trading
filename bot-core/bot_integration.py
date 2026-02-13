"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOT INTEGRATION LAYER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Clean integration of marker system into existing bot.
Separates trading logic from visualization logic.

USAGE:
    from bot_integration import BotMarkerSystem
    
    marker_system = BotMarkerSystem(symbol="EURUSD")
    
    # On each bot cycle:
    marker_system.process_decision(
        price=1.08500,
        direction="BUY",
        score=85,
        prob_buy=72,
        prob_sell=28,
        confidence="ALTA",
        executed=True,
        df_m15=df_m15,
        df_h1=df_h1,
        ...
    )
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pandas as pd
from typing import Optional
from datetime import datetime

from market_context import analyze_market_context
from marker_generator import MarkerGenerator
from event_emitter import emit_marker, emit_context, emit_state
from events import MarketContextEvent, BotStateEvent, BotMode, RiskLevel
from safety import get_safety_monitor, SafetyMonitor, emergency_stop


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BOT MARKER SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BotMarkerSystem:
    """
    Central integration point for marker system.
    
    Responsibilities:
    - Analyze market context
    - Generate appropriate markers
    - Emit events to backend/app
    - Maintain clean separation from trading logic
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.generator = MarkerGenerator(symbol)
        self.safety = get_safety_monitor()
        self.last_context = None
        self.last_state = None
    
    def process_decision(
        self,
        price: float,
        direction: str,
        score: float,
        prob_buy: float,
        prob_sell: float,
        confidence: str,
        executed: bool,
        df_m15: pd.DataFrame,
        df_h1: pd.DataFrame,
        mode: str,
        ticket: Optional[int] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        can_trade: bool = True,
        block_reason: Optional[str] = None
    ):
        """
        Process bot decision and generate appropriate markers.
        
        This is THE integration point - call this on every bot cycle.
        WITH PRODUCTION SAFETY CHECKS.
        """
        
        try:
            # SAFETY: Check if kill switch active
            if self.safety.kill_switch.is_active():
                print(f"🛑 Kill switch active: {self.safety.kill_switch.get_reason()}")
                return
            
            # SAFETY: Check if bot can trade
            can_trade_safe, reason = self.safety.can_trade()
            if not can_trade_safe and executed:
                print(f"⚠️ SAFETY VIOLATION: Trade executed but not allowed: {reason}")
                emergency_stop(f"Safety violation: {reason}")
                return
            
            # 1. Analyze market context
            market_analysis = analyze_market_context(df_m15, df_h1)
        
        except Exception as e:
            print(f"❌ ERROR in process_decision: {e}")
            self.safety.error(str(e))
            return
        
        # 2. Emit context update (periodic)
        self._emit_context_if_changed(market_analysis)
        
        # 3. Generate and emit appropriate marker
        if executed:
            # EXECUTION marker
            marker = self.generator.generate_trade_marker(
                direction=direction,
                price=price,
                score=score,
                prob_buy=prob_buy,
                prob_sell=prob_sell,
                confidence=confidence,
                executed=True,
                market_analysis=market_analysis,
                mode=mode,
                ticket=ticket,
                sl=sl,
                tp=tp
            )
            emit_marker(marker)
        
        elif score >= 50 and can_trade:
            # RECOMMENDATION marker
            marker = self.generator.generate_trade_marker(
                direction=direction,
                price=price,
                score=score,
                prob_buy=prob_buy,
                prob_sell=prob_sell,
                confidence=confidence,
                executed=False,
                market_analysis=market_analysis,
                mode=mode
            )
            emit_marker(marker)
        
        elif not can_trade and block_reason:
            # NO TRADE marker
            marker = self.generator.generate_no_trade_marker(
                price=price,
                score=score,
                market_analysis=market_analysis,
                block_reason=block_reason
            )
            emit_marker(marker)
        
        elif market_analysis["risk_level"] == RiskLevel.EXTREME:
            # HIGH RISK marker
            marker = self.generator.generate_high_risk_marker(
                price=price,
                market_analysis=market_analysis
            )
            emit_marker(marker)
    
    def process_pause(
        self,
        price: float,
        pause_reason: str,
        risk_level: RiskLevel = RiskLevel.HIGH
    ):
        """Process bot pause event"""
        
        marker = self.generator.generate_pause_marker(
            price=price,
            pause_reason=pause_reason,
            risk_level=risk_level
        )
        emit_marker(marker)
    
    def update_bot_state(
        self,
        mode: str,
        active: bool,
        paused: bool = False,
        paused_reason: Optional[str] = None,
        daily_trades: int = 0,
        daily_pnl: float = 0.0,
        risk_utilized: float = 0.0
    ):
        """Update and emit bot state"""
        
        mode_enum = self._parse_mode(mode)
        
        state = BotStateEvent(
            timestamp=datetime.now().isoformat(),
            mode=mode_enum,
            active=active and not paused,
            paused_reason=paused_reason if paused else None,
            daily_trades=daily_trades,
            daily_pnl=daily_pnl,
            risk_utilized=risk_utilized
        )
        
        emit_state(state)
        self.last_state = state
    
    # ━━━━━ INTERNAL HELPERS ━━━━━
    
    def _emit_context_if_changed(self, market_analysis: dict):
        """Emit context event only if significantly changed"""
        
        current = market_analysis["context"]
        
        # Emit if context changed or first time
        if self.last_context != current:
            context_event = MarketContextEvent(
                timestamp=datetime.now().isoformat(),
                symbol=self.symbol,
                context=current,
                volatility=market_analysis["volatility"],
                liquidity_score=market_analysis["liquidity_score"],
                session=market_analysis["session"],
                trend_strength=market_analysis["trend_strength"]
            )
            
            emit_context(context_event)
            self.last_context = current
    
    def _parse_mode(self, mode: str) -> BotMode:
        """Parse mode string to enum"""
        mode_map = {
            "AUTO": BotMode.AUTO,
            "HYBRID": BotMode.HYBRID,
            "MANUAL": BotMode.MANUAL,
            "SILENCE": BotMode.SILENCE
        }
        return mode_map.get(mode, BotMode.MANUAL)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIMPLIFIED INTEGRATION FOR EXISTING BOT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def integrate_markers_into_bot(
    symbol: str,
    price: float,
    direction: str,
    score: float,
    prob_buy: float,
    prob_sell: float,
    confidence: str,
    executed: bool,
    df_m15: pd.DataFrame,
    df_h1: pd.DataFrame,
    mode: str,
    can_trade: bool = True,
    block_reason: str = None,
    ticket: int = None,
    sl: float = None,
    tp: float = None
):
    """
    Simplified integration function.
    
    Can be called directly from existing bot with minimal changes.
    """
    
    # Create system instance
    marker_system = BotMarkerSystem(symbol)
    
    # Process decision
    marker_system.process_decision(
        price=price,
        direction=direction,
        score=score,
        prob_buy=prob_buy,
        prob_sell=prob_sell,
        confidence=confidence,
        executed=executed,
        df_m15=df_m15,
        df_h1=df_h1,
        mode=mode,
        ticket=ticket,
        sl=sl,
        tp=tp,
        can_trade=can_trade,
        block_reason=block_reason
    )
