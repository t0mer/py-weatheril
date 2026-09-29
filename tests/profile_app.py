#!/usr/bin/env python3
"""Simple profiling script for weatheril application"""

import cProfile
import pstats
import io
from weatheril.utils import get_value, fetch_data
from weatheril.consts import HE_LOCATIONS
import json
from unittest.mock import patch, Mock


def test_get_value_performance():
    """Test get_value performance with various inputs"""
    # Test data
    nested_data = {"level1": {"level2": {"level3": {"value": 42}}}}

    flat_data = {"key": "value"}

    # Run multiple iterations to get meaningful profiling data
    for i in range(10000):
        # Test nested access
        get_value(nested_data, "level1", "level2", dict)
        get_value(nested_data, "level1", "level2", dict, "level3", dict)
        temp_dict = get_value(nested_data, "level1", "level2", dict, "level3", dict)
        if temp_dict:
            get_value(temp_dict, "value", None, int)

        # Test flat access
        get_value(flat_data, "key", None, str)
        get_value(flat_data, "missing", None, str, default_value="default")

        # Test type conversions
        get_value(flat_data, "key", None, int)
        get_value(flat_data, "key", None, float)


def test_fetch_data_performance():
    """Test fetch_data performance with mocking"""
    mock_response = Mock()
    mock_response.json.return_value = {"data": {"test": "value"}}

    with patch("weatheril.utils.requests.get", return_value=mock_response):
        for i in range(1000):
            fetch_data("http://example.com/api/data")


def main():
    """Main profiling function"""
    print("Starting profiling...")

    # Profile get_value
    print("\n=== Profiling get_value ===")
    profiler = cProfile.Profile()
    profiler.enable()
    test_get_value_performance()
    profiler.disable()

    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats("cumulative")
    ps.print_stats(20)
    print(s.getvalue())

    # Profile fetch_data
    print("\n=== Profiling fetch_data ===")
    profiler = cProfile.Profile()
    profiler.enable()
    test_fetch_data_performance()
    profiler.disable()

    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats("cumulative")
    ps.print_stats(20)
    print(s.getvalue())


if __name__ == "__main__":
    main()
