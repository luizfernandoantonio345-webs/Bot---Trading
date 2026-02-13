"""
╔══════════════════════════════════════════════════════════╗
║      ELITE ORCHESTRATOR — 11 AI ENGINE COORDINATOR       ║
╚══════════════════════════════════════════════════════════╝

Master orchestrator coordinates all 11 AI engines.
Aggregates recommendations into final institutional decision.

ARCHITECTURE:
┌─────────────────────────────────────────────────────────┐
│                   ELITE ORCHESTRATOR                    │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ INPUT LAYER                                        │ │
│  │ • Market Data (M15, H1)                           │ │
│  │ • Bot Signal (BUY/SELL + Strength)               │ │
│  │ • Account State                                   │ │
│  └───────────────────────────────────────────────────┘ │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐ │
│  │ AI ENGINES (11)                                    │ │
│  │  1. ScoreEngine          → Quality Assessment     │ │
│  │  2. RiskEngine           → Risk/Reward Check      │ │
│  │  3. ContextClassifier    → Market Regime          │ │
│  │  4. DecisionEngine       → Aggregation            │ │
│  │  5. CopilotExplainer     → Transparency           │ │
│  │  6. SupervisorEngine     → Health Monitor         │ │
│  │  7. RegimeDetector       → Stability Check        │ │
│  │  8. ConfidenceDecay      → Signal Freshness       │ │
│  │  9. SessionMemory        → Pattern Learning       │ │
│  │ 10. ContrafactualAnalyzer→ Historical Insight     │ │
│  │ 11. CapitalAdvisor       → Preservation           │ │
│  └───────────────────────────────────────────────────┘ │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐ │
│  │ VETO AGGREGATION                                   │ │
│  │ • ANY engine can veto                             │ │
│  │ • Consensus required for execution                │ │
│  │ • "NO TRADE" is valid decision                    │ │
│  └───────────────────────────────────────────────────┘ │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐ │
│  │ OUTPUT LAYER                                       │ │
│  │ • Final Decision (EXECUTE/RECOMMEND/NO_TRADE)     │ │
│  │ • Explanation (Transparent reasoning)             │ │
│  │ • Visual Markers (App display)                    │ │
│  │ • Event Logging (Audit trail)                     │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

PRINCIPLES:
- Any engine can VETO
- Human maintains final control
- Transparency mandatory
- Capital preservation priority
- Long-term consistency over short-term gains
"""

import pandas as pd
from typing import Dict, Optional
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from safety import get_safety_monitor, TradingMode

# Import all AI engines
from ai_engines.score_engine import ScoreEngine
from ai_engines.risk_engine import RiskEngine
from ai_engines.context_classifier import MarketContextClassifier
from ai_engines.decision_engine import DecisionEngine
from ai_engines.copilot_explainer import CopilotExplainer
from ai_engines.supervisor_engine import SupervisorEngine
from ai_engines.regime_detector import (
    RegimeShiftDetector,
    ConfidenceDecayEngine,
    SessionMemoryEngine,
    ContrafactualAnalyzer,
    CapitalPreservationAdvisor
)


