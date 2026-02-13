"""
Script de validação do sistema de trading.
Verifica se todos os módulos estão funcionando corretamente.
"""

import sys
import os

print("=" * 70)
print("🔍 VALIDAÇÃO DO SISTEMA DE TRADING")
print("=" * 70)

# Testar imports
print("\n1️⃣ Testando imports dos módulos...")

try:
    from core.market_analyzer import MarketAnalyzer
    print("  ✅ MarketAnalyzer")
except Exception as e:
    print(f"  ❌ MarketAnalyzer: {e}")
    sys.exit(1)

try:
    from core.pattern_engine import PatternEngine
    print("  ✅ PatternEngine")
except Exception as e:
    print(f"  ❌ PatternEngine: {e}")
    sys.exit(1)

try:
    from core.score_engine import ScoreEngine
    print("  ✅ ScoreEngine")
except Exception as e:
    print(f"  ❌ ScoreEngine: {e}")
    sys.exit(1)

try:
    from core.risk_manager import RiskManager
    print("  ✅ RiskManager")
except Exception as e:
    print(f"  ❌ RiskManager: {e}")
    sys.exit(1)

try:
    from core.execution_engine import BinanceExecutor
    print("  ✅ BinanceExecutor")
except Exception as e:
    print(f"  ❌ BinanceExecutor: {e}")
    sys.exit(1)

try:
    from core.memory_engine import MemoryEngine
    print("  ✅ MemoryEngine")
except Exception as e:
    print(f"  ❌ MemoryEngine: {e}")
    sys.exit(1)

try:
    from core.learning_engine import LearningEngine
    print("  ✅ LearningEngine")
except Exception as e:
    print(f"  ❌ LearningEngine: {e}")
    sys.exit(1)

try:
    from core.logger import get_logger
    print("  ✅ Logger")
except Exception as e:
    print(f"  ❌ Logger: {e}")
    sys.exit(1)

# Testar dependências externas
print("\n2️⃣ Testando dependências externas...")

try:
    import numpy as np
    print(f"  ✅ NumPy {np.__version__}")
except:
    print("  ❌ NumPy não instalado")
    sys.exit(1)

try:
    import pandas as pd
    print(f"  ✅ Pandas {pd.__version__}")
except:
    print("  ❌ Pandas não instalado")
    sys.exit(1)

try:
    import ccxt
    print(f"  ✅ CCXT {ccxt.__version__}")
except:
    print("  ❌ CCXT não instalado")
    sys.exit(1)

try:
    import requests
    print(f"  ✅ Requests {requests.__version__}")
except:
    print("  ❌ Requests não instalado")
    sys.exit(1)

try:
    import yaml
    print(f"  ✅ PyYAML")
except:
    print("  ❌ PyYAML não instalado")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print(f"  ✅ Python-dotenv")
except:
    print("  ❌ Python-dotenv não instalado")
    sys.exit(1)

# Testar estrutura de arquivos
print("\n3️⃣ Verificando estrutura de arquivos...")

required_files = [
    "config/api_keys.env",
    "config/risk_limits.yaml",
    "config/weights.yaml",
    "core/__init__.py",
    "core/market_analyzer.py",
    "core/pattern_engine.py",
    "core/score_engine.py",
    "core/risk_manager.py",
    "core/execution_engine.py",
    "core/memory_engine.py",
    "core/learning_engine.py",
    "core/logger.py",
    "trading_bot.py",
    "requirements.txt"
]

missing_files = []
for file in required_files:
    if os.path.exists(file):
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} - AUSENTE")
        missing_files.append(file)

# Testar configurações
print("\n4️⃣ Verificando configurações...")

if os.path.exists("config/api_keys.env"):
    from dotenv import load_dotenv
    load_dotenv("config/api_keys.env")
    
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")
    
    if api_key and api_key != "your_api_key_here":
        print("  ✅ BINANCE_API_KEY configurada")
    else:
        print("  ⚠️  BINANCE_API_KEY não configurada (necessário para produção)")
    
    if api_secret and api_secret != "your_api_secret_here":
        print("  ✅ BINANCE_API_SECRET configurada")
    else:
        print("  ⚠️  BINANCE_API_SECRET não configurada (necessário para produção)")
    
    use_testnet = os.getenv("USE_TESTNET", "True")
    print(f"  ℹ️  USE_TESTNET: {use_testnet}")
    
    if use_testnet.lower() == "true":
        print("  ✅ Modo TESTNET ativo (seguro para testes)")
    else:
        print("  ⚠️  Modo PRODUÇÃO ativo (cuidado!)")
else:
    print("  ❌ config/api_keys.env não encontrado")

# Testar criação de diretórios
print("\n5️⃣ Verificando/criando diretórios necessários...")

required_dirs = ["logs", "data"]
for directory in required_dirs:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"  ✅ {directory}/ criado")
    else:
        print(f"  ✅ {directory}/ existe")

# Resultado final
print("\n" + "=" * 70)
if missing_files:
    print("❌ VALIDAÇÃO FALHOU")
    print(f"   Arquivos ausentes: {', '.join(missing_files)}")
    sys.exit(1)
else:
    print("✅ SISTEMA VALIDADO COM SUCESSO")
    print("\n📋 Próximos passos:")
    print("   1. Configure suas API keys em config/api_keys.env")
    print("   2. Ajuste os limites de risco em config/risk_limits.yaml")
    print("   3. Execute: python trading_bot.py")
    print("\n⚠️  ATENÇÃO: Inicie sempre em modo TESTNET!")
    print("=" * 70)
