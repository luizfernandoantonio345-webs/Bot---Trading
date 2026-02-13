"""
Rate Limiter para Binance API
Previne banimento por excesso de requisições
"""
import time
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class RateLimitManager:
    """
    Gerencia rate limits da Binance API
    - Orders: 10/segundo, 200,000/dia
    - Weight: 1200/minuto
    """
    
    def __init__(self):
        # Limites da Binance
        self.limits = {
            'orders_per_second': 10,
            'orders_per_day': 200000,
            'weight_per_minute': 1200
        }
        
        # Contadores
        self.orders_this_second = []
        self.orders_today = 0
        self.weight_this_minute = []
        
        # Timestamps
        self.day_start = time.time()
        
    def can_execute_order(self, weight: int = 1) -> tuple[bool, str]:
        """
        Verifica se pode executar uma ordem
        
        Args:
            weight: Peso da requisição (default=1)
            
        Returns:
            (pode_executar, motivo)
        """
        now = time.time()
        
        # Limpar contadores antigos
        self._cleanup_counters(now)
        
        # Verificar orders/segundo
        if len(self.orders_this_second) >= self.limits['orders_per_second']:
            return False, f"Limite de {self.limits['orders_per_second']} orders/segundo atingido"
        
        # Verificar weight/minuto
        current_weight = sum(w for _, w in self.weight_this_minute)
        if current_weight + weight > self.limits['weight_per_minute']:
            return False, f"Limite de weight/minuto atingido ({current_weight}/{self.limits['weight_per_minute']})"
        
        # Verificar orders/dia
        if self.orders_today >= self.limits['orders_per_day']:
            return False, f"Limite diário de {self.limits['orders_per_day']} orders atingido"
        
        return True, "OK"
    
    def record_order(self, weight: int = 1):
        """Registra uma ordem executada"""
        now = time.time()
        
        self.orders_this_second.append(now)
        self.weight_this_minute.append((now, weight))
        self.orders_today += 1
        
        logger.debug(f"Order registrada - Weight: {weight}, Total hoje: {self.orders_today}")
    
    def _cleanup_counters(self, now: float):
        """Remove contadores expirados"""
        # Orders do último segundo
        self.orders_this_second = [
            t for t in self.orders_this_second 
            if now - t < 1.0
        ]
        
        # Weight do último minuto
        self.weight_this_minute = [
            (t, w) for t, w in self.weight_this_minute 
            if now - t < 60.0
        ]
        
        # Resetar contador diário
        if now - self.day_start > 86400:  # 24 horas
            self.orders_today = 0
            self.day_start = now
            logger.info("Contador diário resetado")
    
    def get_status(self) -> Dict:
        """Retorna status atual dos rate limits"""
        now = time.time()
        self._cleanup_counters(now)
        
        current_weight = sum(w for _, w in self.weight_this_minute)
        
        return {
            'orders_this_second': len(self.orders_this_second),
            'orders_limit_second': self.limits['orders_per_second'],
            'orders_today': self.orders_today,
            'orders_limit_day': self.limits['orders_per_day'],
            'weight_this_minute': current_weight,
            'weight_limit_minute': self.limits['weight_per_minute'],
            'weight_available': self.limits['weight_per_minute'] - current_weight
        }
    
    def wait_if_needed(self, weight: int = 1) -> float:
        """
        Espera se necessário para não violar rate limits
        
        Returns:
            Tempo de espera em segundos
        """
        can_execute, reason = self.can_execute_order(weight)
        
        if can_execute:
            return 0.0
        
        # Calcular tempo de espera baseado no motivo
        if "segundo" in reason:
            wait_time = 1.0
        elif "minuto" in reason:
            wait_time = 60.0
        else:
            wait_time = 0.0
        
        if wait_time > 0:
            logger.warning(f"Rate limit atingido: {reason}. Aguardando {wait_time}s")
        
        return wait_time


# Instância global
rate_limiter = RateLimitManager()
