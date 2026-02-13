"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MARKER GENERATION ENGINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Intelligent decision-to-visual-marker converter.
Transforms bot decisions into professional chart markers
with institutional clarity.

CORE PRINCIPLE: Every decision deserves a marker.
Even "NO TRADE" decisions are visual teaching moments.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Optional
from events import (
    MarkerEvent,
    MarkerType,
    ExecutionStatus,
    MarketContext,
    RiskLevel,
    BotMode,
    create_decision_marker,
    create_no_trade_marker,
    create_pause_marker,
    create_high_risk_marker
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DECISION MARKER GENERATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class MarkerGenerator:
    """
    Converts bot decisions into professional visual markers.
    
    Philosophy:
    - Every significant decision creates a marker
    - "DO NOT TRADE" is as important as "BUY/SELL"
    - Visual intensity reflects confidence
    - Explanation clarity over technical jargon
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.last_marker: Optional[MarkerEvent] = None
    
    def generate_trade_marker(
        self,
        direction: str,  # "BUY" or "SELL"
        price: float,
        score: float,
        prob_buy: float,
        prob_sell: float,
        confidence: str,
        executed: bool,
        market_analysis: dict,
        mode: str,
        ticket: Optional[int] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None
    ) -> MarkerEvent:
        """
        Generate BUY or SELL marker with full context.
        
        Args:
            direction: "BUY" or "SELL"
            price: Current market price
            score: Quality score (0-100)
            prob_buy: Buy probability
            prob_sell: Sell probability
            confidence: "ALTA", "MEDIA", "BAIXA"
            executed: Whether trade was actually executed
            market_analysis: Dict from market_context.analyze_market_context()
            mode: "AUTO", "HYBRID", "MANUAL"
            ticket: MT5 ticket if executed
            sl: Stop loss if executed
            tp: Take profit if executed
        """
        
        # Convert confidence to float
        confidence_val = self._parse_confidence(confidence, prob_buy, prob_sell, direction)
        
        # Build human-readable reason
        reason = self._build_trade_reason(
            direction=direction,
            score=score,
            confidence=confidence,
            market_analysis=market_analysis,
            executed=executed
        )
        
        # Technical details for advanced users
        technical_details = {
            "score": score,
            "prob_buy": prob_buy,
            "prob_sell": prob_sell,
            "trend_strength": market_analysis.get("trend_strength", 0),
            "volatility": market_analysis.get("volatility", 0),
            "liquidity": market_analysis.get("liquidity_score", 0),
            "session": market_analysis.get("session", "UNKNOWN"),
            "atr": market_analysis.get("atr", 0)
        }
        
        # Create marker
        marker = create_decision_marker(
            symbol=self.symbol,
            price=price,
            direction=direction,
            score=score,
            confidence=confidence_val,
            executed=executed,
            market_context=market_analysis["context"],
            risk_level=market_analysis["risk_level"],
            mode=self._parse_mode(mode),
            reason=reason,
            technical_details=technical_details,
            ticket=ticket,
            sl=sl,
            tp=tp
        )
        
        self.last_marker = marker
        return marker
    
    def generate_no_trade_marker(
        self,
        price: float,
        score: float,
        market_analysis: dict,
        block_reason: str
    ) -> MarkerEvent:
        """
        Generate NO TRADE marker — critical for user education.
        
        These markers teach users WHY not to trade,
        building discipline and understanding.
        """
        
        reason = self._build_no_trade_reason(block_reason, market_analysis, score)
        
        marker = create_no_trade_marker(
            symbol=self.symbol,
            price=price,
            reason=reason,
            market_context=market_analysis["context"],
            risk_level=market_analysis["risk_level"],
            score=score
        )
        
        self.last_marker = marker
        return marker
    
    def generate_pause_marker(
        self,
        price: float,
        pause_reason: str,
        risk_level: RiskLevel = RiskLevel.HIGH
    ) -> MarkerEvent:
        """Generate BOT PAUSED marker"""
        
        marker = create_pause_marker(
            symbol=self.symbol,
            price=price,
            reason=self._format_pause_reason(pause_reason),
            risk_level=risk_level
        )
        
        self.last_marker = marker
        return marker
    
    def generate_high_risk_marker(
        self,
        price: float,
        market_analysis: dict
    ) -> MarkerEvent:
        """Generate HIGH RISK warning marker"""
        
        reason = self._build_high_risk_reason(market_analysis)
        
        marker = create_high_risk_marker(
            symbol=self.symbol,
            price=price,
            reason=reason,
            market_context=market_analysis["context"]
        )
        
        self.last_marker = marker
        return marker
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # REASON BUILDERS — HUMAN LANGUAGE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _build_trade_reason(
        self,
        direction: str,
        score: float,
        confidence: str,
        market_analysis: dict,
        executed: bool
    ) -> str:
        """Build clear, institutional explanation"""
        
        context = market_analysis["context"].value
        session = market_analysis["session"]
        trend_strength = market_analysis.get("trend_strength", 0)
        
        if executed:
            prefix = "Trade executed"
        else:
            prefix = "Trade candidate identified"
        
        # Quality descriptor
        if score >= 85:
            quality = "high-quality"
        elif score >= 70:
            quality = "moderate-quality"
        else:
            quality = "conditional"
        
        # Context descriptor
        context_desc = self._describe_context(context, session)
        
        # Trend component
        if trend_strength > 0.6:
            trend_desc = "strong directional movement"
        elif trend_strength > 0.3:
            trend_desc = "moderate trend"
        else:
            trend_desc = "ranging conditions"
        
        return (
            f"{prefix}: {quality} {direction} setup detected. "
            f"Market shows {trend_desc} during {session} session. "
            f"{context_desc}"
        )
    
    def _build_no_trade_reason(
        self,
        block_reason: str,
        market_analysis: dict,
        score: float
    ) -> str:
        """Explain WHY not to trade — educational"""
        
        context = market_analysis["context"].value
        risk = market_analysis["risk_level"].value
        
        reasons = {
            "LOW_SCORE": f"Setup quality insufficient (score: {score:.0f}/100)",
            "POSITION_ACTIVE": "Existing position requires attention first",
            "MAX_TRADES": "Daily trade limit reached — preserving capital",
            "MAX_RISK": "Daily risk threshold met — risk management protocol",
            "CONSECUTIVE_LOSSES": "Recovery mode active — waiting for better conditions",
            "PROFIT_TARGET": "Daily profit target achieved — locking in gains",
            "PAUSED": "Bot in pause state — manual intervention required",
            "HIGH_RISK_CONTEXT": f"Elevated market risk ({risk}) — exercise caution",
            "NEWS_WINDOW": "High-impact news event nearby — avoiding uncertainty",
            "LOW_LIQUIDITY": "Insufficient market liquidity — spreads may be unfavorable",
            "OFF_HOURS": "Outside optimal trading hours — waiting for better participation"
        }
        
        base_reason = reasons.get(block_reason, "Market conditions not optimal for entry")
        
        return f"{base_reason}. Context: {context}."
    
    def _build_high_risk_reason(self, market_analysis: dict) -> str:
        """Explain high-risk conditions"""
        
        context = market_analysis["context"].value
        volatility = market_analysis.get("volatility", 0)
        
        if volatility > 0.8:
            return f"Extreme volatility detected ({volatility:.0%}). Increased probability of sudden price swings."
        
        if context == "NEWS_WINDOW":
            return "High-impact economic data release imminent. Market may gap or spike unexpectedly."
        
        if context == "LOW_LIQUIDITY":
            return "Thin order book detected. Executions may experience significant slippage."
        
        return f"Elevated risk environment ({context}). Proceed with heightened caution."
    
    def _format_pause_reason(self, reason: str) -> str:
        """Format pause reason for display"""
        
        pause_formats = {
            "MAX_DAILY_RISK": "Daily risk limit reached — bot paused until next session",
            "CONSECUTIVE_LOSSES": "Multiple consecutive losses — entering recovery mode",
            "MANUAL_PAUSE": "Manual pause activated — bot awaiting user intervention",
            "SYSTEM_ERROR": "System anomaly detected — pausing for safety",
            "PROFIT_TARGET": "Daily profit target achieved — preserving gains"
        }
        
        return pause_formats.get(reason, f"Bot paused: {reason}")
    
    def _describe_context(self, context: str, session: str) -> str:
        """Describe market context in simple terms"""
        
        context_map = {
            "TRENDING": "Momentum strategies favored.",
            "RANGING": "Support/resistance strategies preferred.",
            "VOLATILE": "Exercise caution with position sizing.",
            "LOW_LIQUIDITY": "Avoid aggressive entries.",
            "NEWS_WINDOW": "Elevated uncertainty.",
            "UNKNOWN": "Awaiting clearer structure."
        }
        
        return context_map.get(context, "Market structure unclear.")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PARSERS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _parse_confidence(
        self,
        confidence: str,
        prob_buy: float,
        prob_sell: float,
        direction: str
    ) -> float:
        """Convert confidence string to float (0-1)"""
        
        # Use probability difference as primary metric
        prob = prob_buy if direction == "BUY" else prob_sell
        confidence_val = prob / 100.0
        
        # Adjust by confidence level
        if confidence == "ALTA":
            confidence_val = min(1.0, confidence_val * 1.1)
        elif confidence == "MEDIA":
            confidence_val = min(1.0, confidence_val * 0.9)
        else:  # BAIXA
            confidence_val = min(1.0, confidence_val * 0.7)
        
        return round(confidence_val, 2)
    
    def _parse_mode(self, mode: str) -> BotMode:
        """Parse mode string to enum"""
        mode_map = {
            "AUTO": BotMode.AUTO,
            "HYBRID": BotMode.HYBRID,
            "MANUAL": BotMode.MANUAL,
            "SILENCE": BotMode.SILENCE
        }
        return mode_map.get(mode, BotMode.MANUAL)
