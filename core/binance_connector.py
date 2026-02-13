"""
Optimized Binance connector with async support and connection pooling
High-performance API client for production trading
"""

import time
import hmac
import hashlib
from typing import Dict, Optional, Any
from urllib.parse import urlencode
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.logger import get_logger, set_correlation_id
from core.exceptions import APIException, RateLimitException
from core.rate_limiter import get_rate_limiter
from core.circuit_breaker import get_circuit_breaker, CircuitBreakerConfig
from core.cache import cached

logger = get_logger(__name__)


class BinanceConnectorOptimized:
    """
    Optimized Binance API connector with:
    - Connection pooling for reduced latency
    - Automatic retry with exponential backoff
    - Integrated rate limiting (token bucket)
    - Circuit breaker protection
    - Response caching for market data
    - Request/response logging with correlation IDs
    """
    
    # API Endpoints
    SPOT_TESTNET_URL = "https://testnet.binance.vision"
    SPOT_PROD_URL = "https://api.binance.com"
    FUTURES_TESTNET_URL = "https://testnet.binancefuture.com"
    FUTURES_PROD_URL = "https://fapi.binance.com"
    
    # Weight costs for common endpoints
    ENDPOINT_WEIGHTS = {
        '/api/v3/ping': 1,
        '/api/v3/time': 1,
        '/api/v3/account': 10,
        '/api/v3/ticker/price': 1,
        '/api/v3/order': 1,
        '/api/v3/openOrders': 3,
        '/api/v3/klines': 1,
        '/api/v3/exchangeInfo': 10,
    }
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = True,
        futures: bool = False,
        pool_connections: int = 10,
        pool_maxsize: int = 20,
        max_retries: int = 3
    ):
        """
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet if True
            futures: Use futures API if True
            pool_connections: Number of connection pools
            pool_maxsize: Maximum size of connection pool
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.futures = futures
        
        # Determine base URL
        if futures:
            self.base_url = self.FUTURES_TESTNET_URL if testnet else self.FUTURES_PROD_URL
        else:
            self.base_url = self.SPOT_TESTNET_URL if testnet else self.SPOT_PROD_URL
        
        # Initialize session with connection pooling
        self.session = self._create_session(pool_connections, pool_maxsize, max_retries)
        
        # Get rate limiter and circuit breaker
        self.rate_limiter = get_rate_limiter()
        self.circuit_breaker = get_circuit_breaker(
            'binance_api',
            CircuitBreakerConfig(
                failure_threshold=5,
                timeout=60.0,
                success_threshold=2,
                name='binance_api'
            )
        )
        
        # Timestamp offset
        self.time_offset = 0
        self._sync_time()
        
        # Metrics
        self.metrics = {
            'requests': 0,
            'errors': 0,
            'cache_hits': 0,
            'avg_latency_ms': 0.0
        }
        
        logger.info(
            f"BinanceConnectorOptimized initialized: "
            f"{'Testnet' if testnet else 'Production'}, "
            f"{'Futures' if futures else 'Spot'}, "
            f"pool_size={pool_maxsize}"
        )
    
    def _create_session(
        self,
        pool_connections: int,
        pool_maxsize: int,
        max_retries: int
    ) -> requests.Session:
        """
        Create requests session with connection pooling and retry logic
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,  # 0.5, 1.0, 2.0 seconds
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=['GET', 'POST', 'DELETE']
        )
        
        # Configure adapter with pooling
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy
        )
        
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session
    
    def _sync_time(self) -> None:
        """Synchronize timestamp with Binance server"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v3/time",
                timeout=5
            )
            response.raise_for_status()
            server_time = response.json()['serverTime']
            local_time = int(time.time() * 1000)
            self.time_offset = server_time - local_time
            
            logger.info(f"Timestamp synchronized. Offset: {self.time_offset}ms")
        except Exception as e:
            logger.warning(f"Failed to sync timestamp: {e}")
            self.time_offset = 0
    
    def _get_timestamp(self) -> int:
        """Get current timestamp with offset"""
        return int(time.time() * 1000) + self.time_offset
    
    def _sign_request(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature"""
        query_string = urlencode(sorted(params.items()))
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_endpoint_weight(self, endpoint: str) -> int:
        """Get weight for endpoint"""
        return self.ENDPOINT_WEIGHTS.get(endpoint, 1)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        signed: bool = False,
        weight: Optional[int] = None
    ) -> Dict:
        """
        Make HTTP request with all protections
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            params: Request parameters
            signed: Whether to sign the request
            weight: Request weight (auto-detected if None)
        
        Returns:
            JSON response as dictionary
        
        Raises:
            APIException: On API errors
            RateLimitException: On rate limit exceeded
        """
        if params is None:
            params = {}
        
        # Set correlation ID for request tracing
        correlation_id = set_correlation_id()
        
        # Determine weight
        if weight is None:
            weight = self._get_endpoint_weight(endpoint)
        
        # Check rate limit (blocking with timeout)
        try:
            self.rate_limiter.acquire(weight=weight, timeout=10.0)
        except RateLimitException as e:
            self.metrics['errors'] += 1
            raise
        
        # Add signature if needed
        if signed:
            params['timestamp'] = self._get_timestamp()
            params['signature'] = self._sign_request(params)
        
        # Build URL
        url = f"{self.base_url}{endpoint}"
        
        # Headers
        headers = {
            'X-MBX-APIKEY': self.api_key,
            'X-Correlation-ID': correlation_id
        }
        
        # Execute with circuit breaker
        def execute():
            start_time = time.time()
            
            try:
                if method == 'GET':
                    response = self.session.get(
                        url,
                        params=params,
                        headers=headers,
                        timeout=10
                    )
                elif method == 'POST':
                    response = self.session.post(
                        url,
                        params=params,
                        headers=headers,
                        timeout=10
                    )
                elif method == 'DELETE':
                    response = self.session.delete(
                        url,
                        params=params,
                        headers=headers,
                        timeout=10
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Update latency metric
                latency_ms = (time.time() - start_time) * 1000
                self._update_latency_metric(latency_ms)
                
                # Check status code
                if response.status_code != 200:
                    error_data = response.json() if response.text else {}
                    raise APIException(
                        f"Binance API error: {response.status_code}",
                        status_code=response.status_code,
                        response_body=response.text,
                        details=error_data
                    )
                
                self.metrics['requests'] += 1
                return response.json()
            
            except requests.exceptions.RequestException as e:
                self.metrics['errors'] += 1
                raise APIException(
                    f"Request failed: {str(e)}",
                    details={'correlation_id': correlation_id}
                )
        
        try:
            return self.circuit_breaker.call(execute)
        except Exception as e:
            logger.error(
                f"Request failed: {method} {endpoint}",
                extra={'correlation_id': correlation_id, 'error': str(e)}
            )
            raise
    
    def _update_latency_metric(self, latency_ms: float) -> None:
        """Update average latency metric using exponential moving average"""
        alpha = 0.1  # Smoothing factor
        if self.metrics['avg_latency_ms'] == 0:
            self.metrics['avg_latency_ms'] = latency_ms
        else:
            self.metrics['avg_latency_ms'] = (
                alpha * latency_ms + (1 - alpha) * self.metrics['avg_latency_ms']
            )
    
    # Public API Methods
    
    def ping(self) -> Dict:
        """Test connectivity"""
        return self._make_request('GET', '/api/v3/ping')
    
    @cached(cache_name='binance_server_time', ttl=10)
    def get_server_time(self) -> Dict:
        """Get server time (cached for 10 seconds)"""
        return self._make_request('GET', '/api/v3/time')
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        return self._make_request('GET', '/api/v3/account', signed=True)
    
    @cached(cache_name='binance_prices', ttl=1)
    def get_ticker_price(self, symbol: str) -> Dict:
        """
        Get current price (cached for 1 second)
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
        """
        params = {'symbol': symbol}
        return self._make_request('GET', '/api/v3/ticker/price', params=params)
    
    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: str = 'GTC'
    ) -> Dict:
        """
        Create an order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            order_type: 'MARKET', 'LIMIT', etc.
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            time_in_force: 'GTC', 'IOC', 'FOK'
        
        Returns:
            Order response
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
        }
        
        if order_type == 'LIMIT':
            if price is None:
                raise ValueError("Price is required for LIMIT orders")
            params['price'] = price
            params['timeInForce'] = time_in_force
        
        logger.info(
            f"Creating order: {side} {quantity} {symbol}",
            extra={'order_type': order_type, 'price': price}
        )
        
        return self._make_request('POST', '/api/v3/order', params=params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancel an order"""
        params = {'symbol': symbol, 'orderId': order_id}
        return self._make_request('DELETE', '/api/v3/order', params=params, signed=True)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """Get all open orders"""
        params = {'symbol': symbol} if symbol else {}
        return self._make_request('GET', '/api/v3/openOrders', params=params, signed=True, weight=3)
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """Get order status"""
        params = {'symbol': symbol, 'orderId': order_id}
        return self._make_request('GET', '/api/v3/order', params=params, signed=True, weight=2)
    
    @cached(cache_name='binance_klines', ttl=60)
    def get_klines(
        self,
        symbol: str,
        interval: str = '5m',
        limit: int = 100
    ) -> list:
        """
        Get candlestick data (cached for 60 seconds)
        
        Args:
            symbol: Trading pair
            interval: '1m', '5m', '15m', '1h', '4h', '1d', etc.
            limit: Number of candles (max 1000)
        """
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': min(limit, 1000)  # Enforce max limit
        }
        return self._make_request('GET', '/api/v3/klines', params=params)
    
    @cached(cache_name='binance_exchange_info', ttl=3600)
    def get_exchange_info(self) -> Dict:
        """Get exchange information (cached for 1 hour)"""
        return self._make_request('GET', '/api/v3/exchangeInfo', weight=10)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get connector metrics"""
        return {
            **self.metrics,
            'rate_limiter': self.rate_limiter.get_status(),
            'circuit_breaker': self.circuit_breaker.get_status()
        }
    
    def close(self) -> None:
        """Close session and cleanup resources"""
        self.session.close()
        logger.info("BinanceConnectorOptimized closed")


def create_binance_connector(config: Dict) -> BinanceConnectorOptimized:
    """
    Factory function to create optimized Binance connector
    
    Args:
        config: Configuration dictionary with keys:
            - api_key: Binance API key
            - api_secret: Binance API secret
            - testnet: Use testnet (default True)
            - futures: Use futures API (default False)
    
    Returns:
        BinanceConnectorOptimized instance
    """
    return BinanceConnectorOptimized(
        api_key=config['api_key'],
        api_secret=config['api_secret'],
        testnet=config.get('testnet', True),
        futures=config.get('futures', False)
    )
