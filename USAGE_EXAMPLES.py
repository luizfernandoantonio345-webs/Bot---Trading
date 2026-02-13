"""
═══════════════════════════════════════════════════════════════════════════════
                        EXEMPLOS DE USO - 20 CAMADAS
═══════════════════════════════════════════════════════════════════════════════


🎯 EXEMPLO 1: DECISÃO COMPLETA BÁSICA
═══════════════════════════════════════════════════════════════════════════════

from core.master_orchestrator import MasterOrchestrator

# Criar bot
config = {'use_testnet': True, 'log_level': 'DEBUG'}
bot = MasterOrchestrator(config)

# Dados de mercado simples
market_data = {
    'price': 1.0800,
    'trend': 'bullish',
    'strength': 75,
    'pattern': 'engulfing',
    'session': 'NY'
}

# Fazer decisão
decision = bot.make_complete_decision(market_data)

# Verificar resultado
print(f"Score: {decision.score:.0f}/100")
print(f"Recommendation: {decision.recommendation}")
print(f"Confidence: {decision.confidence:.0%}")
print(f"Strategy: {decision.strategy_selected}")
print(f"System Health: {decision.system_health:.0%}")
print(f"\\nExplanation:\\n{decision.explanation}")


🎯 EXEMPLO 2: AUTOSSITUAÇÃO DIÁRIA
═══════════════════════════════════════════════════════════════════════════════

from core.self_evaluator import SelfEvaluator, DailyPerformance

# Criar avaliador
evaluator = SelfEvaluator()

# Simular performance do dia
daily_perf = DailyPerformance(
    win_rate=0.45,           # 45% taxa de acerto
    expected_value=0.08,     # EV positivo
    sharpe_ratio=1.2,
    max_drawdown=0.18,       # 18% drawdown
    num_trades=25,
    avg_entry_quality=72,
    profit_factor=1.1,
    consecutive_losses=3,
    best_trade=0.15,
    worst_trade=-0.05
)

# Avaliar
evaluation = evaluator.evaluate_daily_performance(daily_perf)
print(f"Avaliação do Dia:")
print(f"  Win Rate: {evaluation['win_rate']:.0%}")
print(f"  EV: {evaluation['expected_value']:.2f}")

# Ajustar pesos
adjustments = evaluator.adjust_weights_based_on_performance(daily_perf)
print(f"\\nAjustes aplicados: {adjustments}")

# Ajustar frequência
freq_multiplier = evaluator.adjust_frequency_based_on_performance(daily_perf)
print(f"Multiplicador de frequência: {freq_multiplier:.1f}x")

# Ajustar agressividade
aggr_multiplier = evaluator.adjust_aggressiveness(daily_perf)
print(f"Multiplicador de agressividade: {aggr_multiplier:.1f}x")


🎯 EXEMPLO 3: TESTE DE ANOMALIAS
═══════════════════════════════════════════════════════════════════════════════

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
    'volume': [1000, 1200, 5000, 1100, 1300]  # Volume spike na 3ª vela
})

# Detectar anomalias
report = detector.get_anomaly_report(data)
print(f"Relatório de Anomalias:")
print(f"  Mercado Limpo: {report['is_clean_market']}")
print(f"  Anomalias Detectadas: {len(report['anomalies'])}")
for anomaly in report['anomalies']:
    print(f"    - {anomaly}")


🎯 EXEMPLO 4: BUSCA POR HISTÓRICO SIMILAR
═══════════════════════════════════════════════════════════════════════════════

from core.similarity_matcher import SimilarityMatcher

# Criar matcher
matcher = SimilarityMatcher()

# Setup atual
current_analysis = {
    'trend': 0.8,           # 80% bullish
    'volatility': 0.7,
    'structure': 'engulfing',
    'pattern': 'bullish_flag',
    'session': 'NY',
    'momentum': 0.75,
    'liquidity': 0.9
}

# Buscar 5 trades similares
similar = matcher.find_similar_situations(current_analysis, top_n=5)

print(f"Situações Similares Encontradas: {len(similar)}")
for i, match in enumerate(similar, 1):
    print(f"\\n{i}. Similaridade: {match.similarity_score:.2f}")
    print(f"   Win Rate: {match.win_rate:.0%}")
    print(f"   Trades: {match.num_similar_trades}")

# Decidir se bloqueia
should_block = matcher.should_trade_be_blocked(current_analysis)
print(f"\\nBloqueado por histórico ruim: {should_block}")


🎯 EXEMPLO 5: SELEÇÃO DE ESTRATÉGIA
═══════════════════════════════════════════════════════════════════════════════

from core.advanced_layers_1315 import StrategyEnsemble

# Criar ensemble
ensemble = StrategyEnsemble()

# Diferentes condições de mercado
scenarios = [
    {'trend_strength': 75, 'volatility': 0.85, 'structure': 'higher_highs'},
    {'trend_strength': 30, 'volatility': 0.4, 'structure': 'sideways'},
    {'trend_strength': 60, 'volatility': 1.2, 'structure': 'breakout'},
]

for scenario in scenarios:
    strategy, confidence = ensemble.select_strategy(scenario)
    print(f"Market: {scenario['structure']:15} → Strategy: {strategy.name:20} ({confidence:.0%})")


🎯 EXEMPLO 6: ATENÇÃO ADAPTATIVA
═══════════════════════════════════════════════════════════════════════════════

from core.attention_model import ContextualAttentionModel

# Criar modelo
model = ContextualAttentionModel()

# Análise de mercado
market_analysis = {
    'trend': 'up',
    'strength': 75,
    'volatility': 0.85,
    'structure': 'higher_highs',
    'session': 'NY'
}

# Computar pesos de atenção
weights = model.compute_attention_weights(market_analysis)
print(f"Pesos de Atenção por Indicador:")
for indicator, weight in weights.items():
    print(f"  {indicator}: {weight:.2f}")

# Sinais disponíveis
signals = [
    {'name': 'RSI', 'value': 65, 'period': '5m'},
    {'name': 'Moving Average', 'value': 72, 'period': '1h'},
    {'name': 'Volume', 'value': 80, 'period': '15m'},
    {'name': 'MACD', 'value': 45, 'period': '1h'},
]

# Priorizar sinais por relevância
prioritized = model.prioritize_signals(signals, weights)
print(f"\\nSinais Priorizados:")
for sig in prioritized:
    print(f"  1. {sig['name']} ({sig['value']}) - Período: {sig['period']}")


🎯 EXEMPLO 7: INTELIGÊNCIA TEMPORAL
═══════════════════════════════════════════════════════════════════════════════

from core.advanced_layers_1315 import TemporalController
from datetime import datetime

# Criar controller
temporal = TemporalController()

# Testar diferentes horários
test_hours = [
    (8, 'LONDON'),   # 8:00 London (antes do ótimo)
    (10, 'LONDON'),  # 10:00 London (ótimo)
    (15, 'NY'),      # 15:00 NY (ótimo)
    (23, 'NY'),      # 23:00 NY (proibido)
    (2, 'ASIA'),     # 2:00 ASIA (ótimo)
]

print(f"Qualidade de Horários:")
print(f"{'Hora':10} {'Sessão':10} {'Ótimo':8} {'Proibido':10} {'Score':8}")
print(f"{'-'*50}")

for hour, session in test_hours:
    dt = datetime.now().replace(hour=hour)
    is_optimal = temporal.is_optimal_trading_time(dt, session)
    is_forbidden = temporal.is_forbidden_time(dt, session)
    quality = temporal.get_time_quality_score(dt, session)
    
    print(f"{hour:02d}:00 {session:10} {str(is_optimal):8} {str(is_forbidden):10} {quality:.0f}/100")


🎯 EXEMPLO 8: INTELIGÊNCIA DE MULTIDÃO
═══════════════════════════════════════════════════════════════════════════════

from core.advanced_layers_1620 import CrowdIntelligence

# Criar inteligência
crowd = CrowdIntelligence()

print("CENÁRIO 1: FOMO Setup")
print("-" * 50)
market_data_fomo = {
    'momentum': 0.88,
    'volume': 1.8,  # 1.8x media
    'volatility': 0.9
}
fomo = crowd.detect_fomo_setup(market_data_fomo)
print(f"FOMO Detectado: {fomo}")

print("\\nCENÁRIO 2: Capitulação")
print("-" * 50)
market_data_cap = {
    'score': 15,  # Muito baixo
    'recent_losses': ['L', 'L', 'L']  # 3 perdas
}
capitulation = crowd.detect_capitulation(market_data_cap)
print(f"Capitulação Detectada: {capitulation}")

print("\\nCENÁRIO 3: Retail Trap")
print("-" * 50)
market_data_trap = {
    'momentum': 0.82,
    'volume': 1.5,
    'price_movement': 0.015  # 1.5% movimento
}
trap = crowd.detect_retail_trap(market_data_trap)
print(f"Armadilha de Varejo Detectada: {trap}")


🎯 EXEMPLO 9: STRESS TEST
═══════════════════════════════════════════════════════════════════════════════

from core.advanced_layers_1620 import InternalSimulator

# Criar simulator
simulator = InternalSimulator()

# Parâmetros do trade
trade = {
    'entry_price': 1.0800,
    'stop_loss': 1.0790,
    'take_profit': 1.0820,
    'position_size': 1.0
}

# Executar stress test
result = simulator.stress_test_trade(trade)

print(f"Stress Test Resultado:")
print(f"  Recommendation: {result['recommendation']}")
print(f"  Survival Rate: {result['survival_rate']:.0%}")
print(f"\\nCenários Testados:")
for scenario in result['scenarios']:
    print(f"  {scenario['name']:20} → {scenario['result']:20} (PnL: {scenario['pnl']:.0f})")


🎯 EXEMPLO 10: EXPLICAÇÃO PROFUNDA
═══════════════════════════════════════════════════════════════════════════════

from core.advanced_layers_1620 import SecondOrderExplainer

# Criar explicador
explainer = SecondOrderExplainer()

print("CENÁRIO 1: Trade Rejeitado")
print("-" * 50)
rejection_data = {
    'score': 72,
    'min_score': 80,
    'key_factors': ['momentum too low', 'volume weak'],
    'recommendation': 'REJECT'
}
explanation = explainer.explain_trade_rejection(rejection_data)
print(explanation)

print("\\nCENÁRIO 2: Trade Aprovado")
print("-" * 50)
approval_data = {
    'score': 92,
    'key_factors': ['strong trend', 'high volume', 'optimal time'],
    'risk_factors': ['sentiment extreme', 'gap risk'],
    'recommendation': 'EXECUTE'
}
explanation2 = explainer.explain_trade_approval(approval_data)
print(explanation2)


🎯 EXEMPLO 11: RESILIÊNCIA E SAFE MODE
═══════════════════════════════════════════════════════════════════════════════

from core.advanced_layers_1620 import ResilienceEngine

# Criar engine
resilience = ResilienceEngine()

print("Sistema de Resiliência")
print("-" * 50)

# Registrar falhas
print("1. Registrando falhas de módulo 'attention_model'...")
for i in range(3):
    resilience.check_module_health('attention_model', failed=True)

# Verificar saúde
health = resilience.get_system_health()
print(f"2. Saúde do Sistema: {health:.0%}")

# Verificar safe mode
should_safe_mode = resilience.should_activate_safe_mode()
print(f"3. Safe Mode Ativado: {should_safe_mode}")

# Obter fallback settings
if should_safe_mode:
    fallback = resilience.get_fallback_settings()
    print(f"4. Configurações de Fallback:")
    print(f"   Min Score: {fallback['min_score']}")
    print(f"   Position Size: {fallback['position_size']}")
    print(f"   Max Trades: {fallback['max_trades']}")


🎯 EXEMPLO 12: EXTENSIBILIDADE (Plugin System)
═══════════════════════════════════════════════════════════════════════════════

from core.advanced_layers_1620 import FutureReadiness

# Criar readiness engine
future = FutureReadiness()

# Registrar novo plugin
print("Registrando novo plugin...")
future.register_plugin('custom_trend_strategy', {
    'version': '1.0',
    'author': 'your_team',
    'description': 'Custom trend following strategy'
})

# Registrar nova data source
print("Registrando nova data source...")
future.register_data_source('crypto_sentiment_api', {
    'url': 'https://api.example.com',
    'frequency': 'minute',
    'format': 'json'
})

# Adicionar novo regime
print("Adicionando novo regime...")
future.add_market_regime('crypto_volatility', {
    'volatility_min': 0.02,
    'volatility_max': 0.05,
    'description': 'Medium volatility crypto markets'
})

# Listar instalados
print("\\nPlugins Instalados:")
plugins = future.list_installed_plugins()
print(f"Estratégias: {len(plugins['strategies'])}")
print(f"Data Sources: {len(plugins['data_sources'])}")
print(f"Regimes: {len(plugins['regimes'])}")


🎯 EXEMPLO 13: INTEGRAÇÃO COMPLETA
═══════════════════════════════════════════════════════════════════════════════

from core.master_orchestrator import MasterOrchestrator
import json

# Criar bot completo
bot = MasterOrchestrator({'use_testnet': True})

# Dados reais
market_data = {
    'symbol': 'EURUSD',
    'timeframe': '5m',
    'price': 1.0800,
    'trend': 'bullish',
    'pattern': 'engulfing',
    'momentum': 0.75,
    'volume': 1.2,
    'session': 'NY'
}

print("DECISÃO COMPLETA - 8 FASES")
print("=" * 60)

# Fazer decisão
decision = bot.make_complete_decision(market_data)

# Mostrar resultado completo
print(f"\\n✓ FASE 1-8 Completa")
print(f"\\nResultado da Decisão:")
print(f"  Score: {decision.score:.0f}/100")
print(f"  Recomendação: {decision.recommendation}")
print(f"  Confiança: {decision.confidence:.0%}")
print(f"\\nContexto Completo:")
print(f"  Estratégia: {decision.strategy_selected}")
print(f"  Anomalias: {decision.anomalies_detected}")
print(f"  Qualidade Temporal: {decision.time_quality:.0%}")
print(f"  Sentimento Multidão: {decision.crowd_sentiment}")
print(f"  Saúde do Sistema: {decision.system_health:.0%}")
print(f"\\nExplicação:")
print(f"{decision.explanation}")

# Executar se aprovado
if decision.recommendation == "EXECUTE":
    print(f"\\n✓ Executando com todas validações...")
    result = bot.execute_with_all_validations(decision)
    print(f"  Resultado: {result}")


═══════════════════════════════════════════════════════════════════════════════

Estes são exemplos práticos de como usar cada camada do sistema.

Para mais informações, consulte:
  • ARCHITECTURE_20_LAYERS.py
  • IMPLEMENTATION_SUMMARY.py
  • TESTING_GUIDE.py
"""

if __name__ == "__main__":
    print(__doc__)
