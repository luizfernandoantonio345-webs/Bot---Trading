#!/usr/bin/env python3
"""
Setup rápido para VS Code
Prepara o projeto para execução imediata
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print header formatado"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_step(number, text):
    """Print passo formatado"""
    print(f"\n[{number}] {text}")

def check_python_version():
    """Verifica versão do Python"""
    print_step(1, "Verificando Python...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ necessário")
        print(f"   Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def install_dependencies():
    """Instala dependências"""
    print_step(2, "Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
        print("✅ Dependências instaladas")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        print("   Execute manualmente: pip install -r requirements.txt")
        return False

def setup_env_file():
    """Configura arquivo .env"""
    print_step(3, "Configurando .env...")
    
    if os.path.exists(".env"):
        print("⚠️  .env já existe")
        response = input("   Deseja recriar? (s/N): ")
        if response.lower() != 's':
            print("✅ Mantendo .env existente")
            return True
    
    if not os.path.exists(".env.example"):
        print("❌ .env.example não encontrado")
        return False
    
    # Copia .env.example para .env
    with open(".env.example", "r") as f:
        content = f.read()
    
    with open(".env", "w") as f:
        f.write(content)
    
    print("✅ .env criado")
    print("\n⚠️  IMPORTANTE: Configure suas API keys no arquivo .env")
    print("   1. Abra .env no VS Code")
    print("   2. Configure BINANCE_API_KEY e BINANCE_SECRET_KEY")
    print("   3. Use testnet keys de: https://testnet.binance.vision/")
    
    return True

def check_vscode_config():
    """Verifica configuração VS Code"""
    print_step(4, "Verificando configuração VS Code...")
    
    vscode_dir = Path(".vscode")
    required_files = [
        "settings.json",
        "launch.json",
        "tasks.json",
        "extensions.json"
    ]
    
    missing = []
    for file in required_files:
        if not (vscode_dir / file).exists():
            missing.append(file)
    
    if missing:
        print(f"⚠️  Arquivos faltando: {', '.join(missing)}")
        print("   Isso é OK se você acabou de clonar o repo")
        return True
    
    print("✅ Configuração VS Code completa")
    return True

def create_directories():
    """Cria diretórios necessários"""
    print_step(5, "Criando diretórios...")
    
    dirs = ["logs", "data", "models"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    print("✅ Diretórios criados")
    return True

def print_next_steps():
    """Mostra próximos passos"""
    print_header("SETUP COMPLETO! 🎉")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("\n1️⃣  Configure API Keys:")
    print("   - Abra .env no VS Code")
    print("   - Configure BINANCE_API_KEY e BINANCE_SECRET_KEY")
    print("   - Obtenha testnet keys: https://testnet.binance.vision/")
    
    print("\n2️⃣  Instale Extensões VS Code:")
    print("   - Abra projeto no VS Code: code .")
    print("   - Clique em 'Instalar Tudo' na notificação")
    print("   - Ou Ctrl+Shift+P → 'Extensions: Show Recommended Extensions'")
    
    print("\n3️⃣  Selecione Python Interpreter:")
    print("   - Ctrl+Shift+P")
    print("   - 'Python: Select Interpreter'")
    print("   - Escolha Python 3.8+")
    
    print("\n4️⃣  Verifique Setup:")
    print("   - Execute: python verify_setup.py")
    print("   - Ou use task no VS Code")
    
    print("\n5️⃣  EXECUTE O BOT:")
    print("   - Pressione F5 no VS Code")
    print("   - Ou: python main.py")
    
    print("\n📚 DOCUMENTAÇÃO:")
    print("   - EXECUTAR_NO_VSCODE.md - Guia completo")
    print("   - VS_CODE_QUICK_START.md - Referência rápida")
    print("   - COMO_COMECAR_AGORA.md - Guia geral")
    
    print("\n" + "="*60)

def main():
    """Main function"""
    print_header("🚀 SETUP VS CODE - TRADING BOT")
    
    print("\nEste script vai:")
    print("  ✓ Verificar Python")
    print("  ✓ Instalar dependências")
    print("  ✓ Configurar .env")
    print("  ✓ Verificar VS Code")
    print("  ✓ Criar diretórios")
    
    input("\nPressione Enter para continuar...")
    
    # Execute checks
    checks = [
        check_python_version(),
        install_dependencies(),
        setup_env_file(),
        check_vscode_config(),
        create_directories()
    ]
    
    # Results
    if all(checks):
        print_next_steps()
        return 0
    else:
        print("\n❌ Setup incompleto")
        print("   Resolva os erros acima e execute novamente")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        sys.exit(1)
