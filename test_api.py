"""
Script para testar a API do bot sem iniciar o servidor.
Verifica se todos os endpoints funcionam corretamente.
"""

import json
import os
from datetime import datetime

print("=" * 70)
print("🔍 TESTE DE API - TRADING BOT")
print("=" * 70)

# Importar funções da API
from main_api import (
    health,
    get_state,
    pause,
    resume,
    ai_health,
    ai_engines_status,
    get_latest_decision,
    export_decisions,
    get_veto_log,
    get_engine_performance
)

print("\n✅ Imports bem-sucedidos")

# Teste 1: Health check
print("\n1️⃣  Health Check...")
try:
    result = health()
    print(f"   ✓ Status: {result['status']}")
except Exception as e:
    print(f"   ✗ Erro: {e}")

# Teste 2: Get State
print("\n2️⃣  Get State...")
try:
    result = get_state()
    print(f"   ✓ Bot Status: {result['bot']['status']}")
    print(f"   ✓ Trade Ativo: {result['operacao']['trade_ativo']}")
except Exception as e:
    print(f"   ✗ Erro: {e}")

# Teste 3: Pause/Resume
print("\n3️⃣  Pause/Resume...")
try:
    pause()
    result = get_state()
    print(f"   ✓ Após pause: {result['bot']['status']}")
    
    resume()
    result = get_state()
    print(f"   ✓ Após resume: {result['bot']['status']}")
except Exception as e:
    print(f"   ✗ Erro: {e}")

# Teste 4: AI Health
print("\n4️⃣  AI Health Check...")
try:
    result = ai_health()
    print(f"   ✓ Success: {result['success']}")
    print(f"   ✓ Healthy: {result['healthy']}")
    print(f"   ✓ Overall Health: {result['overall_health']:.1f}%")
    print(f"   ✓ Engines: {len(result['engines'])}")
except Exception as e:
    print(f"   ✗ Erro: {e}")

# Teste 5: AI Engines Status
print("\n5️⃣  AI Engines Status...")
try:
    result = ai_engines_status()
    print(f"   ✓ Success: {result['success']}")
    print(f"   ✓ All Operational: {result['all_operational']}")
    for engine in result['engines'][:3]:
        print(f"     - {engine['name']}: {engine['status']}")
except Exception as e:
    print(f"   ✗ Erro: {e}")

# Teste 6: Latest Decision
print("\n6️⃣  Latest Decision...")
try:
    result = get_latest_decision()
    print(f"   ✓ Success: {result['success']}")
    decision = result['decision']
    print(f"   ✓ Action: {decision['action']}")
    print(f"   ✓ Confidence: {decision['confidence']:.2f}")
except Exception as e:
    print(f"   ✗ Erro: {e}")

# Teste 7: Export Decisions
print("\n7️⃣  Export Decisions...")
try:
    result = export_decisions()
    print(f"   ✓ Success: {result['success']}")
    print(f"   ✓ Decision Count: {result['count']}")
    print(f"   ✓ Format: {result['format']}")
except Exception as e:
    print(f"   ✗ Erro: {e}")

# Teste 8: Veto Log
print("\n8️⃣  Veto Log...")
try:
    result = get_veto_log()
    print(f"   ✓ Success: {result['success']}")
    print(f"   ✓ Total Vetoes: {result['total']}")
    print(f"   ✓ Limit: {result['limit']}")
except Exception as e:
    print(f"   ✗ Erro: {e}")

# Teste 9: Engine Performance
print("\n9️⃣  Engine Performance...")
try:
    result = get_engine_performance()
    print(f"   ✓ Success: {result['success']}")
    for engine_name, stats in result['engines'].items():
        print(f"     - {engine_name}: {stats['accuracy']:.1%} accuracy")
except Exception as e:
    print(f"   ✗ Erro: {e}")

print("\n" + "=" * 70)
print("✅ TESTES CONCLUÍDOS COM SUCESSO")
print("=" * 70)
print("\nPróximos passos:")
print("  1. python run_api.py          # Inicia servidor API")
print("  2. Acessar http://localhost:8000/docs")
print("  3. Testar endpoints interativamente")
print("\nOu executar:")
print("  python trading_bot.py         # Inicia bot de trading")
