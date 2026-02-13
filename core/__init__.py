"""
Core package - Trading Bot Professional
"""

__version__ = "2.0.0"  # Versão com camadas 10-20
__author__ = "Trading Bot Team"

# Importações principais (Camadas 1-9)
from .market_analyzer import MarketAnalyzer
from .pattern_engine import PatternEngine
from .score_engine import ScoreEngine, ScoreWeights, ScoreResult
from .risk_manager import RiskManager, RiskLimits, RiskMetrics
from .execution_engine import BinanceExecutor, OrderSide, OrderType
from .memory_engine import MemoryEngine, TradeRecord
from .learning_engine import LearningEngine
from .logger import get_logger

# Importações avançadas (Camadas 10-20)
from .self_evaluator import SelfEvaluator
from .attention_model import ContextualAttentionModel
from .similarity_matcher import SimilarityMatcher
from .advanced_layers_1315 import StrategyEnsemble, AnomalyDetector, TemporalController
from .advanced_layers_1620 import CrowdIntelligence, ResilienceEngine, SecondOrderExplainer, InternalSimulator, FutureReadiness

__all__ = [
    # Camadas 1-9
    'MarketAnalyzer',
    'PatternEngine',
    'ScoreEngine',
    'ScoreWeights',
    'ScoreResult',
    'RiskManager',
    'RiskLimits',
    'RiskMetrics',
    'BinanceExecutor',
    'OrderSide',
    'OrderType',
    'MemoryEngine',
    'TradeRecord',
    'LearningEngine',
    'get_logger',
    # Camadas 10-20
    'SelfEvaluator',
    'ContextualAttentionModel',
    'SimilarityMatcher',
    'StrategyEnsemble',
    'AnomalyDetector',
    'TemporalController',
    'CrowdIntelligence',
    'ResilienceEngine',
    'SecondOrderExplainer',
    'InternalSimulator',
    'FutureReadiness'
]
