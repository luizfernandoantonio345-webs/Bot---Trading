# 🚀 GUIA DE INÍCIO RÁPIDO

## ⚡ Setup em 5 Minutos

### 1. Instalar Dependências (1 min)

```bash
pip install -r requirements.txt
```

### 2. Configurar API Binance (2 min)

Edite `config/api_keys.env`:

```env
BINANCE_API_KEY=sua_chave_aqui
BINANCE_API_SECRET=seu_secret_aqui
USE_TESTNET=True
IS_FUTURES=True
PRIMARY_SYMBOL=BTCUSDT
```

**Como obter API keys:**
1. Acesse [Binance](https://www.binance.com) ou [Binance Testnet](https://testnet.binancefuture.com)
2. Vá em Conta → API Management
3. Crie nova API key
4. **IMPORTANTE**: Habilite permissões de trading

### 3. Ajustar Limites de Risco (1 min)

Edite `config/risk_limits.yaml`:

```yaml
max_daily_loss: 500.0        # Ajuste conforme seu capital
max_weekly_loss: 1500.0
base_position_size: 0.01     # Tamanho inicial de posição
```

### 4. Executar Bot (1 min)

```bash
python trading_bot.py
```

---

## 📊 Comandos Úteis

### Ver Estatísticas

```bash
python utils.py stats --days 30
```

### Ver Melhores Padrões

```bash
python utils.py best-patterns
```

### Ver Piores Padrões (para evitar)

```bash
python utils.py worst-patterns
```

### Exportar Trades

```bash
python utils.py export
```

### Ver Status de Risco

```bash
python utils.py risk
```

### Ver Insights de Aprendizado

```bash
python utils.py learning
```

---

## 🎯 Primeiros Passos Recomendados

### 1. **TESTE EM TESTNET PRIMEIRO**

```env
USE_TESTNET=True
```

Execute por pelo menos 1-2 semanas em testnet antes de usar conta real.

### 2. **Comece Conservador**

```yaml
# config/risk_limits.yaml
max_daily_loss: 100.0        # Baixo
base_position_size: 0.001    # Muito pequeno
threshold_alert: 95          # Muito rigoroso
```

### 3. **Monitore Constantemente**

- Acompanhe logs em `logs/`
- Verifique trades em `trade_memory.db`
- Execute `python utils.py stats` regularmente

### 4. **Ajuste Gradualmente**

Após performance consistente:
- Aumente position size gradualmente
- Reduza threshold_alert (se quiser mais trades)
- Aumente limites de risco (cautelosamente)

---

## ⚙️ Configurações Principais

### Agressividade

**Conservador** (Recomendado para início):
```yaml
threshold_alert: 95
base_position_size: 0.001
max_trades_per_day: 3
```

**Moderado**:
```yaml
threshold_alert: 90
base_position_size: 0.01
max_trades_per_day: 10
```

**Agressivo** (Apenas após consistência provada):
```yaml
threshold_alert: 85
base_position_size: 0.05
max_trades_per_day: 20
```

---

## 🛡️ Checklist de Segurança

Antes de executar em conta real:

- [ ] Testado extensivamente em testnet
- [ ] Limites de risco configurados apropriadamente
- [ ] Capital usado é dispensável (pode perder)
- [ ] Sistema de monitoramento configurado
- [ ] Backups de configuração feitos
- [ ] Entendimento completo de como o bot funciona
- [ ] Plano de ação para emergências

---

## 📈 Métricas de Sucesso

### Indicadores de Performance Saudável:

- **Win Rate**: > 55%
- **Profit Factor**: > 1.5
- **Drawdown Máximo**: < 15%
- **Trades por Dia**: Moderado (não muitos nem poucos)
- **P&L Consistente**: Crescimento gradual sem grandes oscilações

### Sinais de Alerta:

- Win Rate < 45%
- Losses consecutivos > 3
- Drawdown > 15%
- P&L muito volátil
- Muitos trades rejeitados

**Ação em caso de sinais de alerta:** PARE, analise, ajuste, reteste em testnet.

---

## 🔧 Troubleshooting

### Bot não executa trades

**Possíveis causas:**
1. Score sempre < threshold
   - Solução: Reduzir threshold ou ajustar pesos
2. Risk manager bloqueando
   - Solução: Verificar `python utils.py risk`
3. Sem oportunidades válidas
   - Solução: Normal, aguardar

### Muitos erros de API

**Possíveis causas:**
1. API keys incorretas
2. Permissões insuficientes
3. Rate limit excedido
4. Testnet/Produção conflito

**Solução:** Verificar logs em `logs/errors.log`

### Desempenho ruim

**Ações:**
1. Analisar padrões perdedores: `python utils.py worst-patterns`
2. Verificar se está operando em horários ruins
3. Revisar parâmetros de score em `config/weights.yaml`
4. Dar tempo para learning engine aprender (mínimo 50-100 trades)

---

## 📞 Próximos Passos

1. **Semana 1-2**: Testnet + Ajustes
2. **Semana 3-4**: Testnet + Validação de Performance
3. **Semana 5+**: Conta Real (capital pequeno)
4. **Mês 2+**: Escala gradual conforme consistência

---

## ⚡ Comandos de Emergência

### Parar Bot Imediatamente

```
Ctrl + C
```

O bot fechará posições e parará graciosamente.

### Pausar Manualmente

Edite o arquivo de estado ou use interface (se implementada).

---

**🎓 LEMBRE-SE:**

> O melhor trade é o que você NÃO faz quando não há vantagem clara.

> Proteger capital > fazer lucro.

> Consistência > home runs.

---

✅ **Sistema pronto. BOA SORTE E TRADE SAFE!** 🚀