class EliteOrchestrator:
    """
    Coordinates all 11 AI engines for institutional-grade decisions.
    
    RESPONSIBILITY:
    - Collect inputs from all engines
    - Aggregate recommendations
    - Handle vetos
    - Generate final decision + explanation
    - Emit markers for app visualization
    
    GUARANTEES:
    - Any engine can veto
    - All vetos respected
    - Full transparency
    - Capital preservation priority
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        
        # Initialize all 11 AI engines
        self.score_engine = ScoreEngine()
        self.risk_engine = RiskEngine()
        self.context_classifier = MarketContextClassifier()
        self.decision_engine = DecisionEngine()
        self.copilot_explainer = CopilotExplainer()
        self.supervisor = SupervisorEngine()
        self.regime_detector = RegimeShiftDetector()
        self.confidence_decay = ConfidenceDecayEngine()
        self.session_memory = SessionMemoryEngine()
        self.contrafactual = ContrafactualAnalyzer()
        self.capital_advisor = CapitalPreservationAdvisor()
        
        self.safety = get_safety_monitor()
        
        print("🏛️ Elite Orchestrator initialized with 11 AI engines")
    
    def process_signal(
        self,
        signal_direction: str,
        signal_strength: float,
        price: float,
        stop_loss: float,
        take_profit: float,
        df_m15: pd.DataFrame,
        df_h1: pd.DataFrame,
        account_balance: float,
        session: str,
        is_news_window: bool
    ) -> Dict:
        """
        Process trading signal through all 11 AI engines.
        
        Returns comprehensive decision with explanation and markers.
        """
        
        print(f"\n{'='*60}")
        print(f"ELITE DECISION PROCESS — {signal_direction} Signal")
        print(f"{'='*60}")
        
        # ─────────────────────────────────────────────────────────
        # PHASE 1: DATA COLLECTION
        # ─────────────────────────────────────────────────────────
        
        # Calculate technical factors (simplified - use your real indicators)
        trend_alignment = self._calculate_trend_alignment(df_h1)
        momentum_strength = signal_strength
        volatility_context = "MODERATE"  # From ATR analysis
        volume_confirmation = 0.7  # From volume analysis
        sr_proximity = 0.15  # Distance to support/resistance
        
        # ─────────────────────────────────────────────────────────
        # PHASE 2: AI ENGINE EVALUATION
        # ─────────────────────────────────────────────────────────
        
        # Engine #1: Score Quality
        print("\n[1/11] ScoreEngine evaluating...")
        score_result = self.score_engine.evaluate(
            trend_alignment=trend_alignment,
            momentum_strength=momentum_strength,
            volatility_context=volatility_context,
            volume_confirmation=volume_confirmation,
            support_resistance_proximity=sr_proximity,
            session_timing=session
        )
        print(f"  → Score: {score_result.score:.1f}/100 ({score_result.quality})")
        if score_result.veto:
            print(f"  → VETO: {score_result.veto_reason}")
        
        # Engine #2: Risk Assessment
        print("\n[2/11] RiskEngine assessing...")
        risk_assessment = self.risk_engine.assess(
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            account_balance=account_balance,
            direction=signal_direction
        )
        print(f"  → R:R = {risk_assessment.risk_reward_ratio:.2f}:1")
        print(f"  → Position Size: {risk_assessment.position_size:.3f} lots")
        if risk_assessment.veto:
            print(f"  → VETO: {risk_assessment.veto_reason}")
        
        # Engine #3: Market Context
        print("\n[3/11] ContextClassifier analyzing...")
        context_classification = self.context_classifier.classify(
            df_m15=df_m15,
            df_h1=df_h1,
            current_session=session,
            is_news_window=is_news_window
        )
        print(f"  → Regime: {context_classification.regime.value}")
        print(f"  → Tradability: {context_classification.tradability.value}")
        if context_classification.veto:
            print(f"  → VETO: {context_classification.veto_reason}")
        
        # Engine #4: Supervisor
        print("\n[4/11] SupervisorEngine monitoring...")
        recent_performance = {
            'win_rate': 0.6,  # Get from actual performance tracking
            'trade_count': len(self.supervisor.recent_trades)
        }
        supervisor_status = self.supervisor.assess(
            recent_performance=recent_performance,
            error_count=len(self.supervisor.recent_errors),
            total_operations=100  # Track actual
        )
        print(f"  → Health Score: {supervisor_status.health_score:.2f}")
        if supervisor_status.should_pause:
            print(f"  → PAUSE RECOMMENDED: {supervisor_status.reason}")
        
        # Engine #5: Regime Stability
        print("\n[5/11] RegimeDetector checking...")
        regime_analysis = self.regime_detector.analyze(
            df_h1=df_h1,
            current_regime=context_classification.regime.value
        )
        print(f"  → Regime Stable: {regime_analysis['regime_stable']}")
        if regime_analysis['veto']:
            print(f"  → VETO: {regime_analysis['veto_reason']}")
        
        # Engine #6: Signal Freshness
        print("\n[6/11] ConfidenceDecay evaluating...")
        self.confidence_decay.set_signal(score_result.confidence)
        confidence_analysis = self.confidence_decay.get_current_confidence()
        print(f"  → Confidence: {confidence_analysis['confidence']:.2f}")
        if confidence_analysis['veto']:
            print(f"  → VETO: {confidence_analysis['veto_reason']}")
        
        # Engine #7: Session Memory
        print("\n[7/11] SessionMemory checking patterns...")
        memory_context = self.session_memory.analyze_pattern(
            proposed_setup_type=f"{signal_direction}_{context_classification.regime.value}",
            proposed_regime=context_classification.regime.value,
            proposed_score=score_result.score
        )
        if memory_context['veto']:
            print(f"  → VETO: {memory_context['veto_reason']}")
        
        # Engine #8: Contrafactual
        print("\n[8/11] ContrafactualAnalyzer reviewing history...")
        entry_conditions = {
            'direction': signal_direction,
            'regime': context_classification.regime.value,
            'score': score_result.score,
            'volatility': volatility_context
        }
        contrafactual_analysis = self.contrafactual.analyze_proposal(entry_conditions)
        if contrafactual_analysis['veto']:
            print(f"  → VETO: {contrafactual_analysis['veto_reason']}")
        
        # Engine #9: Capital Preservation
        print("\n[9/11] CapitalAdvisor advising...")
        capital_advice = self.capital_advisor.advise(
            current_balance=account_balance,
            daily_loss=self.safety.daily_loss,
            consecutive_losses=self.safety.consecutive_losses,
            open_risk=risk_assessment.risk_amount
        )
        print(f"  → Recommendation: {capital_advice['recommendation']}")
        if capital_advice['veto']:
            print(f"  → VETO: {capital_advice['veto_reason']}")
        
        # ─────────────────────────────────────────────────────────
        # PHASE 3: DECISION AGGREGATION
        # ─────────────────────────────────────────────────────────
        
        print("\n[10/11] DecisionEngine aggregating...")
        mode = self.safety.mode
        
        final_decision = self.decision_engine.aggregate_decision(
            mode=mode,
            score_result=score_result,
            risk_assessment=risk_assessment,
            context_classification=context_classification,
            regime_analysis=regime_analysis,
            confidence_analysis=confidence_analysis,
            memory_context=memory_context,
            contrafactual_analysis=contrafactual_analysis,
            capital_advice=capital_advice,
            supervisor_status={'should_pause': supervisor_status.should_pause, 'reason': supervisor_status.reason},
            signal_direction=signal_direction,
            signal_strength=signal_strength
        )
        
        print(f"\n→ FINAL DECISION: {final_decision.decision_type.value}")
        print(f"→ Can Execute: {final_decision.can_execute}")
        print(f"→ Veto Count: {final_decision.veto_count}")
        
        # ─────────────────────────────────────────────────────────
        # PHASE 4: EXPLANATION GENERATION
        # ─────────────────────────────────────────────────────────
        
        print("\n[11/11] CopilotExplainer generating explanation...")
        explanation = self.copilot_explainer.explain_decision(
            final_decision=final_decision,
            score_result=score_result,
            risk_assessment=risk_assessment,
            context_classification=context_classification,
            all_engine_inputs={
                'supervisor': supervisor_status,
                'regime': regime_analysis,
                'confidence': confidence_analysis,
                'memory': memory_context,
                'contrafactual': contrafactual_analysis,
                'capital': capital_advice
            }
        )
        
        print(f"\n{'='*60}")
        print(f"DECISION COMPLETE")
        print(f"{'='*60}\n")
        
        return {
            'decision': final_decision,
            'explanation': explanation,
            'score': score_result,
            'risk': risk_assessment,
            'context': context_classification
        }
    
    def _calculate_trend_alignment(self, df_h1: pd.DataFrame) -> float:
        """Calculate trend alignment (-1 to +1)"""
        if len(df_h1) < 50:
            return 0.0
        
        close = df_h1['close']
        ema_20 = close.ewm(span=20).mean()
        ema_50 = close.ewm(span=50).mean()
        
        # Simple alignment metric
        if ema_20.iloc[-1] > ema_50.iloc[-1]:
            # Uptrend
            slope = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20]
            return min(max(slope * 100, 0), 1.0)
        else:
            # Downtrend
            slope = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20]
            return max(min(slope * 100, 0), -1.0)
    
    def get_system_status(self) -> Dict:
        """Get status of all 11 engines"""
        return {
            'orchestrator': 'EliteOrchestrator',
            'version': '1.0.0',
            'engines': {
                '1_score': self.score_engine.get_status(),
                '2_risk': self.risk_engine.get_status(),
                '3_context': self.context_classifier.get_status(),
                '4_decision': self.decision_engine.get_status(),
                '5_explainer': self.copilot_explainer.get_status(),
                '6_supervisor': self.supervisor.get_status(),
                '7_regime': {'name': 'RegimeDetector', 'active': True},
                '8_confidence': {'name': 'ConfidenceDecay', 'active': True},
                '9_memory': {'name': 'SessionMemory', 'active': True},
                '10_contrafactual': {'name': 'Contrafactual', 'active': True},
                '11_capital': {'name': 'CapitalAdvisor', 'active': True}
            },
            'safety': self.safety.get_status()
        }
