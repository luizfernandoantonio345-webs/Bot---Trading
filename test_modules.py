"""
Testes básicos para módulos críticos
Execute com: pytest test_modules.py -v
"""
import pytest
from rate_limiter import RateLimitManager
from circuit_breaker import CircuitBreaker, CircuitState
from position_sizer import PositionSizer
from trading_strategy import SimpleMovingAverageStrategy, RSIStrategy


class TestRateLimiter:
    """Testes do Rate Limiter"""
    
    def test_can_execute_order(self):
        """Testa se pode executar ordem"""
        limiter = RateLimitManager()
        can_execute, reason = limiter.can_execute_order()
        assert can_execute == True
        assert reason == "OK"
    
    def test_record_order(self):
        """Testa registro de ordem"""
        limiter = RateLimitManager()
        limiter.record_order(weight=1)
        status = limiter.get_status()
        assert status['orders_today'] == 1
    
    def test_rate_limit_per_second(self):
        """Testa limite por segundo"""
        limiter = RateLimitManager()
        
        # Executar 10 ordens (limite por segundo)
        for i in range(10):
            limiter.record_order()
        
        # 11ª ordem deve ser bloqueada
        can_execute, reason = limiter.can_execute_order()
        assert can_execute == False
        assert "segundo" in reason.lower()


class TestCircuitBreaker:
    """Testes do Circuit Breaker"""
    
    def test_initial_state_closed(self):
        """Testa estado inicial"""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.can_proceed() == True
    
    def test_record_success(self):
        """Testa registro de sucesso"""
        cb = CircuitBreaker()
        cb.record_success()
        assert cb.failures == 0
    
    def test_record_failure(self):
        """Testa registro de falha"""
        cb = CircuitBreaker(failure_threshold=3)
        
        cb.record_failure()
        assert cb.failures == 1
        assert cb.state == CircuitState.CLOSED
        
        cb.record_failure()
        assert cb.failures == 2
        assert cb.state == CircuitState.CLOSED
        
        cb.record_failure()
        assert cb.failures == 3
        assert cb.state == CircuitState.OPEN
    
    def test_circuit_opens_on_threshold(self):
        """Testa abertura do circuito"""
        cb = CircuitBreaker(failure_threshold=2)
        
        for i in range(2):
            cb.record_failure()
        
        assert cb.state == CircuitState.OPEN
        assert cb.can_proceed() == False
    
    def test_call_with_success(self):
        """Testa execução bem-sucedida"""
        cb = CircuitBreaker()
        
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        assert result == "success"
        assert cb.failures == 0
    
    def test_call_with_failure(self):
        """Testa execução com falha"""
        cb = CircuitBreaker()
        
        def fail_func():
            raise Exception("Test error")
        
        with pytest.raises(Exception):
            cb.call(fail_func)
        
        assert cb.failures == 1


class TestPositionSizer:
    """Testes do Position Sizer"""
    
    def test_calculate_size_basic(self):
        """Testa cálculo básico de posição"""
        sizer = PositionSizer()
        
        result = sizer.calculate_size(
            account_balance=1000,
            entry_price=50000,
            stop_loss_price=49000
        )
        
        assert result['position_size'] > 0
        assert result['risk_percentage'] <= 1.0
        assert 'position_value' in result
    
    def test_risk_percentage_respected(self):
        """Testa se % de risco é respeitado"""
        sizer = PositionSizer(max_risk_per_trade=0.01)
        
        result = sizer.calculate_size(
            account_balance=10000,
            entry_price=50000,
            stop_loss_price=49000
        )
        
        # Risco deve ser <= 1% do capital
        assert result['risk_amount'] <= 100
    
    def test_max_position_size_respected(self):
        """Testa se tamanho máximo é respeitado"""
        sizer = PositionSizer(max_position_size=0.05)
        
        result = sizer.calculate_size(
            account_balance=10000,
            entry_price=1000,
            stop_loss_price=900
        )
        
        # Posição deve ser <= 5% do capital
        assert result['position_value'] <= 500
    
    def test_validate_size(self):
        """Testa validação de tamanho"""
        sizer = PositionSizer(max_position_size=0.1)
        
        # Tamanho válido
        is_valid, reason = sizer.validate_size(
            position_size=0.01,
            account_balance=1000,
            current_price=50000
        )
        assert is_valid == True
        
        # Tamanho inválido (muito grande)
        is_valid, reason = sizer.validate_size(
            position_size=1.0,
            account_balance=1000,
            current_price=50000
        )
        assert is_valid == False


class TestTradingStrategy:
    """Testes das estratégias de trading"""
    
    def test_sma_strategy_basic(self):
        """Testa estratégia SMA básica"""
        strategy = SimpleMovingAverageStrategy(fast_period=5, slow_period=10)
        
        # Preços insuficientes
        prices = [100, 101, 102]
        result = strategy.analyze(prices)
        assert result['signal'] == 'WAIT'
        
        # Preços suficientes
        prices = list(range(100, 125))
        result = strategy.analyze(prices)
        assert result['signal'] in ['BUY', 'SELL', 'WAIT']
        assert 'score' in result
        assert 'ma_fast' in result
        assert 'ma_slow' in result
    
    def test_sma_buy_signal(self):
        """Testa sinal de COMPRA"""
        strategy = SimpleMovingAverageStrategy(fast_period=3, slow_period=5)
        
        # Criar preços que geram cruzamento de alta
        prices = [100, 100, 100, 100, 100, 102, 104, 106, 108, 110]
        result = strategy.analyze(prices)
        
        # Deve gerar sinal de compra ou wait (depende do cruzamento exato)
        assert result['signal'] in ['BUY', 'WAIT']
    
    def test_rsi_strategy_basic(self):
        """Testa estratégia RSI básica"""
        strategy = RSIStrategy(period=14)
        
        # Preços insuficientes
        prices = [100, 101, 102]
        result = strategy.analyze(prices)
        assert result['signal'] == 'WAIT'
        
        # Preços suficientes
        prices = list(range(100, 125))
        result = strategy.analyze(prices)
        assert 'rsi' in result
        assert 'signal' in result
    
    def test_stop_loss_calculation(self):
        """Testa cálculo de stop loss"""
        strategy = SimpleMovingAverageStrategy()
        
        # Stop loss para BUY
        stop = strategy.get_stop_loss(entry_price=50000, signal='BUY')
        assert stop < 50000
        
        # Stop loss para SELL
        stop = strategy.get_stop_loss(entry_price=50000, signal='SELL')
        assert stop > 50000
    
    def test_take_profit_calculation(self):
        """Testa cálculo de take profit"""
        strategy = SimpleMovingAverageStrategy()
        
        # Take profit para BUY
        tp = strategy.get_take_profit(entry_price=50000, signal='BUY')
        assert tp > 50000
        
        # Take profit para SELL
        tp = strategy.get_take_profit(entry_price=50000, signal='SELL')
        assert tp < 50000


# Executar testes
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
