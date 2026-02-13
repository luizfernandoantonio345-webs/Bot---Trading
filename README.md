# 🤖 TRADING BOT PROFISSIONAL

Sistema de trading automatizado pronto para produção real com análise multicamadas, gestão de risco rigorosa, aprendizado automático e integração com Binance.

## ⚠️ ATENÇÃO

**Este bot opera em CONTA REAL. Configure corretamente antes de executar.**

## 🏗️ Arquitetura

```
/core
  ├── market_analyzer.py      # Análise multicamadas de mercado
  ├── pattern_engine.py       # Detecção de padrões técnicos
  ├── score_engine.py         # Sistema de pontuação 0-100
  ├── risk_manager.py         # Gestão de risco inviolável
  ├── execution_engine.py     # Integração Binance
  ├── memory_engine.py        # Armazenamento de trades
  ├── learning_engine.py      # Aprendizado automático
  └── logger.py               # Sistema de logs profissional

/config
  ├── api_keys.env           # API keys Binance
  ├── risk_limits.yaml       # Limites de risco
  └── weights.yaml           # Pesos do score

/logs                        # Logs com rotação automática

trading_bot.py              # Orquestrador principal
```

## 📊 Funcionalidades

### Análise de Mercado
- Estrutura (HH, HL, LH, LL)
- Tendência macro e micro
- Momentum real
- Volatilidade vs histórica
- Volume e fluxo
- Liquidez
- Sessão de mercado
- Contexto temporal

### Sistema de Score (0-100)
- **< 65**: NÃO OPERAR
- **65-89**: ALERTA APENAS  
- **≥ 90**: EXECUÇÃO AUTOMÁTICA

Componentes:
- Tendência: 25 pontos
- Momentum: 20 pontos
- Confirmações: 25 pontos
- Qualidade de risco: 20 pontos
- Contexto: 10 pontos

### Gestão de Risco
- Limite de loss diário/semanal/mensal
- Redução automática de lote após loss
- Pausa automática após sequência negativa
- Drawdown máximo
- Exposição controlada
- **Capital preservation > lucro**

### Aprendizado
- Armazena todos os trades
- Identifica padrões vencedores/perdedores
- Penaliza padrões ruins automaticamente
- Reforça padrões vencedores
- Ajusta agressividade dinamicamente

## 🚀 Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar API Keys

Edite `config/api_keys.env`:

```env
BINANCE_API_KEY=sua_chave_aqui
BINANCE_API_SECRET=seu_secret_aqui
USE_TESTNET=True  # False para produção
IS_FUTURES=True   # False para Spot
PRIMARY_SYMBOL=BTCUSDT
```

### 3. Ajustar Limites de Risco

Edite `config/risk_limits.yaml`:

```yaml
max_daily_loss: 500.0
max_weekly_loss: 1500.0
max_trades_per_day: 10
max_consecutive_losses: 3
```

### 4. Personalizar Pesos (Opcional)

Edite `config/weights.yaml` para ajustar pesos do score.

## ▶️ Execução

```bash
python trading_bot.py
```

## 🛡️ Segurança

- ✅ Validação de ordens
- ✅ Confirmação de fills
- ✅ Reconciliação de estado
- ✅ Controle de latência
- ✅ Limites rígidos de risco
- ✅ Pausas automáticas
- ✅ Logs completos

## 📈 Monitoramento

Os logs são salvos em:
- `logs/trades.log` - Histórico de trades
- `logs/errors.log` - Erros e exceções
- `logs/learning.log` - Insights de aprendizado
- `logs/system.log` - Eventos do sistema

Database SQLite:
- `trade_memory.db` - Histórico completo de trades

## 🎯 Estratégia

O bot opera baseado em:

1. **Análise multicamadas**: Avalia mercado em múltiplos timeframes
2. **Confirmações técnicas**: Exige múltiplas confirmações antes de operar
3. **Score rigoroso**: Apenas setups com score ≥ 90 são executados
4. **Risco controlado**: Nunca arrisca mais do que os limites definidos
5. **Aprendizado contínuo**: Adapta-se com base em resultados históricos

## ⚙️ Personalização

### Ajustar Agressividade

Edite `config/weights.yaml`:

```yaml
threshold_alert: 85  # Reduzir para ser mais agressivo
```

### Ajustar Risco

Edite `config/risk_limits.yaml`:

```yaml
base_position_size: 0.02  # Aumentar tamanho de posição
```

## 🧪 Modo Testnet

Para testar sem risco:

```env
USE_TESTNET=True
```

## 📊 Performance

Para ver estatísticas:

```python
from core.memory_engine import MemoryEngine

memory = MemoryEngine()
stats = memory.get_statistics(days=30)
print(stats)
```

## 🚨 Avisos Importantes

1. **RISCO**: Trading envolve risco de perda total
2. **RESPONSABILIDADE**: Use por sua conta e risco
3. **TESTES**: Teste extensivamente em testnet primeiro
4. **MONITORAMENTO**: Monitore o bot regularmente
5. **CAPITAL**: Opere apenas com capital que pode perder

## 📝 Licença

Este é um sistema profissional para trading real. Use com responsabilidade.

## 🤝 Suporte

Para dúvidas ou problemas:
- Consulte os logs em `/logs`
- Verifique o histórico em `trade_memory.db`
- Ajuste configurações conforme necessário

## 💡 Ideias Futuras

Confira o documento [IDEAS_FUTURAS.md](IDEAS_FUTURAS.md) com **10 ideias estratégicas** para evolução do bot:
- Sistema de Aprendizado por Reforço
- Dashboard Web Interativo
- Notificações Multi-Canal
- Múltiplas Estratégias Paralelas
- Backtesting Engine Avançado
- E muito mais!

---

**⚡ BOT PRONTO PARA PRODUÇÃO ⚡**
