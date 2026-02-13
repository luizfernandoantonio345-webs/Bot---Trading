# 🚀 EXECUTAR NO VS CODE - GUIA COMPLETO

## ✅ Checklist Antes de Começar

- [ ] VS Code instalado
- [ ] Python 3.8+ instalado
- [ ] Conta Binance criada (testnet ou produção)
- [ ] API keys da Binance geradas

---

## 📋 PASSO A PASSO (5 minutos)

### 1️⃣ Abrir o Projeto no VS Code

**Opção A: Via Terminal**
```bash
cd Bot---Trading
code .
```

**Opção B: Pelo VS Code**
- Abra VS Code
- File → Open Folder
- Selecione pasta `Bot---Trading`

---

### 2️⃣ Instalar Extensões (OBRIGATÓRIO)

Quando o VS Code abrir, você verá uma notificação no canto inferior direito:

```
📦 Este workspace tem extensões recomendadas
   [Instalar Tudo]  [Mostrar Recomendações]
```

👉 **Clique em "Instalar Tudo"**

**Aguarde a instalação** (2-3 minutos). Você verá progresso na barra de status.

**Extensões que serão instaladas:**
- Python (Microsoft)
- Pylance (Microsoft)
- Black Formatter
- GitLens
- Error Lens
- E mais 22 extensões úteis

---

### 3️⃣ Selecionar Python Interpreter

1. Pressione `Ctrl+Shift+P` (Windows/Linux) ou `Cmd+Shift+P` (Mac)
2. Digite: `Python: Select Interpreter`
3. Escolha: **Python 3.8** ou superior

**Como encontrar se não aparecer:**
- Windows: `C:\Python3X\python.exe`
- Linux: `/usr/bin/python3`
- Mac: `/usr/local/bin/python3`

---

### 4️⃣ Instalar Dependências

**Abra o Terminal Integrado:**
- Pressione: `Ctrl+'` (Windows/Linux)
- Ou: Menu → Terminal → New Terminal

**Execute:**
```bash
pip install -r requirements.txt
```

**Aguarde instalação** (1-2 minutos)

**Verificação:**
```bash
pip list | grep -E "requests|pandas|numpy"
```

Deve mostrar as bibliotecas instaladas.

---

### 5️⃣ Configurar API Keys

**Copie o arquivo de exemplo:**
```bash
cp .env.example .env
```

**Edite o arquivo .env:**
- No VS Code, clique em `.env` no Explorer
- Ou pressione `Ctrl+P` e digite `.env`

**Configure suas API keys:**

```env
# Binance API Configuration
BINANCE_API_KEY=sua_api_key_aqui
BINANCE_SECRET_KEY=sua_secret_key_aqui

# IMPORTANTE: Comece com TESTNET!
BINANCE_TESTNET=true

# Testnet URLs
BINANCE_TESTNET_API_URL=https://testnet.binance.vision/api
BINANCE_TESTNET_WS_URL=wss://testnet.binance.vision/ws
```

**⚠️ IMPORTANTE:**
- **SEMPRE** comece com `BINANCE_TESTNET=true`
- Obtenha testnet keys em: https://testnet.binance.vision/
- **NUNCA** comite o arquivo `.env` (já está no .gitignore)

**Como obter API Keys da Testnet:**
1. Acesse: https://testnet.binance.vision/
2. Faça login com GitHub
3. Vá em "API Keys" → "Generate HMAC_SHA256 Key"
4. Copie API Key e Secret Key
5. Cole no seu `.env`

---

### 6️⃣ Verificar Setup

**Execute o script de verificação:**

**Opção A: Via Task**
- Pressione: `Ctrl+Shift+P`
- Digite: `Tasks: Run Task`
- Escolha: `✅ Verify Setup`

**Opção B: Via Terminal**
```bash
python verify_setup.py
```

**Você deve ver:**
```
✅ Python 3.8+: Installed
✅ Dependencies: All installed
✅ .env file: Configured
✅ API Keys: Valid
✅ Binance Connection: OK (TESTNET)
✅ Core modules: Available

🎉 Setup completo! Pronto para executar!
```

**Se houver erros:**
- ❌ Python: Instale Python 3.8+
- ❌ Dependencies: Execute `pip install -r requirements.txt`
- ❌ .env: Configure API keys
- ❌ API Keys: Verifique keys no .env
- ❌ Connection: Verifique internet/firewall

---

### 7️⃣ EXECUTAR O BOT! 🚀

**🎯 MÉTODO 1: Debug Mode (RECOMENDADO)**

1. **Abra** `main.py` no editor
2. **Pressione** `F5`
3. **Escolha**: `🚀 Run Trading Bot (Main)`

**Pronto!** O bot iniciará em modo debug.

