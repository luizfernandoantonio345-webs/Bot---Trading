"""
Circuit Breaker Pattern
Protege o sistema de cascatas de erros
"""
import time
import logging
from enum import Enum
from typing import Callable, Any

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Estados do circuit breaker"""
    CLOSED = "CLOSED"      # Normal, requisições passam
    OPEN = "OPEN"          # Bloqueado, nenhuma requisição passa
    HALF_OPEN = "HALF_OPEN"  # Testando recuperação


class CircuitBreaker:
    """
    Circuit Breaker para proteger contra falhas em cascata
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 300.0,  # 5 minutos
        success_threshold: int = 2
    ):
        """
        Args:
            failure_threshold: Número de falhas para abrir o circuito
            timeout: Tempo em segundos antes de tentar novamente
            success_threshold: Sucessos necessários para fechar o circuito
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        
        self.failures = 0
        self.successes = 0
        self.last_failure_time = 0
        self.state = CircuitState.CLOSED
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa função com proteção de circuit breaker
        
        Args:
            func: Função a ser executada
            *args, **kwargs: Argumentos para a função
            
        Returns:
            Resultado da função
            
        Raises:
            Exception: Se circuito estiver aberto ou função falhar
        """
        if not self.can_proceed():
            raise Exception(
                f"Circuit breaker OPEN. "
                f"Falhas: {self.failures}/{self.failure_threshold}. "
                f"Aguarde {self._time_until_retry():.0f}s"
            )
        
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
            
        except Exception as e:
            self.record_failure()
            raise e
    
    def can_proceed(self) -> bool:
        """Verifica se pode executar requisições"""
        now = time.time()
        
        if self.state == CircuitState.CLOSED:
            return True
            
        elif self.state == CircuitState.OPEN:
            # Verificar se passou o timeout
            if now - self.last_failure_time >= self.timeout:
                logger.info("Circuit breaker: OPEN -> HALF_OPEN (timeout expirado)")
                self.state = CircuitState.HALF_OPEN
                self.successes = 0
                return True
            return False
            
        elif self.state == CircuitState.HALF_OPEN:
            return True
            
        return False
    
    def record_success(self):
        """Registra uma execução bem-sucedida"""
        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            logger.debug(f"Circuit breaker: Sucesso {self.successes}/{self.success_threshold}")
            
            if self.successes >= self.success_threshold:
                logger.info("Circuit breaker: HALF_OPEN -> CLOSED (recuperado)")
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.successes = 0
        else:
            # Estado CLOSED, resetar contador de falhas
            self.failures = 0
    
    def record_failure(self):
        """Registra uma falha"""
        self.failures += 1
        self.last_failure_time = time.time()
        
        logger.warning(f"Circuit breaker: Falha {self.failures}/{self.failure_threshold}")
        
        if self.state == CircuitState.HALF_OPEN:
            # Falhou durante teste, voltar para OPEN
            logger.warning("Circuit breaker: HALF_OPEN -> OPEN (falha durante teste)")
            self.state = CircuitState.OPEN
            self.successes = 0
            
        elif self.failures >= self.failure_threshold:
            # Threshold atingido, abrir circuito
            logger.error("Circuit breaker: CLOSED -> OPEN (threshold atingido)")
            self.state = CircuitState.OPEN
    
    def reset(self):
        """Reseta o circuit breaker manualmente"""
        logger.info("Circuit breaker resetado manualmente")
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time = 0
    
    def _time_until_retry(self) -> float:
        """Calcula tempo até próxima tentativa"""
        if self.state != CircuitState.OPEN:
            return 0.0
        
        elapsed = time.time() - self.last_failure_time
        remaining = max(0, self.timeout - elapsed)
        return remaining
    
    def get_status(self) -> dict:
        """Retorna status atual"""
        return {
            'state': self.state.value,
            'failures': self.failures,
            'failure_threshold': self.failure_threshold,
            'successes': self.successes,
            'success_threshold': self.success_threshold,
            'time_until_retry': self._time_until_retry(),
            'can_proceed': self.can_proceed()
        }


# Instância global para API Binance
binance_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=300,  # 5 minutos
    success_threshold=2
)
