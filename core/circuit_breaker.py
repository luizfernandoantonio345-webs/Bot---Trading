"""
Optimized Circuit Breaker with state machine and metrics
High-performance fault tolerance mechanism
"""

import time
import threading
from enum import Enum
from typing import Callable, TypeVar, Optional, Dict, Any, List
from dataclasses import dataclass, field
from collections import deque
from functools import wraps

from core.logger import get_logger
from core.exceptions import CircuitBreakerException
from core.singleton import Singleton

logger = get_logger(__name__)

T = TypeVar('T')


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Failing, reject all requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5  # Failures to open circuit
    success_threshold: int = 2  # Successes to close circuit
    timeout: float = 60.0  # Seconds before retry
    half_open_max_calls: int = 3  # Max calls in half-open state
    expected_exception: type = Exception
    name: str = "default"


@dataclass
class CircuitMetrics:
    """Circuit breaker metrics"""
    total_calls: int = 0
    total_successes: int = 0
    total_failures: int = 0
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    state_changes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    recent_errors: deque = field(default_factory=lambda: deque(maxlen=10))


class OptimizedCircuitBreaker:
    """
    High-performance circuit breaker with detailed metrics
    Implements the Circuit Breaker pattern for fault tolerance
    """
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """
        Args:
            config: Circuit breaker configuration
        """
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitMetrics()
        self._lock = threading.RLock()
        self._half_open_calls = 0
        
        logger.info(
            f"CircuitBreaker '{self.config.name}' initialized: "
            f"failure_threshold={self.config.failure_threshold}, "
            f"timeout={self.config.timeout}s"
        )
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
        
        Returns:
            Function result
        
        Raises:
            CircuitBreakerException: If circuit is open
            Exception: If function raises exception
        """
        with self._lock:
            self.metrics.total_calls += 1
            
            # Check if can proceed
            if not self._can_proceed():
                raise CircuitBreakerException(
                    f"Circuit breaker '{self.config.name}' is OPEN",
                    service_name=self.config.name,
                    retry_after=self._time_until_retry()
                )
            
            # Track half-open calls
            if self.state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1
        
        # Execute function (outside lock to avoid blocking)
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except self.config.expected_exception as e:
            self._on_failure(e)
            raise
    
    def _can_proceed(self) -> bool:
        """Check if request can proceed"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if self._should_attempt_reset():
                logger.info(f"Circuit '{self.config.name}': OPEN -> HALF_OPEN")
                self._transition_to_half_open()
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            # Limit calls in half-open state
            return self._half_open_calls < self.config.half_open_max_calls
        
        return False
    
    def _should_attempt_reset(self) -> bool:
        """Check if should attempt to reset circuit"""
        if self.metrics.last_failure_time is None:
            return True
        
        elapsed = time.time() - self.metrics.last_failure_time
        return elapsed >= self.config.timeout
    
    def _on_success(self) -> None:
        """Handle successful execution"""
        with self._lock:
            self.metrics.total_successes += 1
            self.metrics.consecutive_successes += 1
            self.metrics.consecutive_failures = 0
            self.metrics.last_success_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                logger.debug(
                    f"Circuit '{self.config.name}': Success in HALF_OPEN "
                    f"({self.metrics.consecutive_successes}/{self.config.success_threshold})"
                )
                
                # Check if should close circuit
                if self.metrics.consecutive_successes >= self.config.success_threshold:
                    logger.info(f"Circuit '{self.config.name}': HALF_OPEN -> CLOSED")
                    self._transition_to_closed()
    
    def _on_failure(self, exception: Exception) -> None:
        """Handle failed execution"""
        with self._lock:
            self.metrics.total_failures += 1
            self.metrics.consecutive_failures += 1
            self.metrics.consecutive_successes = 0
            self.metrics.last_failure_time = time.time()
            
            # Store recent error
            self.metrics.recent_errors.append({
                'time': time.time(),
                'exception': str(exception),
                'type': type(exception).__name__
            })
            
            if self.state == CircuitState.HALF_OPEN:
                # Failed during test, reopen circuit
                logger.warning(
                    f"Circuit '{self.config.name}': HALF_OPEN -> OPEN "
                    f"(failure during test)"
                )
                self._transition_to_open()
            
            elif self.state == CircuitState.CLOSED:
                # Check if should open circuit
                if self.metrics.consecutive_failures >= self.config.failure_threshold:
                    logger.error(
                        f"Circuit '{self.config.name}': CLOSED -> OPEN "
                        f"(threshold reached: {self.metrics.consecutive_failures})"
                    )
                    self._transition_to_open()
    
    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state"""
        self.state = CircuitState.CLOSED
        self.metrics.consecutive_failures = 0
        self.metrics.consecutive_successes = 0
        self.metrics.state_changes += 1
        self._half_open_calls = 0
    
    def _transition_to_open(self) -> None:
        """Transition to OPEN state"""
        self.state = CircuitState.OPEN
        self.metrics.consecutive_successes = 0
        self.metrics.state_changes += 1
        self._half_open_calls = 0
    
    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state"""
        self.state = CircuitState.HALF_OPEN
        self.metrics.consecutive_successes = 0
        self.metrics.consecutive_failures = 0
        self.metrics.state_changes += 1
        self._half_open_calls = 0
    
    def _time_until_retry(self) -> float:
        """Calculate time until next retry attempt"""
        if self.state != CircuitState.OPEN:
            return 0.0
        
        if self.metrics.last_failure_time is None:
            return 0.0
        
        elapsed = time.time() - self.metrics.last_failure_time
        remaining = max(0.0, self.config.timeout - elapsed)
        return remaining
    
    def reset(self) -> None:
        """Manually reset circuit breaker"""
        with self._lock:
            logger.info(f"Circuit '{self.config.name}' manually reset")
            self.state = CircuitState.CLOSED
            self.metrics = CircuitMetrics()
            self._half_open_calls = 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status and metrics"""
        with self._lock:
            success_rate = 0.0
            if self.metrics.total_calls > 0:
                success_rate = self.metrics.total_successes / self.metrics.total_calls * 100
            
            return {
                'name': self.config.name,
                'state': self.state.value,
                'can_proceed': self._can_proceed(),
                'metrics': {
                    'total_calls': self.metrics.total_calls,
                    'total_successes': self.metrics.total_successes,
                    'total_failures': self.metrics.total_failures,
                    'consecutive_failures': self.metrics.consecutive_failures,
                    'consecutive_successes': self.metrics.consecutive_successes,
                    'success_rate': round(success_rate, 2),
                    'state_changes': self.metrics.state_changes
                },
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'success_threshold': self.config.success_threshold,
                    'timeout': self.config.timeout
                },
                'timing': {
                    'time_until_retry': round(self._time_until_retry(), 2),
                    'last_failure': self.metrics.last_failure_time,
                    'last_success': self.metrics.last_success_time
                },
                'recent_errors': list(self.metrics.recent_errors)
            }


class CircuitBreakerRegistry(Singleton):
    """
    Global registry for circuit breakers
    Allows managing multiple circuit breakers for different services
    """
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._breakers: Dict[str, OptimizedCircuitBreaker] = {}
        self._lock = threading.RLock()
        self._initialized = True
    
    def get_breaker(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> OptimizedCircuitBreaker:
        """
        Get or create circuit breaker
        
        Args:
            name: Circuit breaker name
            config: Optional configuration (used only for new breakers)
        
        Returns:
            OptimizedCircuitBreaker instance
        """
        with self._lock:
            if name not in self._breakers:
                if config is None:
                    config = CircuitBreakerConfig(name=name)
                else:
                    config.name = name
                
                self._breakers[name] = OptimizedCircuitBreaker(config)
            
            return self._breakers[name]
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        with self._lock:
            return {
                name: breaker.get_status()
                for name, breaker in self._breakers.items()
            }
    
    def reset_all(self) -> None:
        """Reset all circuit breakers"""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()


# Global registry instance
_registry = CircuitBreakerRegistry()


def get_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
) -> OptimizedCircuitBreaker:
    """Get circuit breaker from global registry"""
    return _registry.get_breaker(name, config)


def circuit_breaker(
    name: Optional[str] = None,
    **config_kwargs
):
    """
    Decorator for applying circuit breaker to functions
    
    Example:
        @circuit_breaker(name='external_api', failure_threshold=3, timeout=30)
        def call_external_api():
            return requests.get('https://api.example.com')
    """
    def decorator(func: Callable) -> Callable:
        breaker_name = name or f"{func.__module__}.{func.__name__}"
        config = CircuitBreakerConfig(name=breaker_name, **config_kwargs)
        breaker = get_circuit_breaker(breaker_name, config)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        # Add management methods
        wrapper.circuit_breaker = breaker
        wrapper.reset = breaker.reset
        wrapper.get_status = breaker.get_status
        
        return wrapper
    
    return decorator
