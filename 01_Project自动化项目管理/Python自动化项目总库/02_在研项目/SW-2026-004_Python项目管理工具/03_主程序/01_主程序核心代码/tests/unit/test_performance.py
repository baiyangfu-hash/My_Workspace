# -*- coding: utf-8 -*-
"""
性能优化测试
"""

import pytest
import time
import threading
from src.utils.cache import CacheManager, CacheEntry, cached
from src.utils.rate_limiter import TokenBucket, SlidingWindowCounter, RateLimiter


class TestCacheEntry:
    """测试缓存条目"""
    
    def test_entry_creation(self):
        entry = CacheEntry("test_key", "test_value", ttl=60)
        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.is_expired is False
        assert entry.ttl_remaining is not None
        assert entry.ttl_remaining > 0
    
    def test_entry_expiration(self):
        entry = CacheEntry("test_key", "test_value", ttl=0.01)
        time.sleep(0.02)
        assert entry.is_expired is True
    
    def test_entry_no_expiration(self):
        entry = CacheEntry("test_key", "test_value", ttl=None)
        time.sleep(0.01)
        assert entry.is_expired is False
        assert entry.ttl_remaining is None
    
    def test_entry_touch(self):
        entry = CacheEntry("test_key", "test_value")
        assert entry.hit_count == 0
        entry.touch()
        assert entry.hit_count == 1
        entry.touch()
        assert entry.hit_count == 2


class TestCacheManager:
    """测试缓存管理器"""
    
    def setup_method(self):
        CacheManager._instance = None
        self.cache = CacheManager(max_size=10, default_ttl=1.0)
    
    def teardown_method(self):
        CacheManager._instance = None
    
    def test_set_and_get(self):
        self.cache.set("key1", "value1")
        assert self.cache.get("key1") == "value1"
    
    def test_get_default(self):
        assert self.cache.get("nonexistent") is None
        assert self.cache.get("nonexistent", default="default") == "default"
    
    def test_delete(self):
        self.cache.set("key1", "value1")
        assert self.cache.delete("key1") is True
        assert self.cache.get("key1") is None
    
    def test_delete_nonexistent(self):
        assert self.cache.delete("nonexistent") is False
    
    def test_clear_all(self):
        for i in range(5):
            self.cache.set(f"key{i}", f"value{i}")
        count = self.cache.clear()
        assert count == 5
        assert self.cache.size == 0
    
    def test_clear_namespace(self):
        self.cache.set("key1", "v1", namespace="ns1")
        self.cache.set("key2", "v2", namespace="ns1")
        self.cache.set("key3", "v3", namespace="ns2")
        count = self.cache.clear(namespace="ns1")
        assert count == 2
        assert self.cache.get("key1", namespace="ns1") is None
        assert self.cache.get("key3", namespace="ns2") == "v3"
    
    def test_ttl_expiration(self):
        self.cache.set("key1", "value1", ttl=0.05)
        assert self.cache.get("key1") == "value1"
        time.sleep(0.1)
        assert self.cache.get("key1") is None
    
    def test_lru_eviction(self):
        cache = CacheManager(max_size=3, default_ttl=10)
        cache.set("key1", "v1")
        cache.set("key2", "v2")
        cache.set("key3", "v3")
        cache.set("key4", "v4")
        assert cache.size == 3
        assert cache.get("key1") is None
        assert cache.get("key4") == "v4"
    
    def test_get_or_set(self):
        call_count = 0
        
        def factory():
            nonlocal call_count
            call_count += 1
            return "factory_value"
        
        result1 = self.cache.get_or_set("key1", factory)
        assert result1 == "factory_value"
        assert call_count == 1
        
        result2 = self.cache.get_or_set("key1", factory)
        assert result2 == "factory_value"
        assert call_count == 1
    
    def test_exists(self):
        self.cache.set("key1", "value1")
        assert self.cache.exists("key1") is True
        assert self.cache.exists("nonexistent") is False
    
    def test_get_many(self):
        self.cache.set("key1", "v1")
        self.cache.set("key2", "v2")
        result = self.cache.get_many(["key1", "key2", "key3"])
        assert result == {"key1": "v1", "key2": "v2"}
    
    def test_set_many(self):
        count = self.cache.set_many({"key1": "v1", "key2": "v2"})
        assert count == 2
        assert self.cache.get("key1") == "v1"
    
    def test_cleanup_expired(self):
        self.cache.set("key1", "v1", ttl=0.01)
        self.cache.set("key2", "v2", ttl=10)
        time.sleep(0.05)
        cleaned = self.cache.cleanup_expired()
        assert cleaned == 1
        assert self.cache.size == 1
    
    def test_stats(self):
        self.cache.set("key1", "v1")
        self.cache.get("key1")
        self.cache.get("nonexistent")
        stats = self.cache.stats
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["sets"] == 1
        assert stats["size"] == 1
    
    def test_thread_safety(self):
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(100):
                    self.cache.set(f"thread{thread_id}_key{i}", f"value{i}")
                    self.cache.get(f"thread{thread_id}_key{i}")
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
    
    def test_namespace_isolation(self):
        self.cache.set("key1", "ns1_value", namespace="ns1")
        self.cache.set("key1", "ns2_value", namespace="ns2")
        assert self.cache.get("key1", namespace="ns1") == "ns1_value"
        assert self.cache.get("key1", namespace="ns2") == "ns2_value"


