"""
Optimized rate limiter with token bucket algorithm
High-performance implementation with minimal overhead
"""

import time
import threading
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from collections import deque

from core.logger import get_logger
from core.exceptions import RateLimitException
from core.singleton import Singleton

logger = get_logger(__name__)


@dataclass
class RateLimit:
    """Rate limit configuration"""
    max_requests: int
    window_seconds: float
    name: str


class TokenBucket:
    """
    Token bucket algorithm for rate limiting
    More efficient than sliding window for high-throughput scenarios
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self._lock = threading.RLock()
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Calculate tokens to add
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> Tuple[bool, float]:
        """
        Try to consume tokens
        
        Args:
            tokens: Number of tokens to consume
        
        Returns:
            (success, wait_time)
        """
        with self._lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True, 0.0
            
            # Calculate wait time
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.refill_rate
            
            return False, wait_time
    
    def peek(self) -> float:
        """Get current token count without consuming"""
        with self._lock:
            self._refill()
            return self.tokens


class OptimizedRateLimiter(Singleton):
    """
    Optimized rate limiter using token bucket algorithm
    Thread-safe with minimal locking overhead
    """
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        # Binance rate limits (production values)
        self.limits = {
            'orders_per_second': RateLimit(50, 1.0, 'orders/sec'),  # Conservative
            'weight_per_minute': RateLimit(1200, 60.0, 'weight/min'),
            'orders_per_day': RateLimit(200000, 86400.0, 'orders/day')
        }
        
        # Token buckets for each limit
        self.buckets = {
            'orders_per_second': TokenBucket(50, 50.0),  # 50 tokens, 50/sec refill
            'weight_per_minute': TokenBucket(1200, 20.0),  # 1200 tokens, 20/sec refill
            'orders_per_day': TokenBucket(200000, 2.31)  # 200k tokens, ~2.31/sec refill
        }
        
        # Metrics
        self.total_requests = 0
        self.total_blocked = 0
        self.total_wait_time = 0.0
        
        self._lock = threading.RLock()
        self._initialized = True
        
        logger.info("OptimizedRateLimiter initialized with token bucket algorithm")
    
    def check_limit(
        self,
        weight: int = 1,
        block: bool = False
    ) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        Check if request can proceed
        
        Args:
            weight: Request weight (for weight-based limit)
            block: If True, wait for available tokens
        
        Returns:
            (can_proceed, wait_time, reason)
        """
        with self._lock:
            self.total_requests += 1
            
            # Check each limit
            max_wait = 0.0
            blocking_limit = None
            
            # Orders per second
            can_proceed, wait = self.buckets['orders_per_second'].consume(1)
            if not can_proceed:
                max_wait = max(max_wait, wait)
                blocking_limit = 'orders_per_second'
            
            # Weight per minute
            can_proceed_weight, wait_weight = self.buckets['weight_per_minute'].consume(weight)
            if not can_proceed_weight:
                if wait_weight > max_wait:
                    max_wait = wait_weight
                    blocking_limit = 'weight_per_minute'
            
            # Orders per day
            can_proceed_day, wait_day = self.buckets['orders_per_day'].consume(1)
            if not can_proceed_day:
                if wait_day > max_wait:
                    max_wait = wait_day
                    blocking_limit = 'orders_per_day'
            
            # Determine if we can proceed
            if can_proceed and can_proceed_weight and can_proceed_day:
                return True, None, None
            
            # Rate limited
            self.total_blocked += 1
            
            if block and max_wait > 0:
                self.total_wait_time += max_wait
                logger.warning(f"Rate limited, waiting {max_wait:.2f}s ({blocking_limit})")
                time.sleep(max_wait)
                return True, max_wait, blocking_limit
            
            reason = f"Rate limit exceeded: {blocking_limit}"
            return False, max_wait, reason
    
    def acquire(self, weight: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make request (blocking)
        
        Args:
            weight: Request weight
            timeout: Maximum time to wait (None = wait forever)
        
        Returns:
            True if acquired, False if timeout
        
        Raises:
            RateLimitException: If cannot acquire within timeout
        """
        start_time = time.time()
        
        while True:
            can_proceed, wait_time, reason = self.check_limit(weight, block=False)
            
            if can_proceed:
                return True
            
            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    raise RateLimitException(
                        f"Rate limit timeout after {elapsed:.2f}s",
                        retry_after=wait_time,
                        limit_type=reason
                    )
            
            # Wait minimum time
            if wait_time and wait_time > 0:
                sleep_time = min(wait_time, 0.1)  # Max 100ms at a time
                time.sleep(sleep_time)
    
    def get_status(self) -> Dict:
        """Get current rate limiter status"""
        with self._lock:
            status = {
                'buckets': {},
                'metrics': {
                    'total_requests': self.total_requests,
                    'total_blocked': self.total_blocked,
                    'total_wait_time': round(self.total_wait_time, 2),
                    'block_rate': round(
                        self.total_blocked / max(self.total_requests, 1) * 100, 2
                    )
                }
            }
            
            for name, bucket in self.buckets.items():
                limit = self.limits[name]
                status['buckets'][name] = {
                    'available_tokens': round(bucket.peek(), 2),
                    'capacity': bucket.capacity,
                    'utilization': round(
                        (1 - bucket.peek() / bucket.capacity) * 100, 2
                    ),
                    'limit_name': limit.name
                }
            
            return status
    
    def reset(self) -> None:
        """Reset rate limiter (for testing)"""
        with self._lock:
            for bucket in self.buckets.values():
                bucket.tokens = float(bucket.capacity)
                bucket.last_refill = time.time()
            
            self.total_requests = 0
            self.total_blocked = 0
            self.total_wait_time = 0.0
            
            logger.info("Rate limiter reset")


# Factory function
def get_rate_limiter() -> OptimizedRateLimiter:
    """Get global rate limiter instance"""
    return OptimizedRateLimiter()
