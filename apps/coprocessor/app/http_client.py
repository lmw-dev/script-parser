"""
HTTP client manager with connection pooling and timeout optimization
"""

import asyncio
from typing import Optional

import httpx

from .config import PerformanceConfig, TimeoutConfig


class HTTPClientManager:
    """Singleton HTTP client manager with connection pooling"""

    _instance: Optional["HTTPClientManager"] = None
    _client: httpx.AsyncClient | None = None
    _lock = asyncio.Lock()

    def __new__(cls) -> "HTTPClientManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create the shared HTTP client with optimized settings"""
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    # Create HTTP client with connection pooling and timeout optimization
                    timeout = httpx.Timeout(**TimeoutConfig.get_http_timeout())
                    limits = httpx.Limits(**PerformanceConfig.get_http_limits())

                    self._client = httpx.AsyncClient(
                        timeout=timeout,
                        limits=limits,
                        follow_redirects=True,
                        verify=True,
                    )

        return self._client

    async def close(self):
        """Close the HTTP client and cleanup connections"""
        if self._client is not None:
            async with self._lock:
                if self._client is not None:
                    await self._client.aclose()
                    self._client = None

    async def request(
        self, method: str, url: str, timeout_override: float | None = None, **kwargs
    ) -> httpx.Response:
        """
        Make an HTTP request with the shared client

        Args:
            method: HTTP method
            url: Request URL
            timeout_override: Override default timeout for this request
            **kwargs: Additional arguments passed to httpx

        Returns:
            HTTP response
        """
        client = await self.get_client()

        # Override timeout if specified
        if timeout_override is not None:
            original_timeout = client.timeout
            client.timeout = httpx.Timeout(timeout_override)
            try:
                response = await client.request(method, url, **kwargs)
                return response
            finally:
                client.timeout = original_timeout
        else:
            return await client.request(method, url, **kwargs)

    async def post(
        self, url: str, timeout_override: float | None = None, **kwargs
    ) -> httpx.Response:
        """Make a POST request"""
        return await self.request(
            "POST", url, timeout_override=timeout_override, **kwargs
        )

    async def get(
        self, url: str, timeout_override: float | None = None, **kwargs
    ) -> httpx.Response:
        """Make a GET request"""
        return await self.request(
            "GET", url, timeout_override=timeout_override, **kwargs
        )


# Global HTTP client manager instance
http_client_manager = HTTPClientManager()


async def get_http_client() -> httpx.AsyncClient:
    """Get the shared HTTP client instance"""
    return await http_client_manager.get_client()


async def cleanup_http_client():
    """Cleanup HTTP client connections"""
    await http_client_manager.close()
