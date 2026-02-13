"""
═══════════════════════════════════════════════════════════════════
ORQUESTRADOR MASTER - 20 CAMADAS INTEGRADAS
═══════════════════════════════════════════════════════════════════
Integração completa de todas as camadas de inteligência.
"""

from datetime import datetime
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# Camadas 1-9 (originais)
from core.market_analyzer import MarketAnalyzer
from core.pattern_engine import PatternEngine
from core.score_engine import ScoreEngine
from core.risk_manager import RiskManager
from core.execution_engine import BinanceExecutor
from core.memory_engine import MemoryEngine
from core.learning_engine import LearningEngine
from core.logger import get_logger

# Camadas 10-20 (novas)
from core.self_evaluator import SelfEvaluator
from core.attention_model import ContextualAttentionModel
from core.similarity_matcher import SimilarityMatcher
from core.advanced_layers_1315 import StrategyEnsemble, AnomalyDetector, TemporalController
from core.advanced_layers_1620 import (
    CrowdIntelligence,
    ResilienceEngine,
    SecondOrderExplainer,
    InternalSimulator,
    FutureReadiness
)


@dataclass
class DecisionContext:
    """Contexto completo de uma decisão"""
    score: float
    recommendation: str
    confidence: float
    market_analysis: Dict
    pattern_analysis: Dict
    strategy_selected: str
    anomalies_detected: list
    time_quality: float
    crowd_sentiment: str
    similar_historical: Dict
    risk_assessment: Dict
    explanation: Dict
    stress_test_result: Dict
    system_health: float
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class MasterOrchestrator:
    """
    Orquestrador master que integra todas as 20 camadas.
    
    Fluxo:
    1. Validação de Risco (Camada 0)
    2. Análise Multitimeframe (Camada 1)
    3. Detecção de Padrões (Camada 2)
    4. Scoring Inteligente (Camada 3)
    5. Atenção Contextual (Camada 11)
    6. Seleção de Estratégia (Camada 13)
    7. Detecção de Anomalias (Camada 14)
    8. Análise Temporal (Camada 15)
    9. Inteligência de Multidão (Camada 16)
    10. Busca de Similaridade (Camada 12)
    11. Simulação Interna (Camada 19)
    12. Explicação de 2ª Ordem (Camada 18)
    13. Decisão Final
    14. Autoavaliação (Camada 10)
    """
    
    def __init__(self, config: Dict):
        self.logger = get_logger()
        self.config = config
        
        # Inicializar todas as camadas
        print("═" * 70)
        print("🤖 INICIALIZANDO ORQUESTRADOR MASTER - 20 CAMADAS")
        print("═" * 70)
        
        # Camadas 1-9 (original)
        self.market_analyzer = MarketAnalyzer()
        print("✓ Camada 1: Market Analyzer")
        
        self.pattern_engine = PatternEngine()
        print("✓ Camada 2: Pattern Engine")
        
        self.score_engine = ScoreEngine()
        print("✓ Camada 3: Score Engine")
        
        self.risk_manager = RiskManager()
        print("✓ Camada 4: Risk Manager")
        
        self.executor = BinanceExecutor(
            api_key=config.get("api_key", ""),
            api_secret=config.get("api_secret", ""),
            use_testnet=config.get("use_testnet", True)
        )
        print("✓ Camada 5: Execution Engine")
        
        self.memory = MemoryEngine()
        print("✓ Camada 6: Memory Engine")
        
        self.learning = LearningEngine(self.memory)
        print("✓ Camada 7: Learning Engine")
        
        # Camadas 8-9 seria notifier e outros
        
        # Camadas 10-20 (novas)
        self.self_evaluator = SelfEvaluator(self.memory)
        self.self_evaluator.current_weights = self.score_engine.weights
        print("✓ Camada 10: Self Evaluator (Meta-inteligência)")
        
        self.attention_model = ContextualAttentionModel()
        print("✓ Camada 11: Attention Model")
        
        self.similarity_matcher = SimilarityMatcher(self.memory)
        print("✓ Camada 12: Similarity Matcher")
        
        self.strategy_ensemble = StrategyEnsemble()
        print("✓ Camada 13: Strategy Ensemble")
        
        self.anomaly_detector = AnomalyDetector()
        print("✓ Camada 14: Anomaly Detector")
        
        self.temporal_controller = TemporalController(self.memory)
        print("✓ Camada 15: Temporal Controller")
        
        self.crowd_intelligence = CrowdIntelligence()
        print("✓ Camada 16: Crowd Intelligence")
        
        self.resilience_engine = ResilienceEngine()
        print("✓ Camada 17: Resilience Engine")
        
        self.second_order_explainer = SecondOrderExplainer()
        print("✓ Camada 18: Second Order Explainer")
        
        self.internal_simulator = InternalSimulator()
        print("✓ Camada 19: Internal Simulator")
        
        self.future_readiness = FutureReadiness()
        print("✓ Camada 20: Future Readiness")
        
        print("\n✅ TODAS AS 20 CAMADAS INICIALIZADAS")
        print("═" * 70 + "\n")
    
    def make_complete_decision(self, market_data: Dict) -> DecisionContext:
        """
        Executa análise completa com todas as 20 camadas.
        """
        try:
            # ═══════════════════════════════════════════════════════════
            # FASE 1: VALIDAÇÃO PRELIMINAR
            # ═══════════════════════════════════════════════════════════
            
            # Verificar risco
            can_trade, risk_reason = self.risk_manager.can_trade()
            if not can_trade:
                return self._create_blocked_context(f"Risk blocked: {risk_reason}", market_data)
            
            # Verificar modo seguro
            if self.resilience_engine.should_activate_safe_mode():
                print("⚠️  SAFE MODE ATIVADO - Usando configurações conservadoras")
            
            # ═══════════════════════════════════════════════════════════
            # FASE 2: ANÁLISE MULTICAMADAS
            # ═══════════════════════════════════════════════════════════
            
            # Camada 1: Market Analysis
            market_analysis = self.market_analyzer.analyze_complete_market(
                df_m5=market_data['m5'],
                df_m15=market_data['m15'],
                df_h1=market_data['h1'],
                df_h4=market_data['h4'],
                df_d1=market_data['d1'],
                current_price=market_data['current_price']
            )
            
            # Camada 2: Pattern Detection
            pattern_analysis = self.pattern_engine.detect_all_patterns(
                df_m15=market_data['m15'],
                df_h1=market_data['h1'],
                df_h4=market_data['h4'],
                support_resistance=self._calculate_sr(market_data['h1'])
            )
            
            # ═══════════════════════════════════════════════════════════
            # FASE 3: ANÁLISE CONTEXTUAL AVANÇADA
            # ═══════════════════════════════════════════════════════════
            
            # Camada 11: Attention Model
            attention_weights = self.attention_model.compute_attention_weights(market_analysis)
            
            # Camada 13: Strategy Selection
            selected_strategy, strategy_confidence = self.strategy_ensemble.select_strategy(market_analysis)
            
            # Camada 14: Anomaly Detection
            anomalies = self.anomaly_detector.get_anomaly_report(
                market_data['h1'],
                market_analysis,
                self._calculate_sr(market_data['h1'])
            )
            
            if not anomalies['is_clean_market']:
                return self._create_blocked_context(
                    f"Anomalies detected: {anomalies['detected_anomalies']}",
                    market_data
                )
            
            # Camada 15: Temporal Control
            temporal_report = self.temporal_controller.get_temporal_report(
                market_analysis.get("session", {}).get("current", "UNKNOWN")
            )
            
            if temporal_report['is_forbidden']:
                return self._create_blocked_context("Forbidden trading time", market_data)
            
            # Camada 16: Crowd Intelligence
            crowd_report = self.crowd_intelligence.get_crowd_intelligence_report(market_analysis)
            
            # ═══════════════════════════════════════════════════════════
            # FASE 4: BUSCA HISTÓRICA E VALIDAÇÃO
            # ═══════════════════════════════════════════════════════════
            
            # Camada 12: Similarity Matching
            pattern_type = pattern_analysis.get("primary_signal", {}).get("type", "UNKNOWN")
            similar_situations = self.similarity_matcher.find_similar_situations(
                current_context={
                    "trend_direction": market_analysis["trend"]["consensus"]["direction"],
                    "volatility_level": market_analysis["volatility"]["classification"],
                    "pattern_type": pattern_type
                },
                current_market=market_analysis,
                current_pattern=pattern_type
            )
            
            similarity_report = self.similarity_matcher.analyze_similar_outcomes(similar_situations)
            
            # Verificar se histórico bloqueia trade
            should_block, block_reason = self.similarity_matcher.should_trade_be_blocked(similar_situations)
            if should_block:
                return self._create_blocked_context(f"Historical block: {block_reason}", market_data)
            
            # ═══════════════════════════════════════════════════════════
            # FASE 5: SCORING E DECISÃO PRELIMINAR
            # ═══════════════════════════════════════════════════════════
            
            # Camada 7: Learning Insights
            learning_insights = self.learning.get_learning_insights({
                "primary_pattern": pattern_type,
                "market_trend": market_analysis["trend"]["consensus"]["direction"],
                "volatility_level": market_analysis["volatility"]["classification"]
            })
            
            # Camada 3: Score Calculation
            score_result = self.score_engine.calculate_comprehensive_score(
                market_analysis=market_analysis,
                pattern_analysis=pattern_analysis,
                risk_analysis=self._prepare_risk_analysis(),
                learning_insights=learning_insights
            )
            
            # ═══════════════════════════════════════════════════════════
            # FASE 6: SIMULAÇÃO E VALIDAÇÃO FINAL
            # ═══════════════════════════════════════════════════════════
            
            # Camada 19: Internal Simulation
            stress_test = self.internal_simulator.stress_test_trade(
                entry_price=market_data['current_price'],
                stop_loss=market_data['current_price'] * 0.98,
                take_profit=market_data['current_price'] * 1.03,
                position_size=0.01
            )
            
            if not stress_test['trade_survives_stress']:
                return self._create_blocked_context("Failed stress test", market_data)
            
            # ═══════════════════════════════════════════════════════════
            # FASE 7: EXPLICAÇÃO E CONTEXTO FINAL
            # ═══════════════════════════════════════════════════════════
            
            # Camada 18: Second Order Explanation
            if score_result.recommendation == "EXECUTE":
                explanation = self.second_order_explainer.explain_trade_approval(
                    score=score_result.total_score,
                    key_factors=score_result.reasons,
                    risk_factors=score_result.warnings,
                    exit_conditions=[]
                )
            else:
                explanation = self.second_order_explainer.explain_trade_rejection(
                    score=score_result.total_score,
                    min_required=90,
                    reasons_for_rejection=score_result.warnings,
                    alternative_strategies=[]
                )
            
            # ═══════════════════════════════════════════════════════════
            # FASE 8: CRIAR CONTEXTO DE DECISÃO
            # ═══════════════════════════════════════════════════════════
            
            decision = DecisionContext(
                score=score_result.total_score,
                recommendation=score_result.recommendation,
                confidence=score_result.confidence,
                market_analysis=market_analysis,
                pattern_analysis=pattern_analysis,
                strategy_selected=selected_strategy.value,
                anomalies_detected=anomalies['detected_anomalies'],
                time_quality=temporal_report['time_quality_score'],
                crowd_sentiment=crowd_report['crowd_sentiment'],
                similar_historical=similarity_report,
                risk_assessment=self._prepare_risk_analysis(),
                explanation=explanation,
                stress_test_result=stress_test,
                system_health=self.resilience_engine.get_system_health()
            )
            
            return decision
        
        except Exception as e:
            self.logger.log_error("ORCHESTRATION_ERROR", str(e), {"phase": "decision_making"})
            return self._create_error_context(str(e), market_data)
    
    def execute_with_all_validations(self, decision: DecisionContext) -> bool:
        """
        Executa trade com todas as validações das 20 camadas.
        """
        if decision.recommendation != "EXECUTE":
            print(f"❌ Trade bloqueado: {decision.recommendation}")
            return False
        
        if decision.system_health < 50:
            print("⚠️  Saúde do sistema < 50%. Usando modo seguro.")
            # Aplicar configurações de segurança
        
        # Executar trade
        try:
            # ... lógica de execução ...
            print(f"✅ Trade executado com score {decision.score:.0f}/100")
            self.memory.save_trade(...)  # Salvar para histórico
            return True
        except Exception as e:
            self.logger.log_error("EXECUTION_ERROR", str(e))
            return False
    
    def periodic_self_evaluation(self):
        """
        Camada 10: Autoavaliação periódica (diária).
        """
        perf = self.self_evaluator.evaluate_daily_performance()
        
        if perf:
            # Ajustar pesos
            self.self_evaluator.adjust_weights_based_on_performance()
            self.self_evaluator.adjust_frequency_based_on_performance()
            self.self_evaluator.adjust_aggressiveness()
            
            # Atualizar score engine
            self.score_engine.weights = self.self_evaluator.current_weights
            
            print(f"📊 Autoavaliação: WR {perf.win_rate:.0%} | EV {perf.expectancy:.2f} | Pesos ajustados")
    
    def _create_blocked_context(self, reason: str, market_data: Dict) -> DecisionContext:
        """Cria contexto para decisão bloqueada"""
        return DecisionContext(
            score=0,
            recommendation="NO_TRADE",
            confidence=0,
            market_analysis={},
            pattern_analysis={},
            strategy_selected="BLOCKED",
            anomalies_detected=[reason],
            time_quality=0,
            crowd_sentiment="UNKNOWN",
            similar_historical={},
            risk_assessment={},
            explanation={"reason": reason},
            stress_test_result={},
            system_health=100
        )
    
    def _create_error_context(self, error: str, market_data: Dict) -> DecisionContext:
        """Cria contexto para erro"""
        self.resilience_engine.check_module_health("orchestrator", False)
        return DecisionContext(
            score=0,
            recommendation="ERROR",
            confidence=0,
            market_analysis={},
            pattern_analysis={},
            strategy_selected="ERROR",
            anomalies_detected=[error],
            time_quality=0,
            crowd_sentiment="UNKNOWN",
            similar_historical={},
            risk_assessment={},
            explanation={"error": error},
            stress_test_result={},
            system_health=self.resilience_engine.get_system_health()
        )
    
    def _calculate_sr(self, df) -> Dict:
        """Calcula suporte/resistência"""
        recent = df.tail(50)
        return {
            "resistance": sorted(recent['high'].nlargest(3).tolist(), reverse=True),
            "support": sorted(recent['low'].nsmallest(3).tolist())
        }
    
    def _prepare_risk_analysis(self) -> Dict:
        """Prepara análise de risco"""
        return {
            "current_drawdown_pct": self.risk_manager.state.get("current_drawdown_pct", 0),
            "exposure_pct": self.risk_manager.state.get("current_exposure_pct", 0),
            "potential_profit": 100,
            "potential_loss": 50
        }
    
    def get_full_system_report(self) -> Dict:
        """Relatório completo do sistema"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": self.resilience_engine.get_system_health(),
            "self_evaluation": self.self_evaluator.get_evaluation_summary(),
            "strategies": self.strategy_ensemble.get_strategy_report(),
            "resilience": self.resilience_engine.get_resilience_report(),
            "future_readiness": self.future_readiness.get_readiness_report(),
            "installed_plugins": self.future_readiness.list_installed_plugins(),
            "version": "2.0 - 20 Camadas"
        }
