# -*- coding: utf-8 -*-
"""
请求限流模块
提供令牌桶和滑动窗口限流算法
"""

import time
import threading
from typing import Optional, Dict, List
from collections import deque

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TokenBucket:
    """
    令牌桶限流器
    
    原理：
    - 桶中存放令牌，以固定速率添加令牌
    - 每次请求消耗一个令牌
    - 桶满时不再添加令牌
    - 桶空时拒绝请求
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: 桶容量（最大令牌数）
            refill_rate: 令牌填充速率（每秒添加的令牌数）
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._tokens = float(capacity)
        self._last_refill = time.time()
        self._lock = threading.Lock()
    
    def _refill(self):
        """补充令牌"""
        now = time.time()
        elapsed = now - self._last_refill
        new_tokens = elapsed * self.refill_rate
        self._tokens = min(self.capacity, self._tokens + new_tokens)
        self._last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """
        消耗令牌
        
        Args:
            tokens: 需要消耗的令牌数
            
        Returns:
            是否允许请求
        """
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False
    
    @property
    def available_tokens(self) -> float:
        """获取可用令牌数"""
        with self._lock:
            self._refill()
            return self._tokens
    
    def wait_for_token(self, tokens: int = 1, timeout: float = 30.0) -> bool:
        """
        等待令牌可用
        
        Args:
            tokens: 需要的令牌数
            timeout: 最大等待时间（秒）
            
        Returns:
            是否获取到令牌
        """
        start = time.time()
        while time.time() - start < timeout:
            if self.consume(tokens):
                return True
            wait_time = min(0.1, tokens / self.refill_rate)
            time.sleep(wait_time)
        return False


class SlidingWindowCounter:
    """
    滑动窗口计数器限流器
    
    原理：
    - 将时间窗口划分为多个小窗口
    - 每个小窗口独立计数
    - 总请求数为所有小窗口计数之和
    """
    
    def __init__(self, window_size: int = 60, limit: int = 100, subdivision: int = 6):
        """
        Args:
            window_size: 时间窗口大小（秒）
            limit: 窗口内最大请求数
            subdivision: 窗口细分数
        """
        self.window_size = window_size
        self.limit = limit
        self.subdivision = subdivision
        self.sub_window_size = window_size / subdivision
        self._windows: deque = deque(maxlen=subdivision)
        self._lock = threading.Lock()
    
    def _get_current_window_index(self) -> int:
        """获取当前子窗口索引"""
        return int(time.time() / self.sub_window_size)
    
    def _cleanup_old_windows(self):
        """清理过期窗口"""
        current_index = self._get_current_window_index()
        while self._windows and self._windows[0][0] <= current_index - self.subdivision:
            self._windows.popleft()
    
    def allow_request(self) -> bool:
        """检查是否允许请求"""
        with self._lock:
            self._cleanup_old_windows()
            current_index = self._get_current_window_index()
            
            if self._windows and self._windows[-1][0] == current_index:
                self._windows[-1] = (current_index, self._windows[-1][1] + 1)
            else:
                self._windows.append((current_index, 1))
            
            total = sum(count for _, count in self._windows)
            return total <= self.limit
    
    @property
    def current_count(self) -> int:
        """获取当前窗口请求计数"""
        with self._lock:
            self._cleanup_old_windows()
            return sum(count for _, count in self._windows)
    
    @property
    def remaining(self) -> int:
        """获取剩余可用请求数"""
        return max(0, self.limit - self.current_count)


class RateLimiter:
    """
    请求限流管理器
    支持多用户/多端点的独立限流
    """
    
    _instance: Optional["RateLimiter"] = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(
        self,
        default_rate: int = 60,
        default_window: int = 60,
        burst_size: int = 10
    ):
        if self._initialized:
            return
        
        self._default_rate = default_rate
        self._default_window = default_window
        self._burst_size = burst_size
        self._sliding_windows: Dict[str, SlidingWindowCounter] = {}
        self._token_buckets: Dict[str, TokenBucket] = {}
        self._stats: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        self._initialized = True
        
        logger.info(f"限流器初始化: rate={default_rate}/min, burst={burst_size}")
    
    def _get_key(self, identifier: str, endpoint: Optional[str] = None) -> str:
        """生成限流键"""
        if endpoint:
            return f"{identifier}:{endpoint}"
        return identifier
    
    def check_rate_limit(
        self,
        identifier: str,
        endpoint: Optional[str] = None,
        rate: Optional[int] = None,
        window: Optional[int] = None
    ) -> tuple[bool, dict]:
        """
        检查请求是否被限流
        
        Args:
            identifier: 标识符（如用户名、IP地址）
            endpoint: 端点路径
            rate: 自定义速率限制
            window: 自定义时间窗口
            
        Returns:
            (是否允许, 限流信息)
        """
        key = self._get_key(identifier, endpoint)
        actual_rate = rate or self._default_rate
        actual_window = window or self._default_window
        
        with self._lock:
            if key not in self._sliding_windows:
                self._sliding_windows[key] = SlidingWindowCounter(
                    window_size=actual_window,
                    limit=actual_rate
                )
            
            window_counter = self._sliding_windows[key]
            allowed = window_counter.allow_request()
            
            info = {
                "allowed": allowed,
                "limit": actual_rate,
                "remaining": window_counter.remaining,
                "reset": int(time.time() + actual_window),
                "identifier": identifier,
                "endpoint": endpoint,
            }
            
            if not allowed:
                logger.warning(f"请求被限流: {key}")
            
            return allowed, info
    
    def check_burst(
        self,
        identifier: str,
        tokens: int = 1
    ) -> tuple[bool, dict]:
        """
        检查突发请求
        
        Args:
            identifier: 标识符
            tokens: 需要的令牌数
            
        Returns:
            (是否允许, 限流信息)
        """
        key = f"burst:{identifier}"
        
        with self._lock:
            if key not in self._token_buckets:
                self._token_buckets[key] = TokenBucket(
                    capacity=self._burst_size,
                    refill_rate=self._burst_size / self._default_window
                )
            
            bucket = self._token_buckets[key]
            allowed = bucket.consume(tokens)
            
            info = {
                "allowed": allowed,
                "available_tokens": bucket.available_tokens,
                "capacity": self._burst_size,
                "identifier": identifier,
            }
            
            return allowed, info
    
    def get_stats(self, identifier: Optional[str] = None) -> dict:
        """获取限流统计信息"""
        with self._lock:
            if identifier:
                key = self._get_key(identifier)
                window = self._sliding_windows.get(key)
                return {
                    "identifier": identifier,
                    "current_count": window.current_count if window else 0,
                    "limit": window.limit if window else self._default_rate,
                    "remaining": window.remaining if window else self._default_rate,
                }
            
            return {
                "total_identifiers": len(self._sliding_windows),
                "default_rate": self._default_rate,
                "default_window": self._default_window,
                "burst_size": self._burst_size,
            }
    
    def reset(self, identifier: Optional[str] = None):
        """重置限流计数"""
        with self._lock:
            if identifier:
                keys_to_remove = [k for k in self._sliding_windows if identifier in k]
                for key in keys_to_remove:
                    del self._sliding_windows[key]
                burst_keys = [k for k in self._token_buckets if identifier in k]
                for key in burst_keys:
                    del self._token_buckets[key]
            else:
                self._sliding_windows.clear()
                self._token_buckets.clear()


rate_limiter = RateLimiter()
