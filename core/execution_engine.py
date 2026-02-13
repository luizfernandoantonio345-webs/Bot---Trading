"""
═══════════════════════════════════════════════════════════════════
EXECUTION ENGINE - INTEGRAÇÃO BINANCE E EXECUÇÃO PROFISSIONAL
═══════════════════════════════════════════════════════════════════
Execução real de ordens com controle de latência, validação de fills,
reconciliação de estado e gerenciamento de posições.
"""

import time
import hmac
import hashlib
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"


class OrderStatus(Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


@dataclass
class Order:
    """Representação de uma ordem."""
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    order_id: Optional[str] = None
    client_order_id: Optional[str] = None
    status: Optional[str] = None
    filled_qty: float = 0.0
    executed_price: float = 0.0
    timestamp: Optional[datetime] = None


@dataclass
class Position:
    """Representação de uma posição."""
    symbol: str
    side: str
    entry_price: float
    quantity: float
    current_price: float
    unrealized_pnl: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    opened_at: datetime = None


class BinanceExecutor:
    """
    Executor de ordens na Binance (Spot e Futures).
    Gerencia execução, latência, fills e reconciliação de estado.
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        use_testnet: bool = False,
        is_futures: bool = False
    ):
        """
        Inicializa executor Binance.
        
        Args:
            api_key: API key da Binance
            api_secret: API secret da Binance
            use_testnet: Se usa testnet (para testes)
            is_futures: Se opera Futures (True) ou Spot (False)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.is_futures = is_futures
        
        # Base URLs
        if use_testnet:
            if is_futures:
                self.base_url = "https://testnet.binancefuture.com"
            else:
                self.base_url = "https://testnet.binance.vision"
        else:
            if is_futures:
                self.base_url = "https://fapi.binance.com"
            else:
                self.base_url = "https://api.binance.com"
        
        # Headers
        self.headers = {
            'X-MBX-APIKEY': self.api_key
        }
        
        # Estado
        self.active_orders = {}
        self.open_positions = {}
        self.latency_ms = 0
        
        # Verificar conexão
        self._test_connection()
    
    def _test_connection(self):
        """
        Testa conexão com API Binance.
        """
        try:
            start = time.time()
            endpoint = "/fapi/v1/ping" if self.is_futures else "/api/v3/ping"
            response = requests.get(f"{self.base_url}{endpoint}")
            self.latency_ms = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                print(f"✅ Binance conectada | Latência: {self.latency_ms}ms")
            else:
                raise Exception(f"Erro de conexão: {response.status_code}")
        except Exception as e:
            raise Exception(f"Falha ao conectar Binance: {e}")
    
    def _sign_request(self, params: Dict) -> str:
        """
        Assina requisição com HMAC SHA256.
        """
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
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
        params: Dict = None,
        signed: bool = False
    ) -> Dict:
        """
        Faz requisição à API Binance.
        """
        params = params or {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._sign_request(params)
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            start = time.time()
            
            if method == "GET":
                response = requests.get(url, params=params, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, params=params, headers=self.headers)
            elif method == "DELETE":
                response = requests.delete(url, params=params, headers=self.headers)
            else:
                raise ValueError(f"Método inválido: {method}")
            
            # Atualizar latência
            self.latency_ms = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = response.json().get('msg', 'Erro desconhecido')
                raise Exception(f"API Error [{response.status_code}]: {error_msg}")
        
        except Exception as e:
            raise Exception(f"Erro na requisição: {e}")
    
    def get_account_balance(self) -> Dict:
        """
        Obtém saldo da conta.
        """
        if self.is_futures:
            endpoint = "/fapi/v2/balance"
        else:
            endpoint = "/api/v3/account"
        
        data = self._make_request("GET", endpoint, signed=True)
        
        if self.is_futures:
            # Futures retorna lista de ativos
            balances = {b['asset']: float(b['balance']) for b in data}
        else:
            # Spot retorna objeto account
            balances = {b['asset']: float(b['free']) + float(b['locked']) 
                       for b in data['balances'] if float(b['free']) > 0 or float(b['locked']) > 0}
        
        return balances
    
    def get_current_price(self, symbol: str) -> float:
        """
        Obtém preço atual de um símbolo.
        """
        if self.is_futures:
            endpoint = "/fapi/v1/ticker/price"
        else:
            endpoint = "/api/v3/ticker/price"
        
        data = self._make_request("GET", endpoint, params={"symbol": symbol})
        return float(data['price'])
    
    def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        reduce_only: bool = False
    ) -> Order:
        """
        Executa ordem de mercado.
        
        Args:
            symbol: Par de trading (ex: BTCUSDT)
            side: BUY ou SELL
            quantity: Quantidade
            reduce_only: Se é ordem apenas para reduzir posição (Futures)
        
        Returns:
            Order com detalhes da execução
        """
        if self.is_futures:
            endpoint = "/fapi/v1/order"
        else:
            endpoint = "/api/v3/order"
        
        params = {
            "symbol": symbol,
            "side": side.value,
            "type": OrderType.MARKET.value,
            "quantity": quantity
        }
        
        if self.is_futures and reduce_only:
            params["reduceOnly"] = "true"
        
        # Executar
        print(f"📤 Executando ordem: {side.value} {quantity} {symbol}")
        
        try:
            response = self._make_request("POST", endpoint, params=params, signed=True)
            
            order = Order(
                symbol=symbol,
                side=side.value,
                order_type=OrderType.MARKET.value,
                quantity=quantity,
                order_id=str(response['orderId']),
                client_order_id=response.get('clientOrderId'),
                status=response['status'],
                filled_qty=float(response.get('executedQty', 0)),
                executed_price=float(response.get('avgPrice', 0)) if 'avgPrice' in response else 0.0,
                timestamp=datetime.now()
            )
            
            # Armazenar ordem ativa
            self.active_orders[order.order_id] = order
            
            print(f"✅ Ordem executada | ID: {order.order_id} | Preço: {order.executed_price}")
            
            # Verificar fill
            self._verify_order_fill(order)
            
            return order
        
        except Exception as e:
            print(f"❌ Erro ao executar ordem: {e}")
            raise
    
    def place_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        price: float
    ) -> Order:
        """
        Coloca ordem limite.
        """
        if self.is_futures:
            endpoint = "/fapi/v1/order"
        else:
            endpoint = "/api/v3/order"
        
        params = {
            "symbol": symbol,
            "side": side.value,
            "type": OrderType.LIMIT.value,
            "quantity": quantity,
            "price": price,
            "timeInForce": "GTC"  # Good Till Cancel
        }
        
        print(f"📤 Colocando ordem limite: {side.value} {quantity} {symbol} @ {price}")
        
        try:
            response = self._make_request("POST", endpoint, params=params, signed=True)
            
            order = Order(
                symbol=symbol,
                side=side.value,
                order_type=OrderType.LIMIT.value,
                quantity=quantity,
                price=price,
                order_id=str(response['orderId']),
                client_order_id=response.get('clientOrderId'),
                status=response['status'],
                timestamp=datetime.now()
            )
            
            self.active_orders[order.order_id] = order
            
            print(f"✅ Ordem limite colocada | ID: {order.order_id}")
            
            return order
        
        except Exception as e:
            print(f"❌ Erro ao colocar ordem limite: {e}")
            raise
    
    def place_stop_loss(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        stop_price: float
    ) -> Order:
        """
        Coloca ordem de stop loss.
        """
        if self.is_futures:
            endpoint = "/fapi/v1/order"
            order_type = "STOP_MARKET"
        else:
            endpoint = "/api/v3/order"
            order_type = "STOP_LOSS"
        
        params = {
            "symbol": symbol,
            "side": side.value,
            "type": order_type,
            "quantity": quantity,
            "stopPrice": stop_price
        }
        
        if not self.is_futures:
            # Spot precisa de timeInForce
            params["timeInForce"] = "GTC"
        
        print(f"📤 Colocando stop loss: {side.value} {quantity} {symbol} @ {stop_price}")
        
        try:
            response = self._make_request("POST", endpoint, params=params, signed=True)
            
            order = Order(
                symbol=symbol,
                side=side.value,
                order_type=order_type,
                quantity=quantity,
                stop_price=stop_price,
                order_id=str(response['orderId']),
                client_order_id=response.get('clientOrderId'),
                status=response['status'],
                timestamp=datetime.now()
            )
            
            self.active_orders[order.order_id] = order
            
            print(f"✅ Stop loss colocado | ID: {order.order_id}")
            
            return order
        
        except Exception as e:
            print(f"❌ Erro ao colocar stop loss: {e}")
            raise
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """
        Cancela ordem.
        """
        if self.is_futures:
            endpoint = "/fapi/v1/order"
        else:
            endpoint = "/api/v3/order"
        
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        
        try:
            response = self._make_request("DELETE", endpoint, params=params, signed=True)
            
            if order_id in self.active_orders:
                del self.active_orders[order_id]
            
            print(f"✅ Ordem cancelada | ID: {order_id}")
            return True
        
        except Exception as e:
            print(f"❌ Erro ao cancelar ordem: {e}")
            return False
    
    def get_order_status(self, symbol: str, order_id: str) -> Dict:
        """
        Consulta status de ordem.
        """
        if self.is_futures:
            endpoint = "/fapi/v1/order"
        else:
            endpoint = "/api/v3/order"
        
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        
        return self._make_request("GET", endpoint, params=params, signed=True)
    
    def _verify_order_fill(self, order: Order, max_retries: int = 5):
        """
        Verifica se ordem foi completamente executada.
        """
        for attempt in range(max_retries):
            time.sleep(0.5)  # Aguardar 500ms
            
            status_data = self.get_order_status(order.symbol, order.order_id)
            
            order.status = status_data['status']
            order.filled_qty = float(status_data['executedQty'])
            
            if status_data.get('avgPrice'):
                order.executed_price = float(status_data['avgPrice'])
            
            if order.status == OrderStatus.FILLED.value:
                print(f"✅ Ordem completamente preenchida | Qtd: {order.filled_qty}")
                return True
            
            elif order.status == OrderStatus.PARTIALLY_FILLED.value:
                print(f"⚠️  Ordem parcialmente preenchida | Qtd: {order.filled_qty}/{order.quantity}")
            
            elif order.status in [OrderStatus.CANCELED.value, OrderStatus.REJECTED.value, OrderStatus.EXPIRED.value]:
                print(f"❌ Ordem não executada | Status: {order.status}")
                return False
        
        print(f"⚠️  Timeout verificando fill da ordem {order.order_id}")
        return False
    
    def get_open_positions(self) -> List[Position]:
        """
        Obtém posições abertas (apenas Futures).
        """
        if not self.is_futures:
            return []
        
        endpoint = "/fapi/v2/positionRisk"
        
        data = self._make_request("GET", endpoint, signed=True)
        
        positions = []
        for pos_data in data:
            position_amt = float(pos_data['positionAmt'])
            
            if position_amt != 0:  # Posição aberta
                position = Position(
                    symbol=pos_data['symbol'],
                    side="LONG" if position_amt > 0 else "SHORT",
                    entry_price=float(pos_data['entryPrice']),
                    quantity=abs(position_amt),
                    current_price=float(pos_data['markPrice']),
                    unrealized_pnl=float(pos_data['unRealizedProfit'])
                )
                
                positions.append(position)
                self.open_positions[position.symbol] = position
        
        return positions
    
    def close_position(self, symbol: str, position_side: str = None) -> bool:
        """
        Fecha posição aberta.
        
        Args:
            symbol: Símbolo da posição
            position_side: LONG ou SHORT (Futures) ou None (Spot)
        """
        if not self.is_futures:
            print("❌ Close position apenas para Futures")
            return False
        
        # Obter posição atual
        positions = self.get_open_positions()
        position = next((p for p in positions if p.symbol == symbol), None)
        
        if not position:
            print(f"⚠️  Nenhuma posição aberta para {symbol}")
            return False
        
        # Determinar side oposto
        close_side = OrderSide.SELL if position.side == "LONG" else OrderSide.BUY
        
        # Executar ordem de fechamento
        try:
            order = self.place_market_order(
                symbol=symbol,
                side=close_side,
                quantity=position.quantity,
                reduce_only=True
            )
            
            print(f"✅ Posição fechada | {symbol} | P&L: {position.unrealized_pnl:.2f}")
            
            # Remover de posições abertas
            if symbol in self.open_positions:
                del self.open_positions[symbol]
            
            return True
        
        except Exception as e:
            print(f"❌ Erro ao fechar posição: {e}")
            return False
    
    def get_latency(self) -> int:
        """
        Retorna latência atual em ms.
        """
        return self.latency_ms
    
    def reconcile_state(self):
        """
        Reconcilia estado interno com estado real na exchange.
        """
        print("🔄 Reconciliando estado com exchange...")
        
        # Atualizar posições
        if self.is_futures:
            self.get_open_positions()
        
        # Atualizar ordens ativas
        for order_id in list(self.active_orders.keys()):
            order = self.active_orders[order_id]
            
            try:
                status_data = self.get_order_status(order.symbol, order_id)
                order.status = status_data['status']
                
                # Remover se finalizada
                if order.status in [OrderStatus.FILLED.value, OrderStatus.CANCELED.value, 
                                   OrderStatus.REJECTED.value, OrderStatus.EXPIRED.value]:
                    del self.active_orders[order_id]
            
            except:
                pass
        
        print(f"✅ Reconciliação completa | Posições: {len(self.open_positions)} | Ordens: {len(self.active_orders)}")


if __name__ == "__main__":
    print("Execution Engine - Integração Binance Profissional")
    print("Módulo pronto para integração")
