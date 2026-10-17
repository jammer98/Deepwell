from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class FetchResult:
    url: str
    status: int | None   # HTTP status, or None if no response arrived
    attempts: int
    error: str | None    # None means success

    @property
    def ok(self) -> bool:
        return self.error is None


async def fetch_one(client: httpx.AsyncClient, url: str, timeout: float) -> FetchResult:
    try:
        resp = await client.get(url, timeout=timeout)
    except httpx.TimeoutException:
        # Must come before HTTPError: TimeoutException is a subclass of it.
        return FetchResult(url, status=None, attempts=1, error="timeout")
    except httpx.HTTPError as exc:
        # Connection refused, DNS failure, reset, and so on.
        return FetchResult(url, status=None, attempts=1, error=f"transport: {type(exc).__name__}")

    if 200 <= resp.status_code < 300:
        return FetchResult(url, status=resp.status_code, attempts=1, error=None)
    return FetchResult(url, status=resp.status_code, attempts=1, error=f"http {resp.status_code}")


async def _demo() -> None:
    base = "http://localhost:8000/r/"
    async with httpx.AsyncClient() as client:
        for rid in ["a", "b", "c"]:
            print(await fetch_one(client, base + rid, timeout=3.0))


if __name__ == "__main__":
    asyncio.run(_demo())