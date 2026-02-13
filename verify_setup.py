#!/usr/bin/env python3
"""
✅ VERIFICAÇÃO DE SETUP
========================

Script para verificar se o ambiente está corretamente configurado.
Execute: python3 verify_setup.py

"""

import sys
import os
import importlib.util


def check_python_version():
    """Verifica versão do Python"""
    print("🐍 Verificando Python...")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version_str} (OK)")
        return True
    else:
        print(f"   ❌ Python {version_str} (Requer 3.8+)")
        return False


def check_package(package_name, import_name=None):
    """Verifica se um pacote está instalado"""
    if import_name is None:
        import_name = package_name
    
    spec = importlib.util.find_spec(import_name)
    return spec is not None


def check_dependencies():
    """Verifica dependências essenciais"""
    print("\n📦 Verificando dependências...")
    
    essential_packages = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'python-dotenv': 'dotenv',
        'python-binance': 'binance',
        'ccxt': 'ccxt',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'requests': 'requests',
    }
    
    all_ok = True
    missing = []
    
    for package, import_name in essential_packages.items():
        if check_package(package, import_name):
            print(f"   ✅ {package}")
        else:
            print(f"   ❌ {package} (não instalado)")
            missing.append(package)
            all_ok = False
    
    if missing:
        print(f"\n   📥 Para instalar os pacotes faltando:")
        print(f"   pip3 install {' '.join(missing)}")
    
    return all_ok


def check_env_file():
    """Verifica arquivo .env"""
    print("\n⚙️  Verificando arquivo .env...")
    
    if not os.path.exists('.env'):
        print("   ❌ Arquivo .env não encontrado")
        print("   📝 Crie o arquivo: cp .env.example .env")
        return False
    
    print("   ✅ Arquivo .env existe")
    
    # Carregar .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verificar variáveis essenciais
    required_vars = {
        'BINANCE_API_KEY': 'API Key da Binance',
        'BINANCE_API_SECRET': 'API Secret da Binance',
        'USE_TESTNET': 'Modo Testnet/Produção',
        'PRIMARY_SYMBOL': 'Símbolo de trading',
    }
    
    all_configured = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value not in ['', 'your_api_key_here', 'your_api_secret_here']:
            print(f"   ✅ {var}: Configurado")
        else:
            print(f"   ⚠️  {var}: NÃO configurado ({description})")
            all_configured = False
    
    return all_configured


def check_binance_connection():
    """Testa conexão com Binance"""
    print("\n🔌 Testando conexão Binance...")
    
    try:
        from dotenv import load_dotenv
        from binance.client import Client
        
        load_dotenv()
        
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        use_testnet = os.getenv('USE_TESTNET', 'True').lower() == 'true'
        
        if not api_key or api_key == 'your_api_key_here':
            print("   ⚠️  API Key não configurada")
            return False
        
        if not api_secret or api_secret == 'your_api_secret_here':
            print("   ⚠️  API Secret não configurada")
            return False
        
        # Criar cliente
        client = Client(api_key, api_secret, testnet=use_testnet)
        
        # Testar conexão
        server_time = client.get_server_time()
        mode = "TESTNET 🧪" if use_testnet else "PRODUÇÃO ⚠️"
        
        print(f"   ✅ Conexão OK ({mode})")
        print(f"   ⏰ Server time: {server_time['serverTime']}")
        
        # Testar acesso à conta
        try:
            account_status = client.get_account_status()
            print(f"   ✅ Acesso à conta: OK")
        except Exception as e:
            print(f"   ⚠️  Acesso à conta: {str(e)[:50]}...")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Erro ao importar: {e}")
        print("   📥 Instale: pip3 install python-binance python-dotenv")
        return False
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        print("   💡 Verifique:")
        print("      - API Keys corretas")
        print("      - Permissões da API (leitura/trading)")
        print("      - Conexão com internet")
        return False


def check_core_modules():
    """Verifica módulos core do bot"""
    print("\n🧩 Verificando módulos core...")
    
    core_modules = [
        'ensemble_strategy',
        'binance_connector',
        'circuit_breaker',
        'rate_limiter',
        'position_sizer',
    ]
    
    all_ok = True
    for module in core_modules:
        if os.path.exists(f"{module}.py"):
            print(f"   ✅ {module}.py")
        else:
            print(f"   ⚠️  {module}.py (não encontrado)")
            all_ok = False
    
    return all_ok


def check_directories():
    """Verifica/cria diretórios necessários"""
    print("\n📁 Verificando diretórios...")
    
    directories = ['logs', 'data', 'models']
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"   ✅ {directory}/ (criado)")
            except Exception as e:
                print(f"   ❌ {directory}/ (erro ao criar: {e})")
        else:
            print(f"   ✅ {directory}/ (existe)")
    
    return True


def print_summary(results):
    """Imprime resumo da verificação"""
    print("\n" + "="*60)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("="*60)
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{status:12} {check}")
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 TUDO PRONTO! Você pode iniciar o bot.")
        print("\n📚 Próximos passos:")
        print("   1. Execute: python3 main.py")
        print("   2. Monitore os logs em: logs/trading_bot.log")
        print("   3. Acesse o guia: COMO_COMECAR_AGORA.md")
        print("\n✨ Bom trading!")
    else:
        print("\n⚠️  ATENÇÃO: Alguns problemas foram encontrados.")
        print("   Resolva os itens marcados com ❌ antes de continuar.")
        print("\n📖 Consulte o guia: COMO_COMECAR_AGORA.md")
    
    return all_passed


def main():
    """Função principal"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         ✅ VERIFICAÇÃO DE SETUP DO BOT                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    results = {}
    
    # Executar verificações
    results['Python 3.8+'] = check_python_version()
    results['Dependências'] = check_dependencies()
    results['Arquivo .env'] = check_env_file()
    results['Conexão Binance'] = check_binance_connection()
    results['Módulos Core'] = check_core_modules()
    results['Diretórios'] = check_directories()
    
    # Resumo
    success = print_summary(results)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
