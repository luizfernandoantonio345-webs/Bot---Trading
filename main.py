#!/usr/bin/env python3
"""
🤖 BOT TRADING - ENTRY POINT SIMPLIFICADO
==========================================

Ponto de entrada principal para iniciar o bot de trading.
Execute: python3 main.py

"""

import os
import sys
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_bot.log') if os.path.exists('logs') or os.makedirs('logs', exist_ok=True) else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def print_banner():
    """Exibe banner de inicialização"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         🤖  BOT TRADING PROFISSIONAL                      ║
    ║         Versão 2.0 - Institutional Grade                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"    📅 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"    🐍 Python: {sys.version.split()[0]}")
    print()


def check_configuration():
    """Verifica se a configuração está completa"""
    required_vars = ['BINANCE_API_KEY', 'BINANCE_API_SECRET']
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        logger.error(f"❌ Variáveis de ambiente faltando: {', '.join(missing)}")
        logger.error("   Configure o arquivo .env antes de continuar.")
        logger.error("   Execute: cp .env.example .env")
        return False
    
    # Verificar modo
    use_testnet = os.getenv('USE_TESTNET', 'True').lower() == 'true'
    mode = "TESTNET 🧪" if use_testnet else "PRODUÇÃO ⚠️"
    
    logger.info(f"✅ Configuração carregada")
    logger.info(f"   Modo: {mode}")
    logger.info(f"   Par: {os.getenv('PRIMARY_SYMBOL', 'BTCUSDT')}")
    logger.info(f"   Risk/Trade: {os.getenv('RISK_PER_TRADE', '0.01')}")
    
    if not use_testnet:
        logger.warning("⚠️  ATENÇÃO: Você está em MODO PRODUÇÃO!")
        logger.warning("   Certifique-se de ter testado suficientemente no testnet.")
        response = input("   Continuar? (digite 'SIM' para confirmar): ")
        if response != 'SIM':
            logger.info("Abortado pelo usuário.")
            return False
    
    return True


def run_simple_strategy():
    """Executa estratégia simples de trading"""
    try:
        from binance.client import Client
        from ensemble_strategy import create_ensemble_strategy
        import numpy as np
        
        # Criar cliente Binance
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        use_testnet = os.getenv('USE_TESTNET', 'True').lower() == 'true'
        
        client = Client(api_key, api_secret, testnet=use_testnet)
        
        # Testar conexão
        logger.info("🔌 Testando conexão com Binance...")
        server_time = client.get_server_time()
        logger.info(f"✅ Conectado! Server time: {server_time['serverTime']}")
        
        # Obter info da conta
        account = client.get_account()
        logger.info(f"💰 Saldo da conta carregado")
        
        # Criar estratégia ensemble
        logger.info("🧠 Carregando estratégia de trading...")
        ensemble = create_ensemble_strategy()
        logger.info("✅ Estratégia ensemble carregada")
        
        # Símbolo para trading
        symbol = os.getenv('PRIMARY_SYMBOL', 'BTCUSDT')
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 BOT INICIADO - Aguardando sinais de trading...")
        logger.info(f"📊 Símbolo: {symbol}")
        logger.info(f"⏱️  Intervalo de verificação: 60 segundos")
        logger.info(f"{'='*60}\n")
        
        # Loop principal
        iteration = 0
        while True:
            try:
                iteration += 1
                logger.info(f"🔄 Iteração #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Obter dados de mercado
                klines = client.get_klines(symbol=symbol, interval='15m', limit=100)
                
                # Converter para arrays numpy
                closes = np.array([float(k[4]) for k in klines])
                highs = np.array([float(k[2]) for k in klines])
                lows = np.array([float(k[3]) for k in klines])
                opens = np.array([float(k[1]) for k in klines])
                volumes = np.array([float(k[5]) for k in klines])
                
                market_data = {
                    'open': opens,
                    'high': highs,
                    'low': lows,
                    'close': closes,
                    'volume': volumes
                }
                
                # Analisar com ensemble
                analysis = ensemble.analyze(market_data)
                
                signal = analysis.get('final_signal', 'NEUTRAL')
                score = analysis.get('final_score', 0)
                confidence = analysis.get('confidence', 0)
                
                logger.info(f"   📈 Preço atual: ${closes[-1]:.2f}")
                logger.info(f"   🎯 Sinal: {signal} | Score: {score:.1f} | Confiança: {confidence:.1f}%")
                
                # Verificar se deve executar
                min_confidence = float(os.getenv('MIN_CONFIDENCE', '70'))
                if ensemble.should_execute_trade(analysis, min_confidence=min_confidence):
                    logger.info(f"   ✅ SINAL DE TRADE DETECTADO!")
                    logger.info(f"   📌 Sinal: {signal} com {confidence:.1f}% de confiança")
                    
                    # Em produção real, executaria o trade aqui
                    # Por enquanto, apenas loga
                    logger.info(f"   ℹ️  Modo demonstração - trade NÃO executado")
                    logger.info(f"   ℹ️  Para executar trades reais, implemente lógica de execução")
                else:
                    logger.info(f"   ⏸️  Aguardando condições ideais (confiança < {min_confidence}%)")
                
                # Aguardar próxima iteração
                logger.info(f"   ⏳ Próxima verificação em 60 segundos...\n")
                time.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("\n⚠️  Interrupção detectada (Ctrl+C)")
                raise
            except Exception as e:
                logger.error(f"❌ Erro na iteração: {e}")
                logger.info("   Tentando novamente em 60 segundos...")
                time.sleep(60)
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot interrompido pelo usuário")
        logger.info("   Encerrando gracefully...")
    except ImportError as e:
        logger.error(f"❌ Erro ao importar módulos: {e}")
        logger.error("   Instale as dependências: pip3 install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


def run_api_mode():
    """Executa o bot em modo API (FastAPI)"""
    try:
        logger.info("🌐 Iniciando em modo API...")
        logger.info("   Acesse: http://localhost:8000/docs")
        
        import uvicorn
        uvicorn.run("main_api:app", host="0.0.0.0", port=8000, reload=False)
    except ImportError:
        logger.error("❌ FastAPI não instalado")
        logger.error("   Instale: pip3 install fastapi uvicorn")
        sys.exit(1)


def main():
    """Função principal"""
    print_banner()
    
    # Verificar configuração
    if not check_configuration():
        sys.exit(1)
    
    # Determinar modo de execução
    mode = os.getenv('EXECUTION_MODE', 'simple').lower()
    
    if mode == 'api':
        run_api_mode()
    else:
        run_simple_strategy()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Até logo!")
        sys.exit(0)