class TestTokenBucket:
    """测试令牌桶"""
    
    def test_initial_tokens(self):
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        assert bucket.available_tokens == 10
    
    def test_consume(self):
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        assert bucket.consume(1) is True
        assert bucket.available_tokens == 9
    
    def test_consume_too_many(self):
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        assert bucket.consume(6) is False
        assert bucket.consume(5) is True
    
    def test_refill(self):
        bucket = TokenBucket(capacity=10, refill_rate=100.0)
        bucket.consume(10)
        time.sleep(0.05)
        assert bucket.available_tokens > 0
    
    def test_wait_for_token(self):
        bucket = TokenBucket(capacity=1, refill_rate=100.0)
        bucket.consume(1)
        result = bucket.wait_for_token(1, timeout=1.0)
        assert result is True


class TestSlidingWindowCounter:
    """测试滑动窗口计数器"""
    
    def test_allow_request(self):
        counter = SlidingWindowCounter(window_size=1, limit=5)
        for _ in range(5):
            assert counter.allow_request() is True
        assert counter.allow_request() is False
    
    def test_remaining(self):
        counter = SlidingWindowCounter(window_size=1, limit=5)
        counter.allow_request()
        counter.allow_request()
        assert counter.remaining == 3
    
    def test_current_count(self):
        counter = SlidingWindowCounter(window_size=1, limit=5)
        counter.allow_request()
        counter.allow_request()
        counter.allow_request()
        assert counter.current_count == 3


class TestRateLimiter:
    """测试限流管理器"""
    
    def setup_method(self):
        RateLimiter._instance = None
        self.limiter = RateLimiter(default_rate=5, default_window=1, burst_size=3)
    
    def teardown_method(self):
        RateLimiter._instance = None
    
    def test_check_rate_limit(self):
        for _ in range(5):
            allowed, info = self.limiter.check_rate_limit("user1")
            assert allowed is True
        
        allowed, info = self.limiter.check_rate_limit("user1")
        assert allowed is False
    
    def test_different_identifiers(self):
        for _ in range(5):
            self.limiter.check_rate_limit("user1")
        
        allowed, _ = self.limiter.check_rate_limit("user2")
        assert allowed is True
    
    def test_check_burst(self):
        for _ in range(3):
            allowed, info = self.limiter.check_burst("user1")
            assert allowed is True
        
        allowed, info = self.limiter.check_burst("user1")
        assert allowed is False
    
    def test_get_stats(self):
        self.limiter.check_rate_limit("user1")
        self.limiter.check_rate_limit("user1")
        stats = self.limiter.get_stats("user1")
        assert stats["current_count"] == 2
    
    def test_reset(self):
        for _ in range(5):
            self.limiter.check_rate_limit("user1")
        self.limiter.reset("user1")
        allowed, _ = self.limiter.check_rate_limit("user1")
        assert allowed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
