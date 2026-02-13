"""
Exception hierarchy for the trading system
Provides structured error handling with proper classification
"""

from typing import Optional, Dict, Any


class TradingException(Exception):
    """Base exception for all trading system errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details
        }


class APIException(TradingException):
    """Raised when API calls fail"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_body = response_body
        if status_code:
            self.details['status_code'] = status_code
        if response_body:
            self.details['response_body'] = response_body


class RateLimitException(TradingException):
    """Raised when rate limits are exceeded"""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[float] = None,
        limit_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        self.limit_type = limit_type
        if retry_after:
            self.details['retry_after'] = retry_after
        if limit_type:
            self.details['limit_type'] = limit_type


class ValidationException(TradingException):
    """Raised when input validation fails"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
        if field:
            self.details['field'] = field
        if value is not None:
            self.details['value'] = str(value)


class ConfigurationException(TradingException):
    """Raised when configuration is invalid or missing"""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        if config_key:
            self.details['config_key'] = config_key


class CircuitBreakerException(TradingException):
    """Raised when circuit breaker is open"""
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        retry_after: Optional[float] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.service_name = service_name
        self.retry_after = retry_after
        if service_name:
            self.details['service_name'] = service_name
        if retry_after:
            self.details['retry_after'] = retry_after


class DataException(TradingException):
    """Raised when data is invalid or missing"""
    pass


class ExecutionException(TradingException):
    """Raised when trade execution fails"""
    
    def __init__(
        self,
        message: str,
        order_id: Optional[str] = None,
        symbol: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.order_id = order_id
        self.symbol = symbol
        if order_id:
            self.details['order_id'] = order_id
        if symbol:
            self.details['symbol'] = symbol


class InsufficientFundsException(TradingException):
    """Raised when account has insufficient funds"""
    
    def __init__(
        self,
        message: str,
        required: Optional[float] = None,
        available: Optional[float] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.required = required
        self.available = available
        if required:
            self.details['required'] = required
        if available:
            self.details['available'] = available
