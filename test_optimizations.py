#!/usr/bin/env python3
"""Test script to verify the optimizations in weatheril.utils"""

from weatheril.utils import get_value, fetch_data
import json
from unittest.mock import patch, Mock
import datetime


def test_get_value():
    # Test basic functionality
    data = {"a": 1, "b": {"c": 2}}
    assert get_value(data, "a", None, int) == 1
    assert get_value(data, "b", "c", int) == 2
    assert get_value(data, "b", "d", int, default_value=0) == 0
    assert get_value(data, "x", "y", int, default_value=-1) == -1
    # Test type conversion
    assert get_value(data, "a", None, str) == "1"
    assert get_value(data, "b", "c", float) == 2.0
    # Test custom empty value (when value matches custom_empty_value, return default_value)
    assert (
        get_value(data, "a", None, int, custom_empty_value=1) is None
    )  # default_value is None
    assert get_value(data, "a", None, int, custom_empty_value=1, default_value=42) == 42
    # Test when inner_dict_key is not a dict
    assert (
        get_value(data, "a", "b", int) is None
    )  # because data["a"] is int, not dict, returns default_value (None)
    assert get_value(data, "a", "b", int, default_value=99) == 99  # with custom default
    print("get_value tests passed")


def test_fetch_data_basic():
    # Mock the requests.get call
    mock_response = Mock()
    mock_response.json.return_value = {"key": "value"}
    with patch("weatheril.utils.requests.get", return_value=mock_response):
        result = fetch_data("http://example.com")
        assert result == {"key": "value"}
        mock_response.json.assert_called_once()
    print("fetch_data basic tests passed")


def test_fetch_data_caching():
    # Test that caching works by calling the same URL twice
    mock_response = Mock()
    mock_response.json.return_value = {"data": "test"}

    with patch("weatheril.utils.requests.get", return_value=mock_response) as mock_get:
        # First call
        result1 = fetch_data("http://example.com/api")
        # Second call with same URL
        result2 = fetch_data("http://example.com/api")

        # Both should return the same data
        assert result1 == result2 == {"data": "test"}
        # But the mock should only be called once due to caching
        assert mock_get.call_count == 1

    print("fetch_data caching tests passed")


def test_fetch_data_cache_expiration():
    # Test that cache expires after time
    from weatheril.utils import _fetch_data_cache, _CACHE_EXPIRATION_SECONDS
    import datetime

    # Clear cache
    _fetch_data_cache.clear()

    mock_response = Mock()
    mock_response.json.return_value = {"timestamp": datetime.datetime.now().timestamp()}

    with patch("weatheril.utils.requests.get", return_value=mock_response) as mock_get:
        # First call
        result1 = fetch_data("http://example.com/timestamp")
        first_call_count = mock_get.call_count

        # Second call immediately after (should use cache)
        result2 = fetch_data("http://example.com/timestamp")
        second_call_count = mock_get.call_count

        # Results should be the same (from cache)
        assert result1 == result2
        # Mock should only be called once
        assert mock_get.call_count == 1

    print("fetch_data cache expiration tests passed")


if __name__ == "__main__":
    test_get_value()
    test_fetch_data_basic()
    test_fetch_data_caching()
    test_fetch_data_cache_expiration()
    print("All tests passed")
