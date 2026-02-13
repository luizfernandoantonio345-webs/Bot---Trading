"""
Singleton pattern implementation for shared resources
Thread-safe and optimized for performance
"""

import threading
from typing import Dict, Any, Type, TypeVar


T = TypeVar('T')


class SingletonMeta(type):
    """
    Thread-safe Singleton metaclass
    Uses double-checked locking for optimal performance
    """
    
    _instances: Dict[Type, Any] = {}
    _lock: threading.Lock = threading.Lock()
    
    def __call__(cls: Type[T], *args, **kwargs) -> T:
        # First check without lock (fast path)
        if cls not in cls._instances:
            # Acquire lock for thread safety
            with cls._lock:
                # Double-check after acquiring lock
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        
        return cls._instances[cls]
    
    @classmethod
    def reset_instance(mcs, cls: Type) -> None:
        """Reset singleton instance (useful for testing)"""
        with mcs._lock:
            if cls in mcs._instances:
                del mcs._instances[cls]
    
    @classmethod
    def reset_all(mcs) -> None:
        """Reset all singleton instances"""
        with mcs._lock:
            mcs._instances.clear()


class Singleton(metaclass=SingletonMeta):
    """
    Base class for singletons
    
    Example:
        class DatabaseConnection(Singleton):
            def __init__(self):
                if not hasattr(self, 'initialized'):
                    self.conn = create_connection()
                    self.initialized = True
    """
    pass


def singleton(cls: Type[T]) -> Type[T]:
    """
    Decorator to make a class a singleton
    
    Example:
        @singleton
        class Config:
            def __init__(self):
                self.settings = load_settings()
    """
    return type(cls.__name__, (cls, Singleton), dict(cls.__dict__))