**Você verá:**
```
═══════════════════════════════════════════
🤖 TRADING BOT PROFISSIONAL
═══════════════════════════════════════════
📊 Mode: TESTNET
⚙️  Strategy: Ensemble
🔒 Risk per trade: 1.0%
═══════════════════════════════════════════

[INFO] Bot iniciado com sucesso
[INFO] Conectando à Binance Testnet...
[INFO] Conexão estabelecida
[INFO] Analisando mercado...
```

**Parar o bot:**
- Pressione: `Shift+F5`
- Ou: Ctrl+C no terminal

---

**🎯 MÉTODO 2: Task Mode (Rápido)**

1. **Pressione** `Ctrl+Shift+B`
2. Bot executa no terminal

---

**🎯 MÉTODO 3: Terminal (Manual)**

1. **Abra terminal**: `Ctrl+'`
2. **Execute**:
```bash
python main.py
```

---

## 🐛 DEBUGGING - Como Usar

### Adicionar Breakpoints

1. **Abra** `main.py` (ou qualquer arquivo)
2. **Clique** à esquerda do número da linha
3. **Aparece** um círculo vermelho 🔴

### Executar em Debug

1. **Pressione** `F5`
2. Bot **para** nos breakpoints
3. **Veja** valores das variáveis

### Controles Durante Debug

```
F5         → Continue (próximo breakpoint)
F10        → Step Over (próxima linha)
F11        → Step Into (entrar função)
Shift+F11  → Step Out (sair função)
Shift+F5   → Stop (parar debug)
```

### Inspecionar Variáveis

**Método 1: Hover**
- Passe mouse sobre variável
- Veja valor atual

**Método 2: Variables Panel**
- Painel à esquerda mostra todas variáveis
- Expanda objetos para ver detalhes

**Método 3: Debug Console**
- Digite código Python
- Teste expressões
- Modifique variáveis

**Exemplo:**
```python
# No Debug Console:
>>> print(signal)
{'signal': 'BUY', 'confidence': 0.75}

>>> data['close']
50000.0
```

---

## ⚡ DICAS PARA DESENVOLVIMENTO

### 1. IntelliSense (Autocompletar)

Digite `.` depois de um objeto:
```python
data.  # ← Aparece lista de métodos
```

Forçar IntelliSense: `Ctrl+Space`

### 2. Formatação Automática

- Salve arquivo: `Ctrl+S`
- Código formata automaticamente com Black
- 120 caracteres por linha

### 3. Problemas em Tempo Real

Erros aparecem:
- Sublinhado vermelho no código
- Panel "Problems": `Ctrl+Shift+M`
- Status bar mostra contagem

### 4. Snippets de Código

Digite prefixo + Tab:

```python
strategy  # + Tab → Template completo de estratégia
logger    # + Tab → Setup de logger
riskcheck # + Tab → Validação de risco
possize   # + Tab → Cálculo de posição
```

### 5. Busca Rápida

```
Ctrl+P        → Abrir arquivo por nome
Ctrl+Shift+F  → Buscar em todos arquivos
Ctrl+G        → Ir para linha específica
F12           → Ir para definição
```

### 6. Git Integrado

```
Ctrl+Shift+G  → Source Control
```
- Veja mudanças
- Commit
- Push/Pull

### 7. Terminal Múltiplo

- `Ctrl+'` → Abrir terminal
- `Ctrl+Shift+'` → Novo terminal
- Dropdown para alternar

---

## 🔧 TASKS DISPONÍVEIS

Acesse: `Ctrl+Shift+P` → "Tasks: Run Task"

```
🚀 Run Trading Bot           → Executa o bot
🌐 Run API Server            → Inicia API REST
✅ Verify Setup              → Verifica configuração
📦 Install Dependencies      → Instala requirements
🧪 Run All Tests             → Executa testes
📊 Run Performance Benchmarks → Medir performance
🧹 Clean Python Cache        → Limpa __pycache__
📝 Format Code with Black    → Formata código
🔍 Lint with Pylint          → Análise de código
```

**Task Padrão** (Ctrl+Shift+B): 🚀 Run Trading Bot

---

## 🚨 TROUBLESHOOTING

### ❌ "Python não encontrado"

**Solução:**
```
1. Instale Python 3.8+
2. Adicione ao PATH
3. Reinicie VS Code
4. Ctrl+Shift+P → "Python: Select Interpreter"
```

### ❌ "Module not found"

**Solução:**
```bash
pip install -r requirements.txt
```

### ❌ "API Key inválida"

**Solução:**
1. Verifique .env tem keys corretas
2. Use testnet keys de: https://testnet.binance.vision/
3. Certifique-se `BINANCE_TESTNET=true`

