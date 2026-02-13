"""
═══════════════════════════════════════════════════════════════════
GUIA COMPLETO - SISTEMAS INTEGRADOS
═══════════════════════════════════════════════════════════════════

O bot trading agora possui 3 sistemas integrados:

1️⃣  TRADING BOT (trading_bot.py)
   └─ Core profissional com análise multicamadas
   └─ Execução real em Binance
   └─ Gestão de risco inviolável

2️⃣  REST API (main_api.py)
   └─ Endpoints para controlar o bot
   └─ Monitoramento dos engines de IA
   └─ Histórico de decisões

3️⃣  LINHA DE COMANDO (utils.py)
   └─ Análise de padrões
   └─ Estatísticas de trading
   └─ Exportação de dados

═══════════════════════════════════════════════════════════════════
INICIALIZAÇÃO RÁPIDA
═══════════════════════════════════════════════════════════════════

PASSO 1: Instalar dependências
$ pip install -r requirements.txt

PASSO 2: Configurar API keys
$ nano config/api_keys.env
  - Adicione suas credenciais Binance
  - USE_TESTNET=True (para testes)

PASSO 3: (Opcional) Iniciar API REST
$ python run_api.py
  - Acessar http://localhost:8000/docs

PASSO 4: Iniciar Bot
$ python trading_bot.py
  - Bot rodará em loop analisando mercado

PASSO 5: (Opcional) Monitorar com utils
$ python utils.py stats           # Estatísticas
$ python utils.py best-patterns   # Padrões vencedores
$ python utils.py risk            # Status de risco

═══════════════════════════════════════════════════════════════════
ENDPOINTS PRINCIPAIS
═══════════════════════════════════════════════════════════════════

OPERAÇÃO DE TRADES:
  POST /buy            - {"volume": 0.01}
  POST /sell           - {"volume": 0.01}
  POST /close          - Fechar posição atual
  GET  /position       - Status da posição

MONITORAMENTO:
  GET  /health                     - Status básico
  GET  /state                      - Estado completo
  GET  /api/ai/health              - Saúde dos engines
  GET  /api/ai/decision/latest     - Última decisão

ANÁLISE:
  GET  /api/ai/engines/status              - Todos os engines
  GET  /api/ai/engines/{engine_id}/status  - Engine específico
  GET  /api/ai/decisions/export            - Histórico
  GET  /api/ai/engine-performance          - Performance

CONTROLE:
  POST /pause          - Pausar bot
  POST /resume         - Retomar bot

═══════════════════════════════════════════════════════════════════
ARQUITETURA TÉCNICA
═══════════════════════════════════════════════════════════════════

CORE MODULES:
├── market_analyzer.py      (587 linhas) - Análise multicamadas
├── pattern_engine.py       (870 linhas) - 13 padrões detectados
├── score_engine.py         (464 linhas) - Score 0-100
├── risk_manager.py         (569 linhas) - Gestão rigorosa
├── execution_engine.py     (519 linhas) - Binance Spot/Futures
├── memory_engine.py        (444 linhas) - SQLite persistente
├── learning_engine.py      (429 linhas) - Aprendizado automático
└── logger.py               (327 linhas) - Logging profissional

CONFIG:
├── api_keys.env            - Credenciais Binance
├── risk_limits.yaml        - Parâmetros de risco
└── weights.yaml            - Pesos dos componentes

OUTPUT:
├── logs/                   - Arquivos de log
├── data/                   - Histórico de trades
└── state.json              - Estado persistente

═══════════════════════════════════════════════════════════════════
FLUXO DE DECISÃO
═══════════════════════════════════════════════════════════════════

1. VALIDAÇÃO DE RISCO
   ↓
2. BUSCA DE DADOS (5 timeframes)
   ↓
3. ANÁLISE DE MERCADO (7 dimensões)
   ↓
4. DETECÇÃO DE PADRÕES (13 tipos)
   ↓
5. INSIGHTS DE APRENDIZADO
   ↓
6. CÁLCULO DE SCORE (0-100)
   ↓
7. DECISÃO
   ├─ Score < 65: NO_TRADE
   ├─ 65-89: ALERT_ONLY
   └─ ≥90: EXECUTE

═══════════════════════════════════════════════════════════════════
MONITORAMENTO EM TEMPO REAL
═══════════════════════════════════════════════════════════════════

Logs disponíveis em /logs:
  • trades.log       - Entrada/saída de trades
  • errors.log       - Erros e exceções
  • learning.log     - Insights de aprendizado
  • system.log       - Eventos do sistema

Dashboard API:
  http://localhost:8000/docs
  - Teste endpoints interativamente
  - Veja responses em tempo real

Análise CLI:
  python utils.py stats
  - Win rate, profit factor, sharpe ratio
  - Comparação de períodos

═══════════════════════════════════════════════════════════════════
SEGURANÇA & BOAS PRÁTICAS
═══════════════════════════════════════════════════════════════════

✅ SEMPRE FAZER:
  1. Começar com USE_TESTNET=True
  2. Testar por 1-2 semanas antes de produção
  3. Usar risk_limits conservadores inicialmente
  4. Monitorar logs regularmente
  5. Validar configurações antes de executar

❌ NUNCA FAZER:
  1. Usar credenciais reais sem testnet primeiro
  2. Aumentar limites de risco drasticamente
  3. Desabilitar stop loss
  4. Ignorar alertas do bot
  5. Deixar bot sem monitoramento

⚠️  EMERGÊNCIA:
  1. Ctrl+C - Para o bot graciosamente
  2. POST /close - Fecha posição aberta
  3. POST /pause - Pausa operações (não encerra)
  4. Verifique /logs para diagnosticar

═══════════════════════════════════════════════════════════════════
TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════

Problema: "Import fastapi could not be resolved"
Solução: pip install -r requirements.txt

Problema: "Binance API error"
Solução: Verifique API keys em config/api_keys.env

Problema: "Trading blocked - risk limit exceeded"
Solução: Verifique risk_limits.yaml ou aguarde reset diário

Problema: "No market data available"
Solução: Verifique conexão internet, símbolo correto

Problema: Bot trava
Solução: Verifique logs/, pressione Ctrl+C, reinicie

═══════════════════════════════════════════════════════════════════
SUPORTE
═══════════════════════════════════════════════════════════════════

Documentação: Ver README.md, QUICKSTART.md
Exemplos: Ver examples.py
Validação: python test_system.py
Performance: python utils.py stats

Sistema pronto para PRODUÇÃO! 🚀
"""

def show_help():
    import sys
    with open(__file__, 'r', encoding='utf-8') as f:
        content = f.read()
        # Extrair seção docstring
        print(content.split('def show_help')[0])

if __name__ == "__main__":
    show_help()
