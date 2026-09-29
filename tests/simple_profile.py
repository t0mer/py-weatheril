#!/usr/bin/env python3
"""Simple profiling script for weatheril utils"""

import cProfile
import pstats
from weatheril.utils import get_value, fetch_data
from unittest.mock import patch, Mock


def test_get_value():
    """Test get_value function"""
    data = {"a": {"b": {"c": 42}}}
    for i in range(10000):
        get_value(data, "a", "b", dict)
        get_value(data, "a", "b", dict, "c", int)
        get_value(data, "x", "y", int, default_value=-1)


def test_fetch_data_without_cache():
    """Test fetch_data function without caching (simulating old behavior)"""
    # Clear cache to simulate no caching
    from weatheril.utils import _fetch_data_cache

    _fetch_data_cache.clear()

    mock_response = Mock()
    mock_response.json.return_value = {"data": "value"}

    with patch("weatheril.utils.requests.get", return_value=mock_response):
        for i in range(1000):
            fetch_data("http://example.com/api")


def test_fetch_data_with_cache():
    """Test fetch_data function with caching"""
    # Clear cache first
    from weatheril.utils import _fetch_data_cache

    _fetch_data_cache.clear()

    mock_response = Mock()
    mock_response.json.return_value = {"data": "value"}

    with patch("weatheril.utils.requests.get", return_value=mock_response):
        # Call the same URL multiple times - should benefit from caching
        for i in range(1000):
            fetch_data("http://example.com/api")


def main():
    """Run profiling"""
    print("Profiling get_value...")
    profiler = cProfile.Profile()
    profiler.enable()
    test_get_value()
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(10)

    print("\nProfiling fetch_data WITHOUT caching (1000 API calls)...")
    profiler = cProfile.Profile()
    profiler.enable()
    test_fetch_data_without_cache()
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(10)

    print("\nProfiling fetch_data WITH caching (1000 calls but only 1 API call)...")
    profiler = cProfile.Profile()
    profiler.enable()
    test_fetch_data_with_cache()
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(10)


if __name__ == "__main__":
    main()
