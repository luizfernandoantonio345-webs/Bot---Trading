"""
Connector para Binance API com proteções
"""
import time
import hmac
import hashlib
from typing import Dict, Optional
import logging
import requests
from urllib.parse import urlencode

from rate_limiter import rate_limiter
from circuit_breaker import binance_circuit_breaker

logger = logging.getLogger(__name__)


class BinanceConnector:
    """
    Connector robusto para Binance API com:
    - Rate limiting
    - Circuit breaker
    - Retry logic
    - Timestamp sync
    """
    
    # URLs
    SPOT_TESTNET_URL = "https://testnet.binance.vision"
    SPOT_PROD_URL = "https://api.binance.com"
    FUTURES_TESTNET_URL = "https://testnet.binancefuture.com"
    FUTURES_PROD_URL = "https://fapi.binance.com"
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = True,
        futures: bool = False
    ):
        """
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Se True, usa testnet
            futures: Se True, usa futures
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.futures = futures
        
        # Determinar base URL
        if futures:
            self.base_url = self.FUTURES_TESTNET_URL if testnet else self.FUTURES_PROD_URL
        else:
            self.base_url = self.SPOT_TESTNET_URL if testnet else self.SPOT_PROD_URL
        
        # Timestamp offset
        self.time_offset = 0
        self._sync_time()
        
        logger.info(
            f"BinanceConnector inicializado: "
            f"{'Testnet' if testnet else 'Produção'}, "
            f"{'Futures' if futures else 'Spot'}"
        )
    
    def _sync_time(self):
        """Sincroniza timestamp com servidor Binance"""
        try:
            response = requests.get(f"{self.base_url}/api/v3/time", timeout=5)
            server_time = response.json()['serverTime']
            local_time = int(time.time() * 1000)
            self.time_offset = server_time - local_time
            
            logger.info(f"Timestamp sincronizado. Offset: {self.time_offset}ms")
        except Exception as e:
            logger.warning(f"Falha ao sincronizar timestamp: {e}")
            self.time_offset = 0
    
    def _get_timestamp(self) -> int:
        """Retorna timestamp atual com offset"""
        return int(time.time() * 1000) + self.time_offset
    
    def _sign_request(self, params: Dict) -> str:
        """Gera assinatura para requisição"""
        query_string = urlencode(sorted(params.items()))
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        signed: bool = False,
        weight: int = 1
    ) -> Dict:
        """
        Faz requisição para Binance API com proteções
        
        Args:
            method: GET, POST, DELETE, etc
            endpoint: Endpoint da API (ex: /api/v3/order)
            params: Parâmetros da requisição
            signed: Se True, assina a requisição
            weight: Peso da requisição para rate limiting
        """
        if params is None:
            params = {}
        
        # Verificar rate limit
        can_execute, reason = rate_limiter.can_execute_order(weight)
        if not can_execute:
            wait_time = rate_limiter.wait_if_needed(weight)
            if wait_time > 0:
                logger.warning(f"Rate limit: aguardando {wait_time}s")
                time.sleep(wait_time)
        
        # Adicionar timestamp se assinado
        if signed:
            params['timestamp'] = self._get_timestamp()
            params['signature'] = self._sign_request(params)
        
        # URL completa
        url = f"{self.base_url}{endpoint}"
        
        # Headers
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        
        # Executar com circuit breaker
        def execute():
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, params=params, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, params=params, headers=headers, timeout=10)
            else:
                raise ValueError(f"Método não suportado: {method}")
            
            # Verificar resposta
            if response.status_code != 200:
                error_msg = f"Erro API Binance: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            return response.json()
        
        try:
            result = binance_circuit_breaker.call(execute)
            rate_limiter.record_order(weight)
            return result
            
        except Exception as e:
            logger.error(f"Erro na requisição: {e}")
            raise
    
    # ========== Métodos públicos ==========
    
    def ping(self) -> Dict:
        """Testa conectividade"""
        return self._make_request('GET', '/api/v3/ping', weight=1)
    
    def get_server_time(self) -> Dict:
        """Obtém hora do servidor"""
        return self._make_request('GET', '/api/v3/time', weight=1)
    
    def get_account_info(self) -> Dict:
        """Obtém informações da conta"""
        return self._make_request('GET', '/api/v3/account', signed=True, weight=10)
    
    def get_ticker_price(self, symbol: str) -> Dict:
        """Obtém preço atual"""
        params = {'symbol': symbol}
        return self._make_request('GET', '/api/v3/ticker/price', params=params, weight=1)
    
    def create_order(
        self,
        symbol: str,
        side: str,  # BUY ou SELL
        order_type: str,  # MARKET, LIMIT, etc
        quantity: float,
        price: Optional[float] = None,
        time_in_force: str = 'GTC'
    ) -> Dict:
        """
        Cria uma ordem
        
        Args:
            symbol: Par (ex: BTCUSDT)
            side: BUY ou SELL
            order_type: MARKET, LIMIT, STOP_LOSS_LIMIT, etc
            quantity: Quantidade
            price: Preço (para LIMIT)
            time_in_force: GTC, IOC, FOK
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
        }
        
        if order_type == 'LIMIT':
            if price is None:
                raise ValueError("Preço é obrigatório para ordem LIMIT")
            params['price'] = price
            params['timeInForce'] = time_in_force
        
        logger.info(f"Criando ordem: {side} {quantity} {symbol} @ {price}")
        
        return self._make_request('POST', '/api/v3/order', params=params, signed=True, weight=1)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancela uma ordem"""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('DELETE', '/api/v3/order', params=params, signed=True, weight=1)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """Lista ordens abertas"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        return self._make_request('GET', '/api/v3/openOrders', params=params, signed=True, weight=3)
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """Consulta status de uma ordem"""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('GET', '/api/v3/order', params=params, signed=True, weight=2)
    
    def get_klines(
        self,
        symbol: str,
        interval: str = '5m',
        limit: int = 100
    ) -> list:
        """
        Obtém dados de candlestick
        
        Args:
            symbol: Par
            interval: 1m, 5m, 15m, 1h, 4h, 1d, etc
            limit: Número de candles (max 1000)
        """
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        return self._make_request('GET', '/api/v3/klines', params=params, weight=1)
    
    def get_exchange_info(self) -> Dict:
        """Obtém informações da exchange"""
        return self._make_request('GET', '/api/v3/exchangeInfo', weight=10)


def create_binance_connector(config: Dict) -> BinanceConnector:
    """
    Factory function para criar connector
    
    Args:
        config: Dict com api_key, api_secret, testnet, futures
    """
    return BinanceConnector(
        api_key=config['api_key'],
        api_secret=config['api_secret'],
        testnet=config.get('testnet', True),
        futures=config.get('futures', False)
    )
