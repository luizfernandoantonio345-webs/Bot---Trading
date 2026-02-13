"""
High-performance caching system with LRU and TTL support
Optimized for trading system requirements
"""

import time
from typing import Optional, Any, Callable, Dict, Tuple
from functools import wraps
from collections import OrderedDict
import threading
import pickle
import hashlib


class LRUCache:
    """
    Thread-safe LRU (Least Recently Used) Cache with TTL support
    Optimized for high-performance requirements
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        """
        Args:
            max_size: Maximum number of items to cache
            default_ttl: Default time-to-live in seconds (None = no expiration)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache
        
        Args:
            key: Cache key
            default: Default value if key not found
        
        Returns:
            Cached value or default
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return default
            
            value, expiry = self._cache[key]
            
            # Check if expired
            if expiry is not None and time.time() > expiry:
                del self._cache[key]
                self._misses += 1
                return default
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default_ttl)
        """
        with self._lock:
            # Calculate expiry time
            if ttl is None:
                ttl = self.default_ttl
            
            expiry = time.time() + ttl if ttl is not None else None
            
            # Update cache
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                # Check size limit
                if len(self._cache) >= self.max_size:
                    # Remove least recently used
                    self._cache.popitem(last=False)
            
            self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            now = time.time()
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if expiry is not None and now > expiry
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': round(hit_rate, 2),
                'utilization': round(len(self._cache) / self.max_size * 100, 2)
            }


class CacheManager:
    """
    Central cache manager with multiple cache instances
    """
    
    def __init__(self):
        self._caches: Dict[str, LRUCache] = {}
        self._lock = threading.RLock()
    
    def get_cache(
        self,
        name: str,
        max_size: int = 1000,
        default_ttl: Optional[float] = None
    ) -> LRUCache:
        """
        Get or create a named cache instance
        
        Args:
            name: Cache name
            max_size: Maximum cache size
            default_ttl: Default TTL in seconds
        
        Returns:
            LRUCache instance
        """
        with self._lock:
            if name not in self._caches:
                self._caches[name] = LRUCache(max_size, default_ttl)
            return self._caches[name]
    
    def clear_all(self) -> None:
        """Clear all caches"""
        with self._lock:
            for cache in self._caches.values():
                cache.clear()
    
    def cleanup_all_expired(self) -> int:
        """
        Cleanup expired entries from all caches
        
        Returns:
            Total number of entries removed
        """
        with self._lock:
            total_removed = 0
            for cache in self._caches.values():
                total_removed += cache.cleanup_expired()
            return total_removed
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches"""
        with self._lock:
            return {
                name: cache.get_stats()
                for name, cache in self._caches.items()
            }


# Global cache manager instance
_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    return _cache_manager


def cached(
    cache_name: str = 'default',
    ttl: Optional[float] = 300,  # 5 minutes default
    key_func: Optional[Callable] = None
):
    """
    Decorator for caching function results
    
    Args:
        cache_name: Name of cache to use
        ttl: Time-to-live in seconds
        key_func: Optional function to generate cache key from args
    
    Example:
        @cached(cache_name='prices', ttl=60)
        def get_price(symbol: str) -> float:
            return fetch_price_from_api(symbol)
    """
    def decorator(func: Callable) -> Callable:
        cache = _cache_manager.get_cache(cache_name, default_ttl=ttl)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_data = pickle.dumps((func.__name__, args, tuple(sorted(kwargs.items()))))
                cache_key = hashlib.md5(key_data).hexdigest()
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result
        
        # Add cache management methods
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_stats = lambda: cache.get_stats()
        
        return wrapper
    
    return decorator
