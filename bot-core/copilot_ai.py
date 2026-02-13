"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COPILOT AI — HUMAN EXPLANATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AI-powered explanation generator that translates
technical trading events into clear human language.

PHILOSOPHY:
- No jargon without context
- Education over hype
- Never promise profit
- Explain both actions AND inactions
- Build user understanding and discipline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from events import MarkerEvent, MarkerType, ExecutionStatus, RiskLevel, MarketContext
from typing import Dict, List


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COPILOT EXPLANATION ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CopilotAI:
    """
    Explanatory AI that makes trading decisions understandable.
    
    This is NOT a trading advisor.
    This is an educational transparency layer.
    """
    
    @staticmethod
    def explain(marker: MarkerEvent) -> Dict[str, str]:
        """
        Generate multi-level explanation for any marker.
        
        Returns:
            {
                "title": str,  # Short headline
                "summary": str,  # 1-2 sentence overview
                "details": str,  # Deeper explanation
                "context": str,  # Market context
                "risk": str,  # Risk assessment
                "action": str,  # What this means for user
                "learning": str  # Educational takeaway
            }
        """
        
        if marker.marker_type == MarkerType.BUY_CANDIDATE:
            return CopilotAI._explain_buy(marker)
        
        elif marker.marker_type == MarkerType.SELL_CANDIDATE:
            return CopilotAI._explain_sell(marker)
        
        elif marker.marker_type == MarkerType.NO_TRADE_ZONE:
            return CopilotAI._explain_no_trade(marker)
        
        elif marker.marker_type == MarkerType.BOT_PAUSED:
            return CopilotAI._explain_pause(marker)
        
        elif marker.marker_type == MarkerType.HIGH_RISK_CONTEXT:
            return CopilotAI._explain_high_risk(marker)
        
        return CopilotAI._explain_default(marker)
    
    # ━━━━━ TYPE-SPECIFIC EXPLAINERS ━━━━━
    
    @staticmethod
    def _explain_buy(marker: MarkerEvent) -> Dict[str, str]:
        """Explain BUY marker"""
        
        is_executed = marker.execution_status == ExecutionStatus.EXECUTED
        
        if is_executed:
            title = "🟢 Buy Position Opened"
            summary = f"Long position initiated at {marker.price:.5f} based on {marker.score:.0f}/100 setup quality."
        else:
            title = "🟢 Buy Opportunity Identified"
            summary = f"Potential long entry detected at {marker.price:.5f} with {marker.confidence:.0%} confidence."
        
        # Details
        details = CopilotAI._build_trade_details(marker, "buy")
        
        # Context
        context = CopilotAI._explain_context(marker.market_context, marker.technical_details)
        
        # Risk
        risk = CopilotAI._explain_risk(marker.risk_level, marker.stop_loss, marker.take_profit)
        
        # Action
        if is_executed:
            action = "Position is now active. Monitor for exit signals based on your risk management plan."
        else:
            action = (
                "This is a recommendation, not an order. "
                "Review the setup and decide if it aligns with your trading plan."
            )
        
        # Learning
        learning = CopilotAI._build_learning_point(marker, "buy")
        
        return {
            "title": title,
            "summary": summary,
            "details": details,
            "context": context,
            "risk": risk,
            "action": action,
            "learning": learning
        }
    
    @staticmethod
    def _explain_sell(marker: MarkerEvent) -> Dict[str, str]:
        """Explain SELL marker"""
        
        is_executed = marker.execution_status == ExecutionStatus.EXECUTED
        
        if is_executed:
            title = "🔴 Sell Position Opened"
            summary = f"Short position initiated at {marker.price:.5f} based on {marker.score:.0f}/100 setup quality."
        else:
            title = "🔴 Sell Opportunity Identified"
            summary = f"Potential short entry detected at {marker.price:.5f} with {marker.confidence:.0%} confidence."
        
        details = CopilotAI._build_trade_details(marker, "sell")
        context = CopilotAI._explain_context(marker.market_context, marker.technical_details)
        risk = CopilotAI._explain_risk(marker.risk_level, marker.stop_loss, marker.take_profit)
        
        if is_executed:
            action = "Position is now active. Monitor for exit signals based on your risk management plan."
        else:
            action = (
                "This is a recommendation, not an order. "
                "Review the setup and decide if it aligns with your trading plan."
            )
        
        learning = CopilotAI._build_learning_point(marker, "sell")
        
        return {
            "title": title,
            "summary": summary,
            "details": details,
            "context": context,
            "risk": risk,
            "action": action,
            "learning": learning
        }
    
    @staticmethod
    def _explain_no_trade(marker: MarkerEvent) -> Dict[str, str]:
        """Explain NO TRADE marker — critical for education"""
        
        title = "⚪ No Trade Advised"
        summary = marker.reason
        
        details = (
            "Not every market moment deserves a trade. "
            "The system identified conditions that don't meet quality thresholds. "
            "Patience and selectivity are key to long-term success."
        )
        
        context = CopilotAI._explain_context(marker.market_context, marker.technical_details)
        
        risk = (
            f"Current risk level: {marker.risk_level.value}. "
            "Trading in sub-optimal conditions increases probability of losses."
        )
        
        action = (
            "No action required. Continue monitoring. "
            "Better setups will emerge when conditions improve."
        )
        
        learning = (
            "**Key Lesson**: Professional traders spend most of their time waiting. "
            "Discipline to NOT trade is as important as knowing WHEN to trade. "
            "This marker represents avoided risk, which is a form of profit protection."
        )
        
        return {
            "title": title,
            "summary": summary,
            "details": details,
            "context": context,
            "risk": risk,
            "action": action,
            "learning": learning
        }
    
    @staticmethod
    def _explain_pause(marker: MarkerEvent) -> Dict[str, str]:
        """Explain BOT PAUSED marker"""
        
        title = "🛑 Bot Operation Paused"
        summary = marker.reason
        
        details = (
            "The bot has automatically paused trading to protect capital. "
            "This is a risk management protocol, not a system error."
        )
        
        context = "Bot pause is typically triggered by: reaching daily limits, consecutive losses, or manual intervention."
        
        risk = (
            "Risk management protocols are active. "
            "Bot will resume when conditions reset or manual intervention occurs."
        )
        
        action = (
            "Review your trading journal to understand what triggered the pause. "
            "If manual pause, you can resume when ready. "
            "If automatic, wait for daily reset or condition improvement."
        )
        
        learning = (
            "**Key Lesson**: Automated safeguards exist to prevent emotional overtrading. "
            "Pauses are not failures — they're capital preservation in action."
        )
        
        return {
            "title": title,
            "summary": summary,
            "details": details,
            "context": context,
            "risk": risk,
            "action": action,
            "learning": learning
        }
    
    @staticmethod
    def _explain_high_risk(marker: MarkerEvent) -> Dict[str, str]:
        """Explain HIGH RISK marker"""
        
        title = "⚠️ Elevated Risk Conditions"
        summary = marker.reason
        
        details = (
            "Market conditions indicate increased uncertainty or volatility. "
            "While trading is not blocked, extra caution is advised."
        )
        
        context = CopilotAI._explain_context(marker.market_context, marker.technical_details)
        
        risk = (
            f"Risk level: {marker.risk_level.value}. "
            "Consider reducing position size or widening stops if trading during this period."
        )
        
        action = (
            "If you have open positions, monitor them closely. "
            "For new positions, demand higher quality setups before entry."
        )
        
        learning = (
            "**Key Lesson**: Risk is not constant. "
            "Professional traders adjust their approach based on market conditions, "
            "not just individual setups."
        )
        
        return {
            "title": title,
            "summary": summary,
            "details": details,
            "context": context,
            "risk": risk,
            "action": action,
            "learning": learning
        }
    
    @staticmethod
    def _explain_default(marker: MarkerEvent) -> Dict[str, str]:
        """Default explanation"""
        return {
            "title": f"{marker.marker_type.value}",
            "summary": marker.reason,
            "details": "Event recorded for analysis.",
            "context": f"Market context: {marker.market_context.value}",
            "risk": f"Risk level: {marker.risk_level.value}",
            "action": "Review marker details for more information.",
            "learning": ""
        }
    
    # ━━━━━ HELPER BUILDERS ━━━━━
    
    @staticmethod
    def _build_trade_details(marker: MarkerEvent, direction: str) -> str:
        """Build detailed trade explanation"""
        
        tech = marker.technical_details or {}
        
        parts = [marker.reason]
        
        # Add technical context
        if tech.get("prob_buy") and tech.get("prob_sell"):
            prob_buy = tech["prob_buy"]
            prob_sell = tech["prob_sell"]
            parts.append(
                f"Probability analysis: {prob_buy:.1f}% buy vs {prob_sell:.1f}% sell."
            )
        
        if tech.get("trend_strength"):
            strength = tech["trend_strength"]
            if strength > 0.6:
                parts.append("Strong trending conditions support directional trades.")
            elif strength < 0.3:
                parts.append("Ranging conditions — expect mean reversion behavior.")
        
        if tech.get("volatility"):
            vol = tech["volatility"]
            if vol > 0.7:
                parts.append("High volatility — wider stops recommended.")
            elif vol < 0.3:
                parts.append("Low volatility — tighter stops possible.")
        
        return " ".join(parts)
    
    @staticmethod
    def _explain_context(context: MarketContext, tech: dict) -> str:
        """Explain market context in human terms"""
        
        tech = tech or {}
        session = tech.get("session", "UNKNOWN")
        
        context_explanations = {
            MarketContext.TRENDING: (
                f"The market is in a trending phase during {session} session. "
                "Price is showing sustained directional movement, which favors momentum strategies."
            ),
            MarketContext.RANGING: (
                f"The market is range-bound during {session} session. "
                "Price is oscillating between support and resistance levels."
            ),
            MarketContext.VOLATILE: (
                f"The market is experiencing high volatility during {session} session. "
                "Large price swings are occurring — risk management is crucial."
            ),
            MarketContext.LOW_LIQUIDITY: (
                f"Market liquidity is low (session: {session}). "
                "This can lead to wider spreads and less reliable price action."
            ),
            MarketContext.NEWS_WINDOW: (
                "A high-impact news event is expected. "
                "Markets often become unpredictable around major economic releases."
            ),
            MarketContext.UNKNOWN: (
                f"Market structure is unclear during {session} session. "
                "Waiting for more defined conditions."
            )
        }
        
        return context_explanations.get(context, "Market context analysis in progress.")
    
    @staticmethod
    def _explain_risk(risk_level: RiskLevel, sl: float = None, tp: float = None) -> str:
        """Explain risk level and management"""
        
        risk_explanations = {
            RiskLevel.LOW: "Risk conditions are favorable. Standard position sizing appropriate.",
            RiskLevel.MODERATE: "Moderate risk present. Ensure stops are in place.",
            RiskLevel.HIGH: "Elevated risk conditions. Consider reducing position size.",
            RiskLevel.EXTREME: "Extreme risk present. Trading not recommended."
        }
        
        explanation = risk_explanations.get(risk_level, "Risk assessment in progress.")
        
        if sl and tp:
            explanation += f" Stop loss: {sl:.5f}, Take profit: {tp:.5f}."
        
        return explanation
    
    @staticmethod
    def _build_learning_point(marker: MarkerEvent, direction: str) -> str:
        """Build educational takeaway"""
        
        tech = marker.technical_details or {}
        score = marker.score
        
        if score >= 85:
            return (
                "**Key Lesson**: High-quality setups combine multiple confirming factors. "
                "These are the trades worth taking."
            )
        elif score >= 70:
            return (
                "**Key Lesson**: Moderate-quality setups can work but require "
                "stricter risk management and realistic expectations."
            )
        else:
            return (
                "**Key Lesson**: Lower-quality setups have lower probability of success. "
                "Be selective — not every signal deserves capital."
            )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONVERSATIONAL RESPONSES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CopilotChat:
    """
    Conversational AI for user questions about markers.
    
    Example questions:
    - "Why didn't the bot trade here?"
    - "What does this marker mean?"
    - "Is this a good setup?"
    """
    
    @staticmethod
    def answer_question(question: str, marker: MarkerEvent) -> str:
        """
        Answer user questions about specific markers.
        
        This is a simple rule-based system.
        Can be upgraded to LLM-based for richer responses.
        """
        
        question_lower = question.lower()
        explanation = CopilotAI.explain(marker)
        
        # Question routing
        if any(word in question_lower for word in ["why", "reason", "because"]):
            return explanation["details"]
        
        elif any(word in question_lower for word in ["risk", "safe", "dangerous"]):
            return explanation["risk"]
        
        elif any(word in question_lower for word in ["what", "mean", "means"]):
            return explanation["summary"]
        
        elif any(word in question_lower for word in ["should", "do", "action"]):
            return explanation["action"]
        
        elif any(word in question_lower for word in ["learn", "understand", "teach"]):
            return explanation["learning"]
        
        else:
            # Default: provide summary
            return f"{explanation['summary']} {explanation['details']}"
