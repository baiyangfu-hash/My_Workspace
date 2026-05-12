# -*- coding: utf-8 -*-
"""
缓存管理模块
提供内存缓存、TTL过期、LRU淘汰策略
"""

import time
import threading
import hashlib
import json
from typing import Any, Optional, Callable, Dict, List
from collections import OrderedDict
from functools import wraps

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CacheEntry:
    """缓存条目"""
    
    __slots__ = ('key', 'value', 'expire_at', 'created_at', 'hit_count', 'last_accessed')
    
    def __init__(self, key: str, value: Any, ttl: Optional[float] = None):
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.expire_at = self.created_at + ttl if ttl else None
        self.hit_count = 0
        self.last_accessed = self.created_at
    
    @property
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expire_at is None:
            return False
        return time.time() > self.expire_at
    
    @property
    def ttl_remaining(self) -> Optional[float]:
        """获取剩余TTL"""
        if self.expire_at is None:
            return None
        remaining = self.expire_at - time.time()
        return max(0, remaining)
    
    def touch(self):
        """更新访问时间"""
        self.hit_count += 1
        self.last_accessed = time.time()


class CacheManager:
    """
    线程安全的内存缓存管理器
    支持TTL过期、LRU淘汰策略、命名空间隔离
    """
    
    _instance: Optional["CacheManager"] = None
    _lock = threading.Lock()
    
    def __new__(cls, max_size: int = 1000, default_ttl: float = 300.0):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        if self._initialized:
            return
        
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._namespaces: Dict[str, set] = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "sets": 0,
            "deletes": 0,
        }
        self._lock = threading.RLock()
        self._initialized = True
        
        logger.info(f"缓存管理器初始化: max_size={max_size}, default_ttl={default_ttl}s")
    
    def _make_key(self, key: str, namespace: Optional[str] = None) -> str:
        """生成缓存键"""
        if namespace:
            return f"{namespace}:{key}"
        return key
    
    def _evict_if_needed(self):
        """如果超过最大容量，淘汰最久未使用的条目"""
        while len(self._cache) > self._max_size:
            if self._cache:
                evicted_key, _ = self._cache.popitem(last=False)
                self._stats["evictions"] += 1
                self._cleanup_namespace(evicted_key)
                logger.debug(f"缓存淘汰: {evicted_key}")
            else:
                break
    
    def _cleanup_namespace(self, full_key: str):
        """清理命名空间记录"""
        for ns, keys in self._namespaces.items():
            if full_key in keys:
                keys.discard(full_key)
                if not keys:
                    del self._namespaces[ns]
                break
    
    def get(self, key: str, namespace: Optional[str] = None, default: Any = None) -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            namespace: 命名空间
            default: 默认值
            
        Returns:
            缓存值或默认值
        """
        full_key = self._make_key(key, namespace)
        
        with self._lock:
            entry = self._cache.get(full_key)
            
            if entry is None:
                self._stats["misses"] += 1
                return default
            
            if entry.is_expired:
                del self._cache[full_key]
                self._cleanup_namespace(full_key)
                self._stats["misses"] += 1
                return default
            
            entry.touch()
            self._cache.move_to_end(full_key)
            self._stats["hits"] += 1
            
            return entry.value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        namespace: Optional[str] = None
    ) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None使用默认TTL
            namespace: 命名空间
            
        Returns:
            是否设置成功
        """
        full_key = self._make_key(key, namespace)
        actual_ttl = ttl if ttl is not None else self._default_ttl
        
        with self._lock:
            if full_key in self._cache:
                del self._cache[full_key]
            
            entry = CacheEntry(full_key, value, actual_ttl)
            self._cache[full_key] = entry
            self._cache.move_to_end(full_key)
            
            if namespace:
                if namespace not in self._namespaces:
                    self._namespaces[namespace] = set()
                self._namespaces[namespace].add(full_key)
            
            self._stats["sets"] += 1
            self._evict_if_needed()
            
            return True
    
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
            namespace: 命名空间
            
        Returns:
            是否删除成功
        """
        full_key = self._make_key(key, namespace)
        
        with self._lock:
            if full_key in self._cache:
                del self._cache[full_key]
                self._cleanup_namespace(full_key)
                self._stats["deletes"] += 1
                return True
            return False
    
    def clear(self, namespace: Optional[str] = None) -> int:
        """
        清除缓存
        
        Args:
            namespace: 命名空间，None清除所有
            
        Returns:
            清除的条目数
        """
        with self._lock:
            if namespace:
                keys = self._namespaces.get(namespace, set()).copy()
                for key in keys:
                    if key in self._cache:
                        del self._cache[key]
                count = len(keys)
                if namespace in self._namespaces:
                    del self._namespaces[namespace]
                logger.info(f"清除命名空间 '{namespace}' 缓存: {count} 条")
            else:
                count = len(self._cache)
                self._cache.clear()
                self._namespaces.clear()
                logger.info(f"清除所有缓存: {count} 条")
            
            return count
    
    def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[float] = None,
        namespace: Optional[str] = None
    ) -> Any:
        """
        获取缓存值，如果不存在则通过工厂函数创建
        
        Args:
            key: 缓存键
            factory: 值工厂函数
            ttl: 过期时间
            namespace: 命名空间
            
        Returns:
            缓存值
        """
        value = self.get(key, namespace)
        if value is not None:
            return value
        
        value = factory()
        if value is not None:
            self.set(key, value, ttl=ttl, namespace=namespace)
        return value
    
    def exists(self, key: str, namespace: Optional[str] = None) -> bool:
        """检查缓存是否存在"""
        full_key = self._make_key(key, namespace)
        with self._lock:
            entry = self._cache.get(full_key)
            if entry is None:
                return False
            if entry.is_expired:
                del self._cache[full_key]
                self._cleanup_namespace(full_key)
                return False
            return True
    
    def get_many(self, keys: List[str], namespace: Optional[str] = None) -> Dict[str, Any]:
        """批量获取缓存值"""
        result = {}
        for key in keys:
            value = self.get(key, namespace)
            if value is not None:
                result[key] = value
        return result
    
    def set_many(self, mapping: Dict[str, Any], ttl: Optional[float] = None, namespace: Optional[str] = None) -> int:
        """批量设置缓存值"""
        count = 0
        for key, value in mapping.items():
            if self.set(key, value, ttl=ttl, namespace=namespace):
                count += 1
        return count
    
    def cleanup_expired(self) -> int:
        """清理所有过期条目"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]
            for key in expired_keys:
                del self._cache[key]
                self._cleanup_namespace(key)
            
            if expired_keys:
                logger.info(f"清理过期缓存: {len(expired_keys)} 条")
            
            return len(expired_keys)
    
    @property
    def size(self) -> int:
        """当前缓存大小"""
        with self._lock:
            return len(self._cache)
    
    @property
    def stats(self) -> dict:
        """获取缓存统计信息"""
        with self._lock:
            total = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0
            
            return {
                **self._stats,
                "size": len(self._cache),
                "max_size": self._max_size,
                "hit_rate": round(hit_rate, 2),
                "namespaces": list(self._namespaces.keys()),
            }
    
    def reset_stats(self):
        """重置统计信息"""
        with self._lock:
            for key in self._stats:
                self._stats[key] = 0


def cached(
    key_prefix: str,
    ttl: Optional[float] = None,
    namespace: Optional[str] = None
):
    """
    缓存装饰器
    
    Args:
        key_prefix: 缓存键前缀
        ttl: 过期时间
        namespace: 命名空间
        
    Usage:
        @cached("user_info", ttl=60, namespace="users")
        def get_user(user_id: str):
            return db.query(User).get(user_id)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = CacheManager()
            
            key_parts = [key_prefix]
            key_parts.extend(str(a) for a in args[1:])
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()[:16]
            
            cached_value = cache.get(cache_key, namespace=namespace)
            if cached_value is not None:
                return cached_value
            
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl=ttl, namespace=namespace)
            
            return result
        
        wrapper.cache_clear = lambda: None
        return wrapper
    return decorator


cache = CacheManager()
