"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI ENGINE #4: DECISION ENGINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESPONSIBILITY:
Aggregate all AI engines and make final recommendation.
Respect mode (HYBRID vs AUTO).

CAN VETO IF:
- Any engine vetoed
- Consensus insufficient
- Mode restrictions apply

CANNOT:
- Override vetos from other engines
- Execute without mode permission
- Ignore safety rules
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from safety import TradingMode


class DecisionType(str, Enum):
    """Decision types"""
    EXECUTE_BUY = "EXECUTE_BUY"
    EXECUTE_SELL = "EXECUTE_SELL"
    RECOMMEND_BUY = "RECOMMEND_BUY"
    RECOMMEND_SELL = "RECOMMEND_SELL"
    NO_TRADE = "NO_TRADE"
    PAUSE = "PAUSE"


@dataclass
class FinalDecision:
    """Final aggregated decision"""
    decision_type: DecisionType
    direction: Optional[str]
    can_execute: bool
    execution_reason: str
    score: float
    confidence: float
    veto_count: int
    veto_reasons: List[str]
    engine_votes: Dict[str, str]


class DecisionEngine:
    """
    Aggregates all AI engine inputs and makes final decision.
    
    PRINCIPLES:
    - ANY engine can veto
    - Mode determines execution vs recommendation
    - Consensus required for execution
    - "NO TRADE" is a valid decision
    """
    
    def __init__(self):
        self.name = "DecisionEngine"
        self.version = "1.0.0"
    
    def aggregate_decision(
        self,
        mode: TradingMode,
        score_result,
        risk_assessment,
        context_classification,
        regime_analysis,
        confidence_analysis,
        memory_context,
        contrafactual_analysis,
        capital_advice,
        supervisor_status,
        signal_direction: str,
        signal_strength: float
    ) -> FinalDecision:
        """
        Aggregate all AI engine inputs into final decision.
        
        Args:
            mode: Trading mode (HYBRID/AUTO/NO_TRADE)
            score_result: ScoreEngine result
            risk_assessment: RiskEngine result
            context_classification: MarketContextClassifier result
            regime_analysis: RegimeShiftDetector result
            confidence_analysis: ConfidenceDecayEngine result
            memory_context: SessionMemoryEngine result
            contrafactual_analysis: ContrafactualAnalyzer result
            capital_advice: CapitalPreservationAdvisor result
            supervisor_status: SupervisorEngine status
            signal_direction: BUY or SELL
            signal_strength: 0-1
        
        Returns:
            FinalDecision with aggregated recommendation
        """
        
        # Collect vetos
        vetos = []
        engine_votes = {}
        
        # 1. Check NO_TRADE mode
        if mode == TradingMode.NO_TRADE:
            return self._no_trade_decision("Mode is NO_TRADE")
        
        # 2. Check Supervisor
        if supervisor_status.get('should_pause', False):
            return self._pause_decision(supervisor_status.get('reason', 'Supervisor pause'))
        
        # 3. Score Engine
        if score_result.veto:
            vetos.append(f"ScoreEngine: {score_result.veto_reason}")
            engine_votes['ScoreEngine'] = 'VETO'
        else:
            engine_votes['ScoreEngine'] = 'APPROVE'
        
        # 4. Risk Engine
        if risk_assessment.veto:
            vetos.append(f"RiskEngine: {risk_assessment.veto_reason}")
            engine_votes['RiskEngine'] = 'VETO'
        else:
            engine_votes['RiskEngine'] = 'APPROVE'
        
        # 5. Context Classifier
        if context_classification.veto:
            vetos.append(f"ContextClassifier: {context_classification.veto_reason}")
            engine_votes['ContextClassifier'] = 'VETO'
        else:
            engine_votes['ContextClassifier'] = 'APPROVE'
        
        # 6. Regime Detector
        if regime_analysis.get('veto', False):
            vetos.append(f"RegimeDetector: {regime_analysis.get('veto_reason', 'Regime shift detected')}")
            engine_votes['RegimeDetector'] = 'VETO'
        else:
            engine_votes['RegimeDetector'] = 'APPROVE'
        
        # 7. Confidence Decay
        if confidence_analysis.get('veto', False):
            vetos.append(f"ConfidenceDecay: {confidence_analysis.get('veto_reason', 'Confidence too low')}")
            engine_votes['ConfidenceDecay'] = 'VETO'
        else:
            engine_votes['ConfidenceDecay'] = 'APPROVE'
        
        # 8. Session Memory
        if memory_context.get('veto', False):
            vetos.append(f"SessionMemory: {memory_context.get('veto_reason', 'Recent pattern suggests caution')}")
            engine_votes['SessionMemory'] = 'VETO'
        else:
            engine_votes['SessionMemory'] = 'APPROVE'
        
        # 9. Contrafactual Analyzer
        if contrafactual_analysis.get('veto', False):
            vetos.append(f"Contrafactual: {contrafactual_analysis.get('veto_reason', 'Similar past trades failed')}")
            engine_votes['Contrafactual'] = 'VETO'
        else:
            engine_votes['Contrafactual'] = 'APPROVE'
        
        # 10. Capital Preservation
        if capital_advice.get('veto', False):
            vetos.append(f"CapitalAdvisor: {capital_advice.get('veto_reason', 'Capital preservation required')}")
            engine_votes['CapitalAdvisor'] = 'VETO'
        else:
            engine_votes['CapitalAdvisor'] = 'APPROVE'
        
        # ANY VETO = NO TRADE
        if len(vetos) > 0:
            return FinalDecision(
                decision_type=DecisionType.NO_TRADE,
                direction=None,
                can_execute=False,
                execution_reason=f"{len(vetos)} engine(s) vetoed",
                score=score_result.score,
                confidence=0.0,
                veto_count=len(vetos),
                veto_reasons=vetos,
                engine_votes=engine_votes
            )
        
        # All engines approved - determine execution level
        overall_confidence = self._calculate_overall_confidence(
            score_result.confidence,
            confidence_analysis.get('confidence', 0.5),
            context_classification.confidence
        )
        
        # Mode-based decision
        if mode == TradingMode.HYBRID:
            # HYBRID: Always recommend, never execute
            decision_type = DecisionType.RECOMMEND_BUY if signal_direction == "BUY" else DecisionType.RECOMMEND_SELL
            can_execute = False
            reason = "HYBRID mode: Human confirmation required"
        
        elif mode == TradingMode.AUTO:
            # AUTO: Execute if score high enough
            if score_result.score >= 90.0 and overall_confidence >= 0.8:
                decision_type = DecisionType.EXECUTE_BUY if signal_direction == "BUY" else DecisionType.EXECUTE_SELL
                can_execute = True
                reason = f"AUTO mode: Score {score_result.score:.1f}, Confidence {overall_confidence:.2f}"
            else:
                decision_type = DecisionType.RECOMMEND_BUY if signal_direction == "BUY" else DecisionType.RECOMMEND_SELL
                can_execute = False
                reason = f"Score/confidence insufficient for auto-execution (Score: {score_result.score:.1f}, Conf: {overall_confidence:.2f})"
        
        else:
            return self._no_trade_decision(f"Unknown mode: {mode}")
        
        return FinalDecision(
            decision_type=decision_type,
            direction=signal_direction,
            can_execute=can_execute,
            execution_reason=reason,
            score=score_result.score,
            confidence=overall_confidence,
            veto_count=0,
            veto_reasons=[],
            engine_votes=engine_votes
        )
    
    def _calculate_overall_confidence(
        self,
        score_confidence: float,
        decay_confidence: float,
        context_confidence: float
    ) -> float:
        """Calculate overall confidence from multiple sources"""
        # Weighted average
        weights = [0.4, 0.3, 0.3]  # Score, Decay, Context
        confidences = [score_confidence, decay_confidence, context_confidence]
        
        overall = sum(w * c for w, c in zip(weights, confidences))
        return overall
    
    def _no_trade_decision(self, reason: str) -> FinalDecision:
        """Create NO_TRADE decision"""
        return FinalDecision(
            decision_type=DecisionType.NO_TRADE,
            direction=None,
            can_execute=False,
            execution_reason=reason,
            score=0.0,
            confidence=0.0,
            veto_count=1,
            veto_reasons=[reason],
            engine_votes={}
        )
    
    def _pause_decision(self, reason: str) -> FinalDecision:
        """Create PAUSE decision"""
        return FinalDecision(
            decision_type=DecisionType.PAUSE,
            direction=None,
            can_execute=False,
            execution_reason=reason,
            score=0.0,
            confidence=0.0,
            veto_count=1,
            veto_reasons=[reason],
            engine_votes={}
        )
    
    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            'name': self.name,
            'version': self.version,
            'active': True
        }
