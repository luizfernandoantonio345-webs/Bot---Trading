# 🔧 Guia de Configuração VS Code para Trading Bot

## 📋 Índice
1. [Configuração Inicial](#configuração-inicial)
2. [Extensões Recomendadas](#extensões-recomendadas)
3. [Atalhos e Comandos](#atalhos-e-comandos)
4. [Debugging](#debugging)
5. [Tasks (Tarefas)](#tasks-tarefas)
6. [Dicas e Truques](#dicas-e-truques)

---

## 🚀 Configuração Inicial

### 1. Instalação do VS Code
Se ainda não tem o VS Code instalado:
- **Windows/Mac**: [Baixar VS Code](https://code.visualstudio.com/)
- **Linux**: `sudo snap install code --classic`

### 2. Abrir o Projeto
```bash
cd Bot---Trading
code .
```

### 3. Instalar Extensões Recomendadas
Quando abrir o projeto, o VS Code vai sugerir extensões recomendadas.
Clique em **"Install All"** na notificação que aparecer.

**Ou instale manualmente:**
1. Pressione `Ctrl+Shift+X` (Windows/Linux) ou `Cmd+Shift+X` (Mac)
2. O VS Code mostrará as extensões recomendadas
3. Clique em "Install" em cada uma

### 4. Configurar Python Interpreter
1. Pressione `Ctrl+Shift+P` (Windows/Linux) ou `Cmd+Shift+P` (Mac)
2. Digite "Python: Select Interpreter"
3. Escolha o interpretador Python 3.8+ instalado no seu sistema

**Se usar ambiente virtual (venv):**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

Depois selecione `./venv/bin/python` como interpreter no VS Code.

---

## 🧩 Extensões Recomendadas

### Essenciais (Python)
- ✅ **Python** - Suporte completo Python
- ✅ **Pylance** - IntelliSense rápido e preciso
- ✅ **Black Formatter** - Formatação automática de código
- ✅ **Pylint** - Análise de código
- ✅ **Flake8** - Verificação de estilo

### Produtividade
- ✅ **Error Lens** - Mostra erros inline no código
- ✅ **GitLens** - Recursos avançados de Git
- ✅ **Better Comments** - Destaca comentários importantes
- ✅ **Todo Tree** - Visualiza TODOs no código
- ✅ **Bookmarks** - Marca pontos importantes

### Markdown
- ✅ **Markdown All in One** - Edição melhorada de .md
- ✅ **Markdown Preview Enhanced** - Preview avançado

### Outros
- ✅ **DotEnv** - Sintaxe para arquivos .env
- ✅ **REST Client** - Testar APIs sem sair do VS Code
- ✅ **Git Graph** - Visualizar histórico Git

---

## ⚡ Atalhos e Comandos

### Comandos Essenciais
- `Ctrl+Shift+P` / `Cmd+Shift+P` - Command Palette (acessa tudo)
- `Ctrl+P` / `Cmd+P` - Quick Open (abrir arquivos)
- `Ctrl+``  - Abrir/fechar terminal integrado
- `Ctrl+B` / `Cmd+B` - Toggle sidebar

### Edição de Código
- `Ctrl+Space` - Trigger IntelliSense
- `Ctrl+.` - Quick Fix (sugestões de correção)
- `Alt+Shift+F` - Format document
- `Ctrl+/` - Toggle comment
- `Ctrl+D` - Select next occurrence
- `Alt+Up/Down` - Move line up/down

### Navegação
- `Ctrl+Click` - Go to definition
- `Alt+Left/Right` - Navigate back/forward
- `Ctrl+Shift+O` - Go to symbol in file
- `F12` - Go to definition
- `Shift+F12` - Find all references

### Debugging
- `F5` - Start debugging
- `F9` - Toggle breakpoint
- `F10` - Step over
- `F11` - Step into
- `Shift+F11` - Step out
- `Shift+F5` - Stop debugging

---

## 🐛 Debugging

### 1. Configurações Disponíveis

O projeto já vem com 8 configurações de debug prontas:

#### 🚀 Run Trading Bot (Main)
Executa o bot principal com todas as proteções.
- **Comando**: F5 ou Run → Start Debugging
- **Arquivo**: main.py
- **Uso**: Desenvolvimento e teste do bot

#### 🌐 Run API Server
Inicia o servidor API REST.
- **Arquivo**: main_api.py
- **Porta**: 8000 (por padrão)
- **Uso**: Testar endpoints da API

#### ✅ Verify Setup
Verifica se tudo está configurado corretamente.
- **Arquivo**: verify_setup.py
- **Uso**: Antes de rodar o bot pela primeira vez

#### 🧪 Run Tests
Executa todos os testes com pytest.
- **Uso**: Validar mudanças no código

#### 📊 Run Benchmarks
Executa benchmarks de performance.
- **Arquivo**: benchmark_performance.py
- **Uso**: Medir performance do sistema

#### 🔍 Current Python File
Executa o arquivo Python atual aberto.
- **Uso**: Testar scripts individuais

### 2. Como Usar Debugging

**Passo a Passo:**
1. Abra o arquivo que quer debugar
2. Clique à esquerda do número da linha para adicionar breakpoint (bolinha vermelha)
3. Pressione `F5` ou vá em Run → Start Debugging
4. Escolha a configuração desejada
5. O código vai parar nos breakpoints
6. Use os controles para navegar:
   - Continue (F5)
   - Step Over (F10)
   - Step Into (F11)
   - Step Out (Shift+F11)

**Inspecionar Variáveis:**
- Passe o mouse sobre variáveis para ver valores
- Use o painel "Variables" à esquerda
- Use o "Debug Console" para executar código

---

## 📝 Tasks (Tarefas)

### Acessar Tasks
- `Ctrl+Shift+P` → "Tasks: Run Task"
- Ou `Ctrl+Shift+B` para task padrão

### Tasks Disponíveis

#### 🚀 Run Trading Bot
Inicia o bot de trading.
- **Atalho**: Ctrl+Shift+B (task padrão)

#### 🌐 Run API Server
Inicia servidor API REST.

#### ✅ Verify Setup
Verifica configuração do projeto.

#### 📦 Install Dependencies
Instala todas as dependências do requirements.txt.

#### 🧪 Run All Tests
Executa suite completa de testes.

#### 📊 Run Performance Benchmarks
Executa benchmarks de performance.

#### 🧹 Clean Python Cache
Remove todos os `__pycache__` e `.pyc`.

#### 📝 Format Code with Black
Formata todo o código com Black.

#### 🔍 Lint with Pylint
Analisa código com Pylint.

#### 📋 Create Virtual Environment
Cria novo ambiente virtual (venv).

#### 🔄 Update Requirements
Atualiza requirements.txt com pacotes instalados.

---

## 💡 Dicas e Truques

### 1. Formatação Automática
O projeto está configurado para formatar automaticamente ao salvar:
- Usa **Black** como formatador
- Organiza imports automaticamente
- Linha máxima: 120 caracteres

**Formatar manualmente**: `Alt+Shift+F`

### 2. IntelliSense Poderoso
- Digite `.` depois de um objeto para ver métodos
- `Ctrl+Space` para forçar sugestões
- Hovering sobre funções mostra documentação

### 3. Workspace Settings
Configurações já otimizadas para Python:
- Auto-save após 1 segundo
- Linting automático ao salvar
- Type checking habilitado
- Arquivos de cache ocultos

### 4. Terminal Integrado
- ``Ctrl+` `` - Abrir terminal
- Terminal já tem `PYTHONPATH` configurado
- Múltiplos terminais com dropdown

### 5. Git Integration
- Source Control view: `Ctrl+Shift+G`
- GitLens mostra blame inline
- Git Graph para visualizar branches

### 6. Busca Avançada
- `Ctrl+Shift+F` - Search in files
- `Ctrl+H` - Find and replace
- Regex support habilitado

### 7. Multi-Cursor
- `Alt+Click` - Adicionar cursor
- `Ctrl+Alt+Up/Down` - Cursor acima/abaixo
- `Ctrl+D` - Select next occurrence

### 8. Snippets
Digite e pressione Tab:
- `def` → function definition
- `class` → class definition
- `for` → for loop
- `if` → if statement

### 9. Problems Panel
- `Ctrl+Shift+M` - Ver todos os problemas
- Linting automático mostra erros
- Click para ir direto ao problema

### 10. Workspace Limpo
Arquivos ocultos automaticamente:
- `__pycache__`
- `.pyc` files
- `venv` folder
- `.pytest_cache`

Mas `.env` está visível para fácil edição!

---

## 🔧 Configurações Personalizadas

### settings.json (.vscode/settings.json)
Principais configurações aplicadas:
```json
{
    "python.formatting.provider": "black",
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "editor.formatOnSave": true,
    "files.autoSave": "afterDelay",
    "python.analysis.typeCheckingMode": "basic"
}
```

### Modificar Configurações
1. `Ctrl+,` - Abrir settings
2. Pesquisar configuração desejada
3. Alterações em Workspace Settings aplicam só neste projeto

---

## 🚨 Troubleshooting

### Python Interpreter não encontrado
**Solução:**
1. `Ctrl+Shift+P`
2. "Python: Select Interpreter"
3. Escolher Python 3.8+

### IntelliSense não funciona
**Solução:**
1. Recarregar window: `Ctrl+Shift+P` → "Reload Window"
2. Instalar Pylance se ainda não tiver
3. Verificar que workspace tem PYTHONPATH configurado

### Linting com muitos erros
**Solução:**
1. Configurações estão otimizadas (max-line-length=120)
2. Alguns warnings podem ser ignorados
3. Use `# pylint: disable=rule-name` para casos específicos

### Tasks não funcionam
**Solução:**
1. Verificar que Python interpreter está selecionado
2. Abrir terminal e testar comando manualmente
3. Verificar que dependencies estão instaladas

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [VS Code Python](https://code.visualstudio.com/docs/python/python-tutorial)
- [Debugging Python](https://code.visualstudio.com/docs/python/debugging)
- [VS Code Tips](https://code.visualstudio.com/docs/getstarted/tips-and-tricks)

### Atalhos Completos
- Windows/Linux: `Ctrl+K Ctrl+S`
- Mac: `Cmd+K Cmd+S`

### Customizar Temas
1. `Ctrl+K Ctrl+T` - Theme selector
2. Recomendados: Dark+, One Dark Pro, Material Theme

---

## ✅ Checklist de Configuração

- [ ] VS Code instalado
- [ ] Projeto aberto no VS Code
- [ ] Extensões recomendadas instaladas
- [ ] Python interpreter selecionado
- [ ] Ambiente virtual criado (opcional mas recomendado)
- [ ] Dependencies instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo .env configurado
- [ ] Verify setup executado com sucesso (`python verify_setup.py`)
- [ ] Debug configuration testada (F5)
- [ ] Git configurado (se for contribuir)

---

## 🎉 Pronto para Desenvolver!

Com tudo configurado, você tem:
- ✅ IntelliSense inteligente
- ✅ Formatação automática
- ✅ Linting em tempo real
- ✅ Debugging poderoso
- ✅ Tasks prontas para usar
- ✅ Git integrado
- ✅ Terminal otimizado

**Comece:** Pressione `F5` para rodar o bot em modo debug!

---

## 🆘 Precisa de Ajuda?

1. **Documentação do Projeto**: Veja os arquivos .md na raiz
2. **VS Code Docs**: [code.visualstudio.com/docs](https://code.visualstudio.com/docs)
3. **Python Extension**: [Marketplace](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

---

**Boa sorte com seu Trading Bot! 🚀📈**
