"""
═══════════════════════════════════════════════════════════════════════════════
                         GUIA DE TESTES - 20 CAMADAS
═══════════════════════════════════════════════════════════════════════════════


🧪 TESTES DE IMPORTAÇÃO (VALIDAÇÃO BÁSICA)
═══════════════════════════════════════════════════════════════════════════════

python -c "from core.master_orchestrator import MasterOrchestrator; print('✓ MasterOrchestrator')"
python -c "from core.self_evaluator import SelfEvaluator; print('✓ SelfEvaluator')"
python -c "from core.attention_model import ContextualAttentionModel; print('✓ AttentionModel')"
python -c "from core.similarity_matcher import SimilarityMatcher; print('✓ SimilarityMatcher')"
python -c "from core.advanced_layers_1315 import StrategyEnsemble, AnomalyDetector, TemporalController; print('✓ Layers 13-15')"
python -c "from core.advanced_layers_1620 import CrowdIntelligence, ResilienceEngine, SecondOrderExplainer, InternalSimulator, FutureReadiness; print('✓ Layers 16-20')"


📝 TESTE UNITÁRIO DETALHADO
═══════════════════════════════════════════════════════════════════════════════

1. TESTE CAMADA 10 (SelfEvaluator)
─────────────────────────────────────────────────────────────────────────────

from core.self_evaluator import SelfEvaluator, DailyPerformance

# Criar instância
evaluator = SelfEvaluator()

# Simular performance
performance = DailyPerformance(
    win_rate=0.45,
    expected_value=0.08,
    sharpe_ratio=1.2,
    max_drawdown=0.18,
    num_trades=25,
    avg_entry_quality=72,
    profit_factor=1.1,
    consecutive_losses=3,
    best_trade=0.15,
    worst_trade=-0.05
)

# Avaliar
evaluation = evaluator.evaluate_daily_performance(performance)
print(f"✓ WR: {evaluation['win_rate']}")
print(f"✓ EV: {evaluation['expected_value']}")

# Ajustar pesos
adjustments = evaluator.adjust_weights_based_on_performance(performance)
print(f"✓ Weights adjusted: {adjustments}")


2. TESTE CAMADA 11 (AttentionModel)
─────────────────────────────────────────────────────────────────────────────

from core.attention_model import ContextualAttentionModel, AttentionFocus

# Criar modelo
model = ContextualAttentionModel()

# Simular análise de mercado
market_analysis = {
    'trend': 'up',
    'strength': 75,
    'volatility': 0.85,
    'structure': 'higher_highs',
    'session': 'NY'
}

# Computar pesos
weights = model.compute_attention_weights(market_analysis)
print(f"✓ Attention weights: {weights}")

# Priorizar sinais
signals = [
    {'name': 'RSI', 'value': 65, 'period': '5m'},
    {'name': 'Moving Average', 'value': 72, 'period': '1h'},
    {'name': 'Volume', 'value': 80, 'period': '15m'},
]
prioritized = model.prioritize_signals(signals, weights)
print(f"✓ Prioritized signals: {prioritized}")


3. TESTE CAMADA 12 (SimilarityMatcher)
─────────────────────────────────────────────────────────────────────────────

from core.similarity_matcher import SimilarityMatcher

# Criar matcher
matcher = SimilarityMatcher()

# Análise atual
current_analysis = {
    'trend': 0.8,  # 80% up
    'volatility': 0.7,
    'structure': 'engulfing',
    'pattern': 'bullish_flag',
    'session': 'NY',
    'momentum': 0.75,
    'liquidity': 0.9
}

# Buscar similares
similar = matcher.find_similar_situations(current_analysis, top_n=5)
print(f"✓ Found {len(similar)} similar situations")

# Analisar outcomes
for match in similar:
    print(f"  • Similarity: {match.similarity_score:.2f}, WR: {match.win_rate:.0%}")

# Decisão
should_block = matcher.should_trade_be_blocked(current_analysis)
print(f"✓ Trade blocked: {should_block}")


4. TESTE CAMADA 13 (StrategyEnsemble)
─────────────────────────────────────────────────────────────────────────────

from core.advanced_layers_1315 import StrategyEnsemble, StrategyType

# Criar ensemble
ensemble = StrategyEnsemble()

# Análise de mercado
market_analysis = {
    'trend_strength': 75,
    'volatility': 0.85,
    'structure': 'higher_highs',
    'momentum': 0.8
}

# Selecionar estratégia
strategy, confidence = ensemble.select_strategy(market_analysis)
print(f"✓ Selected: {strategy} ({confidence:.0%} confidence)")

# Verificar performance
status = ensemble.get_strategy_report()
print(f"✓ Strategy report: {status}")


5. TESTE CAMADA 14 (AnomalyDetector)
─────────────────────────────────────────────────────────────────────────────

from core.advanced_layers_1315 import AnomalyDetector
import pandas as pd

# Criar detector
detector = AnomalyDetector()

# Simular dados OHLCV
data = pd.DataFrame({
    'open': [1.0800, 1.0810, 1.0820, 1.0815, 1.0825],
    'high': [1.0815, 1.0825, 1.0835, 1.0820, 1.0830],
    'low': [1.0795, 1.0805, 1.0815, 1.0810, 1.0820],
    'close': [1.0810, 1.0820, 1.0830, 1.0815, 1.0825],
    'volume': [1000, 1200, 5000, 1100, 1300]  # Volume spike
})

# Detectar anomalias
report = detector.get_anomaly_report(data)
print(f"✓ Anomalies detected: {report}")


6. TESTE CAMADA 15 (TemporalController)
─────────────────────────────────────────────────────────────────────────────

from core.advanced_layers_1315 import TemporalController
from datetime import datetime

# Criar controller
temporal = TemporalController()

# Testar horários diferentes
for hour in [2, 9, 15, 23]:  # Testador various hours
    dt = datetime.now().replace(hour=hour)
    is_optimal = temporal.is_optimal_trading_time(dt, session='NY')
    quality = temporal.get_time_quality_score(dt, session='NY')
    print(f"✓ {hour:02d}:00 - Optimal: {is_optimal}, Quality: {quality:.0%}")


7. TESTE CAMADA 16 (CrowdIntelligence)
─────────────────────────────────────────────────────────────────────────────

from core.advanced_layers_1620 import CrowdIntelligence

# Criar inteligência
crowd = CrowdIntelligence()

# Cenário 1: FOMO
market_data = {
    'momentum': 0.88,
    'volume': 1.8,  # 1.8x average
    'volatility': 0.9
}
fomo = crowd.detect_fomo_setup(market_data)
print(f"✓ FOMO detected: {fomo}")

# Cenário 2: Capitulação
market_data2 = {
    'score': 15,  # Muito baixo
    'recent_losses': ['L', 'L', 'L']  # 3 perdas
}
cap = crowd.detect_capitulation(market_data2)
print(f"✓ Capitulation detected: {cap}")


8. TESTE CAMADA 17 (ResilienceEngine)
─────────────────────────────────────────────────────────────────────────────

from core.advanced_layers_1620 import ResilienceEngine

# Criar engine
resilience = ResilienceEngine()

# Registrar falhas
resilience.check_module_health('attention_model', failed=True)
resilience.check_module_health('attention_model', failed=True)
resilience.check_module_health('attention_model', failed=True)

# Verificar saúde
health = resilience.get_system_health()
print(f"✓ System health: {health:.0%}")

# Verificar safe mode
should_safe_mode = resilience.should_activate_safe_mode()
print(f"✓ Safe mode activated: {should_safe_mode}")

# Obter fallback
fallback = resilience.get_fallback_settings()
print(f"✓ Fallback settings: {fallback}")


9. TESTE CAMADA 18 (SecondOrderExplainer)
─────────────────────────────────────────────────────────────────────────────

from core.advanced_layers_1620 import SecondOrderExplainer

# Criar explicador
explainer = SecondOrderExplainer()

# Rejeição
rejection_data = {
    'score': 72,
    'min_score': 80,
    'key_factors': ['momentum too low', 'volume weak']
}
explanation = explainer.explain_trade_rejection(rejection_data)
print(f"✓ Rejection explanation:\n{explanation}\n")

# Aprovação
approval_data = {
    'score': 92,
    'key_factors': ['strong trend', 'high volume', 'optimal time'],
    'risk_factors': ['sentiment extreme', 'gap risk']
}
explanation2 = explainer.explain_trade_approval(approval_data)
print(f"✓ Approval explanation:\n{explanation2}\n")


10. TESTE CAMADA 19 (InternalSimulator)
─────────────────────────────────────────────────────────────────────────────

from core.advanced_layers_1620 import InternalSimulator

# Criar simulator
simulator = InternalSimulator()

# Parâmetros de trade
trade = {
    'entry_price': 1.0800,
    'stop_loss': 1.0790,
    'take_profit': 1.0820,
    'position_size': 1.0
}

# Stress test
result = simulator.stress_test_trade(trade)
print(f"✓ Stress test result:")
print(f"  Survival rate: {result['survival_rate']:.0%}")
print(f"  Recommendation: {result['recommendation']}")


11. TESTE CAMADA 20 (FutureReadiness)
─────────────────────────────────────────────────────────────────────────────

from core.advanced_layers_1620 import FutureReadiness

# Criar readiness
future = FutureReadiness()

# Registrar plugin
future.register_plugin('custom_strategy', {'version': '1.0'})

# Listar plugins
plugins = future.list_installed_plugins()
print(f"✓ Installed plugins: {plugins}")

# API reference
api = future.get_api_reference()
print(f"✓ API available: {len(api)} endpoints")


🔗 TESTE DE INTEGRAÇÃO (MasterOrchestrator)
═══════════════════════════════════════════════════════════════════════════════

from core.master_orchestrator import MasterOrchestrator, DecisionContext
import json

# Criar orquestrador
config = {
    'use_testnet': True,
    'log_level': 'DEBUG'
}
orchestrator = MasterOrchestrator(config)

# Simular análise de mercado
market_data = {
    'price': 1.0800,
    'trend': 'bullish',
    'pattern': 'engulfing',
    'momentum': 0.75,
    'volume': 1.2,  # 1.2x average
    'session': 'NY'
}

# Fazer decisão completa
try:
    decision = orchestrator.make_complete_decision(market_data)
    
    print(f"✓ Decision made:")
    print(f"  Score: {decision.score:.0f}/100")
    print(f"  Recommendation: {decision.recommendation}")
    print(f"  Confidence: {decision.confidence:.0%}")
    print(f"  Strategy: {decision.strategy_selected}")
    print(f"  System Health: {decision.system_health:.0%}")
    print(f"  Explanation:\n{decision.explanation}")
    
except Exception as e:
    print(f"✗ Error: {e}")


📊 TESTE DE PERFORMANCE
═══════════════════════════════════════════════════════════════════════════════

import time

# Timing de pipeline completo
start = time.time()
decision = orchestrator.make_complete_decision(market_data)
elapsed = time.time() - start

print(f"✓ Pipeline execution time: {elapsed*1000:.1f}ms")
print(f"  Expected: < 500ms")
print(f"  Status: {'✓ PASS' if elapsed < 0.5 else '✗ FAIL'}")


🔍 TESTE DE ESTRESSE (Camada 17)
═══════════════════════════════════════════════════════════════════════════════

# Simular falhas de módulos
for i in range(5):
    orchestrator.resilience_engine.check_module_health('test_module', failed=True)

health = orchestrator.resilience_engine.get_system_health()
print(f"✓ After 5 failures: health = {health:.0%}")

if health < 50:
    print(f"✓ Safe mode activated automatically")
    settings = orchestrator.resilience_engine.get_fallback_settings()
    print(f"  Fallback: {settings}")


✅ LISTA DE VERIFICAÇÃO
═══════════════════════════════════════════════════════════════════════════════

[ ] 1. Todas as importações funcionam
[ ] 2. SelfEvaluator calcula performance corretamente
[ ] 3. AttentionModel adapta pesos por regime
[ ] 4. SimilarityMatcher encontra histórico similar
[ ] 5. StrategyEnsemble seleciona estratégia correta
[ ] 6. AnomalyDetector detecta mercado anormal
[ ] 7. TemporalController sabe horários ótimos/ruins
[ ] 8. CrowdIntelligence detecta FOMO/capitulação
[ ] 9. ResilienceEngine ativa safe mode automaticamente
[ ] 10. SecondOrderExplainer explica decisões
[ ] 11. InternalSimulator faz stress test correto
[ ] 12. FutureReadiness plugin system funciona
[ ] 13. MasterOrchestrator integra tudo
[ ] 14. DecisionContext tem todas informações
[ ] 15. Pipeline completo executa < 500ms
[ ] 16. Sistema recupera de falhas automaticamente
[ ] 17. Explicações são claras e acionáveis
[ ] 18. Estado persiste entre reinícios
[ ] 19. Histórico de trades é consultado
[ ] 20. Safe mode reduz agressividade adequadamente


🚀 PRÓXIMOS PASSOS APÓS TESTES
═══════════════════════════════════════════════════════════════════════════════

1. BACKTEST (1-2 dias)
   └─ Testar com dados históricos
   └─ Comparar performance vs versão anterior
   └─ Validar returns & Sharpe ratio

2. PAPER TRADING (1-2 semanas)
   └─ Usar testnet Binance
   └─ Monitore performance diária
   └─ Ajuste parâmetros se necessário

3. PRODUÇÃO (após validação)
   └─ Deploy em conta real
   └─ Monitoramento 24/7
   └─ Gradualmente aumentar posição


═══════════════════════════════════════════════════════════════════════════════
                             TESTES PRONTOS
═══════════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(__doc__)
