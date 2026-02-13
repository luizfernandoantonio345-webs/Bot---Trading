# ⚡ VS Code - Guia Rápido Visual

## 🎯 Primeiros Passos (2 minutos)

### 1️⃣ Abrir o Projeto
```bash
cd Bot---Trading
code .
```

### 2️⃣ Instalar Extensões Recomendadas
Quando o VS Code abrir, você verá uma notificação:
```
"Este workspace tem extensões recomendadas"
```
👉 Clique em **"Instalar Tudo"**

**OU manualmente:**
- Pressione: `Ctrl+Shift+X`
- Veja extensões recomendadas no topo
- Clique "Install" em cada uma

### 3️⃣ Selecionar Python Interpreter
- Pressione: `Ctrl+Shift+P`
- Digite: `Python: Select Interpreter`
- Escolha: Python 3.8 ou superior

---

## 🚀 Executar o Bot (3 formas)

### Forma 1: Debug Mode (Recomendado)
```
Pressione: F5
Escolha: "🚀 Run Trading Bot (Main)"
```
✅ Permite inspecionar variáveis
✅ Pode pausar execução
✅ Vê valores em tempo real

### Forma 2: Task (Rápido)
```
Pressione: Ctrl+Shift+B
```
✅ Execução rápida
✅ Output no terminal

### Forma 3: Terminal Integrado
```
Pressione: Ctrl+`
Digite: python3 main.py
```

---

## 🐛 Debugging - Passo a Passo

### Adicionar Breakpoint
1. Abra arquivo (ex: `main.py`)
2. Clique à **esquerda do número da linha**
3. Aparece um **círculo vermelho** 🔴

### Iniciar Debug
1. Pressione `F5`
2. Bot roda até o breakpoint
3. Execução **pausa** no breakpoint

### Controles de Debug
| Tecla | Ação | Descrição |
|-------|------|-----------|
| `F5` | Continue | Continua até próximo breakpoint |
| `F10` | Step Over | Executa linha atual |
| `F11` | Step Into | Entra na função |
| `Shift+F11` | Step Out | Sai da função |
| `Shift+F5` | Stop | Para debug |

### Inspecionar Variáveis
- **Hover**: Passe mouse sobre variável
- **Panel Variables**: Veja todas variáveis (lado esquerdo)
- **Debug Console**: Digite código para testar

---

## ⌨️ Atalhos Essenciais

### Navegação
```
Ctrl+P          → Abrir arquivo rápido
Ctrl+Shift+F    → Buscar em arquivos
Ctrl+G          → Ir para linha
F12             → Ir para definição
Alt+Left/Right  → Voltar/Avançar
```

### Edição
```
Ctrl+Space      → IntelliSense (autocompletar)
Ctrl+.          → Quick Fix (sugestões)
Alt+Shift+F     → Formatar código
Ctrl+/          → Comentar linha
Ctrl+D          → Selecionar próxima ocorrência
Alt+Up/Down     → Mover linha
```

### Terminal
```
Ctrl+`          → Abrir/fechar terminal
Ctrl+Shift+`    → Novo terminal
```

### Tasks
```
Ctrl+Shift+B    → Run build task (bot)
Ctrl+Shift+P    → Command Palette (todos comandos)
```

---

## 📝 Snippets de Código

### Como Usar Snippets
1. Comece a digitar o prefixo
2. Aparece sugestão
3. Pressione `Tab` para expandir

### Snippets Disponíveis

#### `strategy` + Tab
```python
def strategy_name(data: dict) -> dict:
    """Strategy description"""
    close = data['close']
    # Your indicators here
    return {'signal': 'NEUTRAL', 'confidence': 0}
```

#### `riskcheck` + Tab
```python
if condition:
    logger.warning('Risk limit exceeded')
    return False
