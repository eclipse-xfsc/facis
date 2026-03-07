"""
ORCE webhook client.

Sends tick envelopes to ORCE (Orchestration Engine) via HTTP POST.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from src.config import OrceConfig

logger = logging.getLogger(__name__)


class OrceClient:
    """
    Async HTTP client for pushing tick data to ORCE.

    Posts a unified JSON envelope per simulation tick to ORCE's
    HTTP-in endpoint, where ORCE validates, splits, and publishes
    each feed to Kafka.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:1880",
        webhook_path: str = "/api/sim/tick",
        timeout_seconds: float = 10.0,
    ) -> None:
        self._url = f"{base_url.rstrip('/')}{webhook_path}"
        self._timeout = timeout_seconds
        self._client: httpx.AsyncClient | None = None

    @classmethod
    def from_config(cls, config: OrceConfig) -> OrceClient:
        """Create client from configuration object."""
        return cls(
            base_url=config.url,
            webhook_path=config.webhook_path,
            timeout_seconds=config.timeout_seconds,
        )

    async def connect(self) -> None:
        """Initialize the HTTP client."""
        self._client = httpx.AsyncClient(timeout=self._timeout)
        logger.info(f"ORCE client initialized for {self._url}")

    async def disconnect(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("ORCE client disconnected")

    async def send_tick(self, envelope: dict[str, Any]) -> bool:
        """
        POST a tick envelope to ORCE webhook endpoint.

        Args:
            envelope: The tick envelope dict (from build_tick_envelope).

        Returns:
            True if ORCE accepted the tick (2xx response).
        """
        if self._client is None:
            logger.error("ORCE client not initialized — call connect() first")
            return False

        try:
            response = await self._client.post(self._url, json=envelope)
            if response.is_success:
                logger.debug(f"ORCE tick accepted: {response.status_code}")
                return True
            else:
                logger.warning(
                    f"ORCE tick rejected: {response.status_code} — {response.text[:200]}"
                )
                return False
        except httpx.TimeoutException:
            logger.error(f"ORCE tick timed out after {self._timeout}s")
            return False
        except httpx.ConnectError as e:
            logger.error(f"ORCE connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"ORCE tick error: {e}")
            return False
