"""Unit tests for proxy manager functionality.

Tests proxy rotation, testing, and anti-detection capabilities.
These tests MUST FAIL initially (no proxy_manager implementation yet) - TDD approach.
"""

import time
from unittest.mock import patch

import pytest

# Test proxy data
TEST_PROXIES = [
    "142.111.48.253:7030:testuser:testpass",
    "198.23.239.134:6540:testuser:testpass",
    "45.38.107.97:6014:testuser:testpass",
]


class TestProxyManager:
    """Test cases for proxy manager functionality."""

    def test_proxy_parsing(self) -> None:
        """Test parsing of proxy strings into components."""
        # This test will fail until proxy_manager is implemented
        from src.proxy_manager import ProxyManager

        manager = ProxyManager()
        manager.load_proxies(TEST_PROXIES)

        assert len(manager.proxies) == 3

        # Find the proxy with the expected IP (order may vary due to shuffling)
        proxy = None
        for p in manager.proxies:
            if p["ip"] == "142.111.48.253":
                proxy = p
                break

        assert proxy is not None
        assert proxy["port"] == "7030"
        assert proxy["username"] == "testuser"
        assert proxy["password"] == "testpass"
        assert "proxy_url" in proxy
        assert "https_url" in proxy

    def test_proxy_rotation(self) -> None:
        """Test basic proxy rotation functionality."""
        # This test will fail until proxy_manager is implemented
        from src.proxy_manager import ProxyManager

        manager = ProxyManager()
        manager.load_proxies(TEST_PROXIES)

        # Should have loaded all proxies
        assert len(manager.proxies) == 3

        # Get first proxy
        proxy1 = manager.get_current_proxy()
        assert proxy1 is not None
        first_ip = proxy1["ip"]

        # Rotate to next - should be different
        proxy2 = manager.get_next_proxy()
        assert proxy2 is not None
        assert proxy2["ip"] != first_ip

        # Rotate again - should be different from previous
        proxy3 = manager.get_next_proxy()
        assert proxy3 is not None
        assert proxy3["ip"] != proxy2["ip"]

        # Should cycle back to first after all proxies
        proxy4 = manager.get_next_proxy()
        assert proxy4["ip"] == first_ip

        # Verify we cycled through all unique IPs
        all_ips = {proxy1["ip"], proxy2["ip"], proxy3["ip"]}
        assert len(all_ips) == 3  # All different IPs

    def test_proxy_requests_format(self) -> None:
        """Test proxy formatting for requests library."""
        # This test will fail until proxy_manager is implemented
        from src.proxy_manager import ProxyManager

        manager = ProxyManager()
        manager.load_proxies(TEST_PROXIES)

        requests_proxies = manager.get_proxy_for_requests()
        assert requests_proxies is not None
        assert "http" in requests_proxies
        assert "https" in requests_proxies

        # Should contain username:password@ip:port format
        assert "testuser:testpass@" in requests_proxies["http"]
        # Should contain one of the test proxy IPs and ports
        proxy_urls = [requests_proxies["http"], requests_proxies["https"]]
        found_test_proxy = False
        for url in proxy_urls:
            if (
                "142.111.48.253:7030" in url
                or "198.23.239.134:6540" in url
                or "45.38.107.97:6014" in url
            ):
                found_test_proxy = True
                break
        assert found_test_proxy

    def test_rate_limit_rotation(self) -> None:
        """Test intelligent proxy rotation on rate limiting."""
        # This test will fail until proxy_manager is implemented
        from src.proxy_manager import ProxyManager

        manager = ProxyManager()
        manager.load_proxies(TEST_PROXIES)

        # Get initial proxy
        initial_proxy = manager.get_current_proxy()
        initial_ip = initial_proxy["ip"]

        # Simulate rate limiting - should rotate and add delay
        start_time = time.time()
        new_proxy = manager.rotate_on_rate_limit(
            backoff_seconds=0.1
        )  # Short delay for testing
        end_time = time.time()

        assert new_proxy is not None
        assert new_proxy["ip"] != initial_ip  # Should have rotated

        # Should have waited at least the backoff time
        elapsed = end_time - start_time
        assert elapsed >= 0.1

    def test_invalid_proxy_format(self) -> None:
        """Test handling of invalid proxy format strings."""
        # This test will fail until proxy_manager is implemented
        from src.proxy_manager import ProxyManager

        manager = ProxyManager()

        # Test invalid formats
        invalid_proxies = [
            "invalid",
            "1.2.3.4",  # Missing port/user/pass
            "1.2.3.4:8080",  # Missing user/pass
            "1.2.3.4:8080:user",  # Missing password
            "1.2.3.4:8080:user:pass:extra",  # Too many parts
        ]

        for invalid_proxy in invalid_proxies:
            manager.load_proxies([invalid_proxy])
            # Should not add invalid proxies
            assert len(manager.proxies) == 0

    def test_empty_proxy_list(self) -> None:
        """Test behavior with no proxies loaded."""
        # This test will fail until proxy_manager is implemented
        from src.proxy_manager import ProxyManager

        manager = ProxyManager()

        # No proxies loaded
        assert manager.get_current_proxy() is None
        assert manager.get_next_proxy() is None
        assert manager.get_proxy_for_requests() is None

    def test_proxy_stats(self) -> None:
        """Test proxy usage statistics."""
        # This test will fail until proxy_manager is implemented
        from src.proxy_manager import ProxyManager

        manager = ProxyManager()
        manager.load_proxies(TEST_PROXIES)

        stats = manager.get_proxy_stats()
        assert stats["total_proxies"] == 3
        assert "current_index" in stats
        assert "last_rotation" in stats
        assert "time_since_rotation" in stats

    @patch("src.proxy_manager.requests")
    def test_proxy_testing_functionality(self, mock_requests) -> None:
        """Test proxy testing functionality."""
        # This test will fail until proxy_manager is implemented
        from src.proxy_manager import ProxyManager

        # Mock successful response
        mock_response = mock_requests.get.return_value
        mock_response.status_code = 200

        manager = ProxyManager()
        manager.load_proxies(TEST_PROXIES)

        proxy = manager.proxies[0]

        # Test should pass with mocked success
        result = manager.test_proxy(proxy)
        assert result is True

        # Verify requests was called with correct proxy format
        mock_requests.get.assert_called_once()
        call_args = mock_requests.get.call_args
        proxies_used = call_args[1]["proxies"]
        assert "http" in proxies_used
        assert "https" in proxies_used

    @patch("src.proxy_manager.requests")
    def test_proxy_testing_failure(self, mock_requests) -> None:
        """Test proxy testing when proxy fails."""
        # This test will fail until proxy_manager is implemented
        from src.proxy_manager import ProxyManager

        # Mock failed response
        mock_requests.get.side_effect = Exception("Connection failed")

        manager = ProxyManager()
        manager.load_proxies(TEST_PROXIES)

        proxy = manager.proxies[0]

        # Test should fail
        result = manager.test_proxy(proxy)
        assert result is False

    def test_get_working_proxy(self) -> None:
        """Test finding a working proxy from the list."""
        # This test will fail until proxy_manager is implemented
        from src.proxy_manager import ProxyManager

        manager = ProxyManager()
        manager.load_proxies(TEST_PROXIES)

        # Mock test_proxy to return True for first proxy
        original_test = manager.test_proxy
        manager.test_proxy = lambda p: p["ip"] == "142.111.48.253"

        try:
            working_proxy = manager.get_working_proxy()
            assert working_proxy is not None
            assert working_proxy["ip"] == "142.111.48.253"
        finally:
            manager.test_proxy = original_test

    def test_default_proxy_manager_creation(self) -> None:
        """Test creation of default proxy manager with Webshare proxies."""
        # This test will fail until proxy_manager is implemented
        from src.proxy_manager import create_default_proxy_manager

        manager = create_default_proxy_manager()

        # Should have loaded the default proxies
        assert len(manager.proxies) == 10  # From DEFAULT_WEBHARE_PROXIES

        # Should be able to get a proxy
        proxy = manager.get_current_proxy()
        assert proxy is not None
        assert "ip" in proxy
        assert "port" in proxy
        assert "username" in proxy
        assert "password" in proxy

    def test_proxy_cooldown_prevention(self) -> None:
        """Test that rapid rotations are prevented by cooldown."""
        # This test will fail until proxy_manager is implemented
        from src.proxy_manager import ProxyManager

        manager = ProxyManager()
        manager.load_proxies(TEST_PROXIES)
        manager.cooldown_period = 1.0  # 1 second cooldown

        # First rotation should work
        proxy1 = manager.rotate_on_rate_limit(backoff_seconds=0)
        assert proxy1 is not None

        # Immediate second rotation should wait for cooldown
        start_time = time.time()
        proxy2 = manager.rotate_on_rate_limit(backoff_seconds=0)
        end_time = time.time()

        elapsed = end_time - start_time
        assert elapsed >= 1.0  # Should have waited for cooldown
        assert proxy2 is not None
        assert proxy2["ip"] != proxy1["ip"]  # Should have rotated