```

#### `logger` + Tab
```python
import logging
logger = logging.getLogger(__name__)
```

#### `possize` + Tab
```python
from core.position_sizer import PositionSizer
sizer = PositionSizer()
result = sizer.calculate(...)
```

#### Todos os Snippets
- `strategy` - Trading strategy template
- `riskcheck` - Risk validation
- `tryb` - Try-except Binance
- `logger` - Logger setup
- `possize` - Position sizing
- `ratelimit` - Rate limit check
- `breaker` - Circuit breaker
- `cache` - Cache decorator
- `config` - Config manager
- `signal` - Signal dict
- `test` - Test function
- `main` - Main guard
- `botloop` - Bot main loop

---

## 🎨 Interface Visual

### Panel Esquerdo
```
📁 Explorer        → Arquivos do projeto
🔍 Search          → Buscar em arquivos
🔀 Source Control  → Git (commits, diff)
🐛 Run and Debug   → Debug controls
🧩 Extensions      → Gerenciar extensões
```

### Panel Inferior
```
⚠️ Problems    → Erros e warnings
📤 Output      → Output de tasks/extensões
🐛 Debug Console → Console durante debug
🖥️ Terminal    → Terminal integrado
```

### Status Bar (Embaixo)
```
🐍 Python 3.x     → Click para trocar interpreter
⚡ Pylint         → Status do linting
🔧 Black          → Formatter status
🌿 main           → Branch atual Git
```

---

## 🔧 Tasks Rápidas

### Acessar Tasks
```
Ctrl+Shift+P → "Tasks: Run Task"
```

### Tasks Disponíveis
```
🚀 Run Trading Bot          → Inicia o bot
🌐 Run API Server           → Inicia API
✅ Verify Setup             → Verifica configuração
📦 Install Dependencies     → Instala requirements.txt
🧪 Run All Tests            → Executa pytest
📊 Run Performance Benchmarks → Benchmarks
🧹 Clean Python Cache       → Remove __pycache__
📝 Format Code with Black   → Formata todo código
🔍 Lint with Pylint         → Análise de código
📋 Create Virtual Environment → Cria venv
🔄 Update Requirements      → Atualiza requirements.txt
```

### Task Padrão (Ctrl+Shift+B)
```
🚀 Run Trading Bot
```

---

## 💡 Dicas Rápidas

### 1. Formatação Automática
Código formata automaticamente ao salvar!
- Ctrl+S salva e formata
- Usa Black (120 char line length)

### 2. IntelliSense Inteligente
Digite `.` depois de objeto para ver métodos:
```python
data.   # ← IntelliSense mostra: keys(), values(), items()...
```

### 3. Problemas em Tempo Real
Erros aparecem:
- ❌ Sublinhado vermelho no código
- ⚠️ Panel "Problems" (Ctrl+Shift+M)
- 🔴 Status bar mostra contagem

### 4. Multi-Cursor
Selecione múltiplas linhas:
- Alt+Click em cada lugar
- Ctrl+D seleciona próxima ocorrência
- Ctrl+Alt+Up/Down cursor acima/abaixo

### 5. Git Integrado
Ver mudanças:
- Ctrl+Shift+G → Source Control
- Click em arquivo para ver diff
- Stage changes → Commit → Push

### 6. Split Editor
Ver múltiplos arquivos:
- Ctrl+\ → Split editor
- Arraste arquivo para lado
- Ctrl+1, Ctrl+2 para alternar

---

## 🚨 Troubleshooting Rápido

### Python não encontrado
```
Solução:
Ctrl+Shift+P → "Python: Select Interpreter"
Escolha Python 3.8+
```

### IntelliSense não funciona
```
Solução:
Ctrl+Shift+P → "Reload Window"
Ou instale extensão Pylance
```

### Formatação não automática
```
Solução:
Verifique settings.json tem:
"editor.formatOnSave": true
```

### Tasks não aparecem
```
Solução:
Verifique .vscode/tasks.json existe
Reload window se necessário
```

### Breakpoints não param
```
Solução:
Certifique-se está usando F5 (não executar no terminal)
"justMyCode" deve estar false em launch.json
```

---

## 📱 Cheat Sheet Visual

```
┌─────────────────────────────────────────────────────────────┐
│  VS CODE TRADING BOT - CHEAT SHEET                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🚀 EXECUTAR BOT                                             │
│     F5                    → Debug mode                       │
│     Ctrl+Shift+B          → Task mode                        │
│     Ctrl+`  python3 main.py → Terminal mode                  │
│                                                              │
│  🐛 DEBUGGING                                                │
│     Click linha           → Breakpoint                       │
│     F5                    → Start                            │
│     F10                   → Step over                        │
│     F11                   → Step into                        │
│     Shift+F5              → Stop                             │
│                                                              │
│  📝 EDIÇÃO                                                   │
│     Ctrl+Space            → IntelliSense                     │
│     Ctrl+.                → Quick fix                        │
│     Alt+Shift+F           → Format                           │
│     Ctrl+/                → Comment                          │
│                                                              │
│  🔍 NAVEGAÇÃO                                                │
│     Ctrl+P                → Quick open                       │
│     Ctrl+Shift+F          → Find in files                    │
│     F12                   → Go to definition                 │
│                                                              │
│  ⚡ SNIPPETS                                                 │
│     strategy + Tab        → Strategy template                │
│     riskcheck + Tab       → Risk check                       │
│     logger + Tab          → Logger setup                     │
│     possize + Tab         → Position sizing                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Workflow Recomendado

### Desenvolvimento Diário
```
1. Abrir VS Code (code .)
2. Pull últimas mudanças (Source Control)
3. Criar branch (se nova feature)
4. Editar código (com IntelliSense)
5. Testar com F5 (debug mode)
6. Formatar (Ctrl+S auto-formata)
7. Commit (Source Control)
8. Push
```

### Debugging de Problema
```
1. Adicionar breakpoints onde suspeita erro
2. F5 para debug
3. Inspecionar variáveis no breakpoint
4. F10 para ir linha por linha
5. Debug Console para testar hipóteses
6. Corrigir código
7. F5 novamente para validar
```

### Testing
```
1. Escrever teste (snippet: test + Tab)
2. Task: "🧪 Run All Tests"
3. Ver output no terminal
4. Corrigir falhas
5. Repeat
```

---

## ✅ Setup Completo Checklist

- [ ] VS Code instalado
- [ ] Projeto aberto (code .)
- [ ] Extensões recomendadas instaladas
- [ ] Python interpreter selecionado
- [ ] Testou F5 (debug funciona)
- [ ] Testou Ctrl+Shift+B (task funciona)
- [ ] IntelliSense funcionando (Ctrl+Space)
- [ ] Formatação automática (salvar formata)
- [ ] Leu VS_CODE_SETUP.md
- [ ] Conhece atalhos principais

---

## 🎓 Próximos Passos

1. **Explore snippets**: Digite cada snippet para ver
2. **Configure preferências**: Ctrl+, para settings
3. **Personalize tema**: Ctrl+K Ctrl+T
4. **Instale mais extensões**: Ctrl+Shift+X
5. **Leia documentação completa**: VS_CODE_SETUP.md

---

**🎉 Pronto! Você agora tem ambiente profissional de desenvolvimento!**

**Comece:** Pressione `F5` para executar o bot em modo debug! 🚀
