"""Proxy Manager Module for IP Rotation and Anti-Detection.

Manages residential proxy rotation for enhanced anti-detection capabilities.
Integrates with HAR analysis for intelligent IP rotation strategies.
"""

import random
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    requests = None


class ProxyManager:
    """Manages residential proxy rotation for anti-detection."""

    def __init__(self, proxy_list: Optional[List[str]] = None):
        """Initialize proxy manager.

        Args:
            proxy_list: List of proxy strings in format 'IP:PORT:USERNAME:PASSWORD'
        """
        self.proxies = []
        self.current_index = 0
        self.last_rotation = time.time()
        self.cooldown_period = 30  # seconds between rotations

        if proxy_list:
            self.load_proxies(proxy_list)

    def load_proxies(self, proxy_list: List[str]) -> None:
        """Load proxies from list of proxy strings."""
        self.proxies = []
        for proxy_str in proxy_list:
            if proxy_str.strip():
                proxy_info = self._parse_proxy_string(proxy_str.strip())
                if proxy_info:
                    self.proxies.append(proxy_info)

        # Shuffle for random initial order
        random.shuffle(self.proxies)

    def _parse_proxy_string(self, proxy_str: str) -> Optional[Dict[str, str]]:
        """Parse proxy string into components.

        Format: IP:PORT:USERNAME:PASSWORD
        """
        try:
            parts = proxy_str.split(":")
            if len(parts) != 4:
                return None

            ip, port, username, password = parts

            # Validate IP format
            try:
                urlparse(f"http://{ip}")
            except Exception:
                return None

            return {
                "ip": ip,
                "port": port,
                "username": username,
                "password": password,
                "proxy_url": f"http://{username}:{password}@{ip}:{port}",
                "https_url": f"http://{username}:{password}@{ip}:{port}",
            }
        except Exception:
            return None

    def get_current_proxy(self) -> Optional[Dict[str, str]]:
        """Get current proxy configuration."""
        if not self.proxies:
            return None
        return self.proxies[self.current_index]

    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy in rotation."""
        if not self.proxies:
            return None

        self.current_index = (self.current_index + 1) % len(self.proxies)
        self.last_rotation = time.time()
        return self.proxies[self.current_index]

    def rotate_on_rate_limit(
        self, backoff_seconds: int = 10
    ) -> Optional[Dict[str, str]]:
        """Rotate to new proxy when rate limited, with backoff.

        Args:
            backoff_seconds: Base backoff time before rotation

        Returns:
            New proxy configuration
        """
        # Add cooldown to prevent rapid rotations
        elapsed = time.time() - self.last_rotation
        if elapsed < self.cooldown_period:
            sleep_time = self.cooldown_period - elapsed
            time.sleep(sleep_time)

        # Add random backoff
        backoff = backoff_seconds + random.uniform(0, 5)
        time.sleep(backoff)

        return self.get_next_proxy()

    def get_proxy_for_requests(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration formatted for requests library."""
        proxy = self.get_current_proxy()
        if not proxy:
            return None

        return {"http": proxy["proxy_url"], "https": proxy["https_url"]}

    def test_proxy(self, proxy_info: Dict[str, str], timeout: int = 10) -> bool:
        """Test if a proxy is working.

        Args:
            proxy_info: Proxy configuration
            timeout: Request timeout in seconds

        Returns:
            True if proxy works, False otherwise
        """
        if not requests:
            return True  # Can't test without requests

        try:
            proxies = {
                "http": proxy_info["proxy_url"],
                "https": proxy_info["https_url"],
            }

            response = requests.get(
                "https://ipv4.webshare.io/",
                proxies=proxies,
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0 (compatible; ProxyTest/1.0)"},
            )

            return response.status_code == 200
        except Exception:
            return False

    def get_working_proxy(self, max_attempts: int = 3) -> Optional[Dict[str, str]]:
        """Get a working proxy, testing up to max_attempts proxies.

        Args:
            max_attempts: Maximum number of proxies to test

        Returns:
            Working proxy configuration, or None if none work
        """
        for _ in range(min(max_attempts, len(self.proxies))):
            proxy = self.get_current_proxy()
            if not proxy:
                break

            if self.test_proxy(proxy):
                return proxy

            # Try next proxy
            self.get_next_proxy()

        return None

    def get_proxy_stats(self) -> Dict[str, any]:
        """Get statistics about proxy usage."""
        return {
            "total_proxies": len(self.proxies),
            "current_index": self.current_index,
            "last_rotation": self.last_rotation,
            "time_since_rotation": time.time() - self.last_rotation,
        }


# Default proxy list from user's Webshare credentials
DEFAULT_WEBHARE_PROXIES = [
    "142.111.48.253:7030:zpwhlpsh:f12nqx4tf9bl",
    "198.23.239.134:6540:zpwhlpsh:f12nqx4tf9bl",
    "45.38.107.97:6014:zpwhlpsh:f12nqx4tf9bl",
    "107.172.163.27:6543:zpwhlpsh:f12nqx4tf9bl",
    "64.137.96.74:6641:zpwhlpsh:f12nqx4tf9bl",
    "154.203.43.247:5536:zpwhlpsh:f12nqx4tf9bl",
    "84.247.60.125:6095:zpwhlpsh:f12nqx4tf9bl",
    "216.10.27.159:6837:zpwhlpsh:f12nqx4tf9bl",
    "142.111.67.146:5611:zpwhlpsh:f12nqx4tf9bl",
    "142.147.128.93:6593:zpwhlpsh:f12nqx4tf9bl",
]


def create_default_proxy_manager() -> ProxyManager:
    """Create proxy manager with default Webshare proxies."""
    manager = ProxyManager()
    manager.load_proxies(DEFAULT_WEBHARE_PROXIES)
    return manager
