"""
╔══════════════════════════════════════════════════════════╗
║       ELITE AI ENGINES — INSTITUTIONAL SYSTEM            ║
╚══════════════════════════════════════════════════════════╝

11 specialized AI engines for institutional-grade decisions.
Each engine has LIMITED, CLEAR responsibility.
Any engine can VETO execution.

PHILOSOPHY:
- "NOT TRADING" is a high-value decision
- Fewer trades > More trades
- Capital preserved > Capital exposed
- Predictability > Complexity
- Long-term consistency > Short-term gain
"""

from .score_engine import ScoreEngine
from .risk_engine import RiskEngine
from .context_classifier import MarketContextClassifier
from .decision_engine import DecisionEngine
from .copilot_explainer import CopilotExplainer
from .supervisor_engine import SupervisorEngine
from .regime_detector import (
    RegimeShiftDetector,
    ConfidenceDecayEngine,
    SessionMemoryEngine,
    ContrafactualAnalyzer,
    CapitalPreservationAdvisor
)

__all__ = [
    'ScoreEngine',
    'RiskEngine',
    'MarketContextClassifier',
    'DecisionEngine',
    'CopilotExplainer',
    'SupervisorEngine',
    'RegimeShiftDetector',
    'ConfidenceDecayEngine',
    'SessionMemoryEngine',
    'ContrafactualAnalyzer',
    'CapitalPreservationAdvisor'
]
