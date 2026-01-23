"""Tests for the cache module."""

import time

from app.services.cache import (
    _cache,
    cached,
    get_cache_stats,
    invalidate,
    invalidate_all,
)


def setup_function():
    """Clear cache before each test."""
    _cache.clear()


def test_cached_returns_result():
    """Test that cached decorator returns function result."""
    call_count = 0

    @cached(ttl_seconds=60)
    def my_func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    result = my_func(5)
    assert result == 10
    assert call_count == 1


def test_cached_caches_result():
    """Test that cached decorator caches on repeated calls."""
    call_count = 0

    @cached(ttl_seconds=60)
    def my_func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    result1 = my_func(5)
    result2 = my_func(5)

    assert result1 == result2 == 10
    assert call_count == 1  # Only called once


def test_cached_different_args():
    """Test that different args have separate cache entries."""
    call_count = 0

    @cached(ttl_seconds=60)
    def my_func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    result1 = my_func(5)
    result2 = my_func(10)

    assert result1 == 10
    assert result2 == 20
    assert call_count == 2


def test_cached_expires():
    """Test that cached values expire after TTL."""
    call_count = 0

    @cached(ttl_seconds=0.1)  # 100ms TTL
    def my_func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    result1 = my_func(5)
    time.sleep(0.15)  # Wait for expiry
    result2 = my_func(5)

    assert result1 == result2 == 10
    assert call_count == 2  # Called twice due to expiry


def test_invalidate_by_prefix():
    """Test that invalidate removes matching entries."""

    @cached(ttl_seconds=60, prefix="student")
    def get_student(id):
        return {"id": id}

    @cached(ttl_seconds=60, prefix="quiz")
    def get_quiz(id):
        return {"id": id}

    # Populate cache
    get_student(1)
    get_student(2)
    get_quiz(1)

    assert len(_cache) == 3

    # Invalidate students
    count = invalidate("student")

    assert count == 2
    assert len(_cache) == 1  # Only quiz remains


def test_invalidate_all():
    """Test that invalidate_all clears entire cache."""

    @cached(ttl_seconds=60, prefix="test")
    def my_func(x):
        return x

    my_func(1)
    my_func(2)
    my_func(3)

    assert len(_cache) == 3

    count = invalidate_all()

    assert count == 3
    assert len(_cache) == 0


def test_get_cache_stats():
    """Test cache statistics."""

    @cached(ttl_seconds=0.1, prefix="stats")
    def my_func(x):
        return x

    my_func(1)
    my_func(2)

    stats = get_cache_stats()
    assert stats["total_entries"] == 2
    assert stats["active_entries"] == 2
    assert stats["expired_entries"] == 0

    # Wait for expiry
    time.sleep(0.15)

    stats = get_cache_stats()
    assert stats["total_entries"] == 2
    assert stats["expired_entries"] == 2
    assert stats["active_entries"] == 0


def test_cached_with_kwargs():
    """Test that kwargs are included in cache key."""
    call_count = 0

    @cached(ttl_seconds=60)
    def my_func(x, multiplier=2):
        nonlocal call_count
        call_count += 1
        return x * multiplier

    result1 = my_func(5, multiplier=2)
    result2 = my_func(5, multiplier=3)
    result3 = my_func(5, multiplier=2)

    assert result1 == 10
    assert result2 == 15
    assert result3 == 10
    assert call_count == 2  # Different kwargs = different cache entries
