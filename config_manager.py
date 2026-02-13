"""
Configuração e validação de ambiente
"""
import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Carregar .env se existir
load_dotenv()


class ConfigManager:
    """Gerencia configurações do bot"""
    
    # Variáveis obrigatórias
    REQUIRED_VARS = [
        'BINANCE_API_KEY',
        'BINANCE_API_SECRET',
    ]
    
    # Variáveis opcionais com defaults
    OPTIONAL_VARS = {
        'USE_TESTNET': 'True',
        'IS_FUTURES': 'False',
        'PRIMARY_SYMBOL': 'BTCUSDT',
        'MAX_DAILY_LOSS': '100.0',
        'MAX_POSITION_SIZE': '0.01',
        'RISK_PER_TRADE': '0.01',
        'TELEGRAM_BOT_TOKEN': '',
        'TELEGRAM_CHAT_ID': '',
    }
    
    def __init__(self):
        self.config: Dict[str, str] = {}
        self._validated = False
        
    def validate_environment(self) -> tuple[bool, list[str]]:
        """
        Valida todas as variáveis de ambiente necessárias
        
        Returns:
            (is_valid, missing_vars)
        """
        missing = []
        
        for var in self.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                missing.append(var)
            else:
                self.config[var] = value
        
        # Carregar opcionais com defaults
        for var, default in self.OPTIONAL_VARS.items():
            self.config[var] = os.getenv(var, default)
        
        self._validated = len(missing) == 0
        
        if self._validated:
            logger.info("✅ Configuração validada com sucesso")
            self._log_config()
        else:
            logger.error(f"❌ Variáveis faltando: {', '.join(missing)}")
        
        return self._validated, missing
    
    def _log_config(self):
        """Log de configuração (sem secrets)"""
        safe_config = {
            'USE_TESTNET': self.config.get('USE_TESTNET'),
            'IS_FUTURES': self.config.get('IS_FUTURES'),
            'PRIMARY_SYMBOL': self.config.get('PRIMARY_SYMBOL'),
            'MAX_DAILY_LOSS': self.config.get('MAX_DAILY_LOSS'),
            'MAX_POSITION_SIZE': self.config.get('MAX_POSITION_SIZE'),
            'RISK_PER_TRADE': self.config.get('RISK_PER_TRADE'),
            'HAS_TELEGRAM': bool(self.config.get('TELEGRAM_BOT_TOKEN')),
        }
        logger.info(f"Configuração: {safe_config}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Obtém valor de configuração"""
        return self.config.get(key, default)
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Obtém valor booleano"""
        value = self.config.get(key, str(default))
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Obtém valor float"""
        try:
            return float(self.config.get(key, str(default)))
        except ValueError:
            return default
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Obtém valor inteiro"""
        try:
            return int(self.config.get(key, str(default)))
        except ValueError:
            return default
    
    def is_testnet(self) -> bool:
        """Verifica se está usando testnet"""
        return self.get_bool('USE_TESTNET', True)
    
    def is_futures(self) -> bool:
        """Verifica se está usando futures"""
        return self.get_bool('IS_FUTURES', False)
    
    def has_telegram(self) -> bool:
        """Verifica se telegram está configurado"""
        return bool(self.config.get('TELEGRAM_BOT_TOKEN') and 
                   self.config.get('TELEGRAM_CHAT_ID'))
    
    def get_binance_config(self) -> dict:
        """Retorna configuração para Binance"""
        return {
            'api_key': self.config.get('BINANCE_API_KEY'),
            'api_secret': self.config.get('BINANCE_API_SECRET'),
            'testnet': self.is_testnet(),
            'futures': self.is_futures(),
        }
    
    def get_risk_config(self) -> dict:
        """Retorna configuração de risco"""
        return {
            'max_daily_loss': self.get_float('MAX_DAILY_LOSS', 100.0),
            'max_position_size': self.get_float('MAX_POSITION_SIZE', 0.01),
            'risk_per_trade': self.get_float('RISK_PER_TRADE', 0.01),
        }
    
    def create_sample_env(self, filepath: str = '.env.example'):
        """Cria arquivo .env de exemplo"""
        content = """# Binance API Configuration
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# Trading Configuration
USE_TESTNET=True
IS_FUTURES=False
PRIMARY_SYMBOL=BTCUSDT

# Risk Management
MAX_DAILY_LOSS=100.0
MAX_POSITION_SIZE=0.01
RISK_PER_TRADE=0.01

# Telegram Notifications (Optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
"""
        with open(filepath, 'w') as f:
            f.write(content)
        
        logger.info(f"Arquivo de exemplo criado: {filepath}")


# Instância global
config_manager = ConfigManager()


def validate_config_on_startup():
    """Função helper para validar na inicialização"""
    is_valid, missing = config_manager.validate_environment()
    
    if not is_valid:
        error_msg = f"""
╔═══════════════════════════════════════════════════════════════╗
║  ⚠️  CONFIGURAÇÃO INCOMPLETA                                  ║
╚═══════════════════════════════════════════════════════════════╝

Variáveis de ambiente faltando:
{chr(10).join(f'  - {var}' for var in missing)}

Para corrigir:

1. Crie um arquivo .env na raiz do projeto
2. Adicione as variáveis acima
3. Execute novamente

Exemplo de .env:
{'-' * 60}
BINANCE_API_KEY=sua_chave_aqui
BINANCE_API_SECRET=seu_secret_aqui
USE_TESTNET=True
{'-' * 60}

Um arquivo .env.example foi criado como referência.
"""
        config_manager.create_sample_env()
        raise EnvironmentError(error_msg)
    
    return config_manager