### ❌ "Connection Error"

**Solução:**
1. Verifique internet
2. Verifique firewall
3. Testnet pode estar offline (raro)

### ❌ "Extensões não funcionam"

**Solução:**
```
1. Ctrl+Shift+X → Extensions
2. Instale "Python" (Microsoft)
3. Reload Window: Ctrl+Shift+P → "Reload Window"
```

### ❌ "Breakpoints não param"

**Solução:**
1. Use F5 (não executar no terminal)
2. Verifique launch.json tem "justMyCode": false

### ❌ "Formatação não funciona"

**Solução:**
```bash
pip install black
```

Depois:
```
Ctrl+Shift+P → "Format Document"
```

---

## 📁 ESTRUTURA DO PROJETO

```
Bot---Trading/
├── .vscode/              # Configurações VS Code
│   ├── settings.json     # Configurações workspace
│   ├── launch.json       # Configurações debug
│   ├── tasks.json        # Tasks automatizadas
│   ├── extensions.json   # Extensões recomendadas
│   └── python.code-snippets  # Snippets personalizados
│
├── core/                 # Módulos principais
│   ├── exceptions.py
│   ├── logger.py
│   ├── cache.py
│   ├── rate_limiter.py
│   ├── circuit_breaker.py
│   ├── binance_connector.py
│   └── position_sizer.py
│
├── main.py              # Executável principal ⭐
├── verify_setup.py      # Verificação de setup ⭐
├── requirements.txt     # Dependências
├── .env.example         # Template configuração
├── .env                 # Suas configurações (criar)
│
└── Documentação/
    ├── COMO_COMECAR_AGORA.md
    ├── VS_CODE_SETUP.md
    ├── VS_CODE_QUICK_START.md
    └── EXECUTAR_NO_VSCODE.md (este arquivo)
```

---

## ✅ CHECKLIST FINAL

Antes de executar, verifique:

- [ ] VS Code aberto na pasta do projeto
- [ ] Extensões recomendadas instaladas
- [ ] Python interpreter selecionado (3.8+)
- [ ] Dependencies instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo .env criado e configurado
- [ ] API keys configuradas (TESTNET!)
- [ ] verify_setup.py executado com sucesso (todos ✅)
- [ ] Testou F5 → Bot iniciou

---

## 🎯 PRÓXIMOS PASSOS

### 1. Primeiro Teste (Testnet)
```
1. F5 para executar
2. Observe logs
3. Veja análises de mercado
4. Deixe rodar 5-10 minutos
5. Ctrl+C para parar
```

### 2. Adicionar Breakpoints
```
1. Abra main.py
2. Linha 50: Click para breakpoint
3. F5 para executar
4. Inspecione variáveis
5. F10 para continuar linha por linha
```

### 3. Modificar Configurações
```
1. Edite .env
2. Mude risk_per_trade
3. Mude símbolos
4. F5 para testar
```

### 4. Ver Documentação Completa
```
- COMO_COMECAR_AGORA.md
- VS_CODE_SETUP.md
- 100_MELHORIAS_BINANCE.md
```

---

## 🎓 APRENDIZADO

### Dia 1: Setup e Primeira Execução
- Configure tudo
- Execute bot em testnet
- Observe comportamento
- Leia logs

### Dia 2-7: Testnet Testing
- Rode bot diariamente
- Monitore performance
- Ajuste parâmetros
- Entenda estratégias

### Semana 2+: Otimização
- Teste diferentes estratégias
- Ajuste risk management
- Backtest resultados
- Considere produção

---

## 📞 AJUDA ADICIONAL

### Documentação Projeto
- [COMO_COMECAR_AGORA.md](COMO_COMECAR_AGORA.md) - Guia geral
- [VS_CODE_SETUP.md](VS_CODE_SETUP.md) - Setup completo
- [VS_CODE_QUICK_START.md](VS_CODE_QUICK_START.md) - Referência rápida

### VS Code Oficial
- [Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [Debugging](https://code.visualstudio.com/docs/python/debugging)
- [Shortcuts](https://code.visualstudio.com/docs/getstarted/keybindings)

### Binance
- [Testnet](https://testnet.binance.vision/)
- [API Docs](https://binance-docs.github.io/apidocs/)

---

## 🎉 PRONTO PARA COMEÇAR!

**Comando final para executar:**

```
Pressione F5 no VS Code
```

**Ou via terminal:**
```bash
python main.py
```

---

**Boa sorte com seu Trading Bot! 🚀📈💰**

**Lembre-se:**
- ⚠️ Sempre testnet primeiro
- 📊 Monitore constantemente
- 🔒 Gestão de risco é #1
- 📚 Leia documentação
- 🧪 Teste antes de produção
