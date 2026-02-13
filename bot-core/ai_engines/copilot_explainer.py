"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI ENGINE #5: COPILOT EXPLAINER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESPONSIBILITY:
Generate human-readable explanations for all decisions.
Make AI reasoning transparent and educational.

CAN VETO IF:
- Never (explanation engine doesn't veto)

CANNOT:
- Block trades (explanation only)
- Promise profits
- Provide financial advice
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class Explanation:
    """Human-readable explanation"""
    title: str
    summary: str
    what_happened: str
    why_this_decision: str
    what_engines_said: Dict[str, str]
    risk_context: str
    educational_note: str
    confidence_level: str


class CopilotExplainer:
    """
    Generates transparent explanations for all decisions.
    
    PRINCIPLES:
    - Transparency builds trust
    - Education over prediction
    - Never promise outcomes
    - Show ALL engine inputs
    - Explain WHY NOT TO TRADE when applicable
    """
    
    def __init__(self):
        self.name = "CopilotExplainer"
        self.version = "1.0.0"
    
    def explain_decision(
        self,
        final_decision,
        score_result,
        risk_assessment,
        context_classification,
        all_engine_inputs: Dict
    ) -> Explanation:
        """
        Generate comprehensive explanation for decision.
        """
        
        # Title
        if final_decision.decision_type.value.startswith("EXECUTE"):
            title = f"✅ Trade Execution: {final_decision.direction}"
        elif final_decision.decision_type.value.startswith("RECOMMEND"):
            title = f"💡 Trade Recommendation: {final_decision.direction}"
        elif final_decision.decision_type == "NO_TRADE":
            title = "🚫 No Trade - Conditions Not Met"
        else:
            title = "⏸️ Bot Paused"
        
        # Summary
        summary = self._generate_summary(final_decision, score_result)
        
        # What happened
        what_happened = self._describe_market_state(context_classification, score_result)
        
        # Why this decision
        why_this_decision = self._explain_decision_logic(final_decision, score_result, risk_assessment)
        
        # What engines said
        what_engines_said = self._explain_engine_votes(final_decision.engine_votes, all_engine_inputs)
        
        # Risk context
        risk_context = self._explain_risk_context(risk_assessment, final_decision)
        
        # Educational note
        educational_note = self._generate_educational_note(final_decision, context_classification)
        
        # Confidence level
        confidence_level = self._describe_confidence(final_decision.confidence)
        
        return Explanation(
            title=title,
            summary=summary,
            what_happened=what_happened,
            why_this_decision=why_this_decision,
            what_engines_said=what_engines_said,
            risk_context=risk_context,
            educational_note=educational_note,
            confidence_level=confidence_level
        )
    
    def _generate_summary(self, decision, score_result) -> str:
        """Generate one-sentence summary"""
        
        if decision.decision_type == "NO_TRADE":
            if decision.veto_count > 0:
                return f"{decision.veto_count} AI engine(s) determined conditions are not suitable for trading."
            else:
                return "Market analysis suggests waiting for better opportunity."
        
        elif decision.decision_type.value.startswith("EXECUTE"):
            return f"High-quality setup detected (Score: {score_result.score:.1f}/100). Execution approved."
        
        elif decision.decision_type.value.startswith("RECOMMEND"):
            return f"Potential opportunity identified (Score: {score_result.score:.1f}/100). Human review recommended."
        
        else:
            return "Bot paused for safety reasons."
    
    def _describe_market_state(self, context_classification, score_result) -> str:
        """Describe what's happening in the market"""
        
        regime = context_classification.regime.value.replace("_", " ").title()
        volatility = context_classification.volatility_level.lower()
        liquidity = context_classification.liquidity_level.lower()
        session = context_classification.session
        
        description = f"Market is {regime.lower()} with {volatility} volatility and {liquidity} liquidity during {session} session. "
        description += f"Technical setup quality rated {score_result.quality} based on {len(score_result.components)} indicators."
        
        return description
    
    def _explain_decision_logic(self, decision, score_result, risk_assessment) -> str:
        """Explain why this decision was made"""
        
        if decision.decision_type == "NO_TRADE":
            if len(decision.veto_reasons) > 0:
                reasons = "; ".join(decision.veto_reasons[:3])  # Top 3 reasons
                return f"Trading blocked because: {reasons}. This is a protective decision - not trading in poor conditions is often the best trade."
            else:
                return "While setup shows some potential, overall conditions don't meet our quality threshold. Patience preserves capital."
        
        elif decision.decision_type.value.startswith("EXECUTE"):
            return f"All {len(decision.engine_votes)} AI engines approved this setup. Score of {score_result.score:.1f} exceeds execution threshold. Risk/reward ratio of {risk_assessment.risk_reward_ratio:.2f}:1 is acceptable. Mode permits automatic execution."
        
        elif decision.decision_type.value.startswith("RECOMMEND"):
            return f"Setup meets quality threshold (Score: {score_result.score:.1f}) but {decision.execution_reason}. Human review adds valuable oversight for borderline setups."
        
        else:
            return decision.execution_reason
    
    def _explain_engine_votes(self, engine_votes: Dict, all_inputs: Dict) -> Dict[str, str]:
        """Explain what each engine said"""
        
        explanations = {}
        
        for engine, vote in engine_votes.items():
            if vote == "APPROVE":
                explanations[engine] = self._get_approval_reason(engine, all_inputs)
            else:
                explanations[engine] = self._get_veto_reason(engine, all_inputs)
        
        return explanations
    
    def _get_approval_reason(self, engine: str, inputs: Dict) -> str:
        """Get approval reason for engine"""
        
        reasons = {
            'ScoreEngine': "Setup quality meets standards",
            'RiskEngine': "Risk parameters acceptable",
            'ContextClassifier': "Market conditions suitable",
            'RegimeDetector': "No regime shift detected",
            'ConfidenceDecay': "Confidence level sufficient",
            'SessionMemory': "Recent performance supports trade",
            'Contrafactual': "Similar past setups were successful",
            'CapitalAdvisor': "Capital preservation not triggered"
        }
        
        return reasons.get(engine, "Approved")
    
    def _get_veto_reason(self, engine: str, inputs: Dict) -> str:
        """Get veto reason from inputs"""
        # Extract from inputs if available
        return f"{engine} determined conditions unsuitable"
    
    def _explain_risk_context(self, risk_assessment, decision) -> str:
        """Explain risk context in plain language"""
        
        if decision.decision_type == "NO_TRADE":
            return "No risk exposure - capital preserved."
        
        if risk_assessment.veto:
            return f"Risk check failed: {risk_assessment.veto_reason}. This protects you from unfavorable risk/reward scenarios."
        
        rr = risk_assessment.risk_reward_ratio
        risk_amt = risk_assessment.risk_amount
        position_size = risk_assessment.position_size
        
        context = f"Risking ${risk_amt:.2f} for potential reward of ${risk_amt * rr:.2f} (R:R = {rr:.2f}:1). "
        context += f"Position size: {position_size:.3f} lots. "
        
        if len(risk_assessment.warnings) > 0:
            context += f"Notes: {'; '.join(risk_assessment.warnings)}"
        
        return context
    
    def _generate_educational_note(self, decision, context_classification) -> str:
        """Generate educational insight"""
        
        if decision.decision_type == "NO_TRADE":
            notes = [
                "Not trading is an active decision. Professional traders spend most time waiting for optimal setups.",
                "Preservation of capital is the foundation of long-term success. Missing one trade is better than taking a bad one.",
                "Markets reward patience. The best trades come to those who wait for genuine high-probability setups.",
                "Trading discipline means saying 'no' more often than 'yes'. This protects your capital for truly exceptional opportunities."
            ]
            import random
            return random.choice(notes)
        
        elif context_classification.regime.value.startswith("TRENDING"):
            return "Trending markets offer clearer directional bias. However, risk management remains crucial - even in strong trends, pullbacks occur."
        
        elif context_classification.tradability.value in ["POOR", "UNTRADEABLE"]:
            return "Choppy or low-liquidity conditions increase risk of false signals and slippage. Waiting for better conditions is often the professional choice."
        
        else:
            return "Every trade carries risk. Position sizing and stop loss placement are your primary capital protection tools."
    
    def _describe_confidence(self, confidence: float) -> str:
        """Describe confidence level in human terms"""
        
        if confidence >= 0.9:
            return "Very High - Strong agreement across all indicators"
        elif confidence >= 0.75:
            return "High - Good confluence of factors"
        elif confidence >= 0.6:
            return "Moderate - Acceptable but not ideal"
        elif confidence >= 0.4:
            return "Low - Conflicting signals present"
        else:
            return "Very Low - High uncertainty"
    
    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            'name': self.name,
            'version': self.version,
            'active': True
        }
