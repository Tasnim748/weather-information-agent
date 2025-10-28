# clients/openweather.py
import asyncio
from typing import Any, Dict, List, Optional

import httpx

from settings import Settings


class OpenWeatherClient:
    """
    Minimal OpenWeather HTTP client with retries and timeouts.
    - Uses API key from env (.env) via settings.py
    - Exposes raw-JSON helpers for Geocoding and Current Weather
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = "https://api.openweathermap.org",
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        # Pull settings once and resolve API key:
        # 1) explicit api_key param, else
        # 2) settings.weather_api_key from env/.env
        settings = Settings()
        self.api_key = api_key or settings.weather_api_key
        if not self.api_key:
            # Fail fast at startup if key is missing
            raise ValueError("OpenWeather API key not configured (weather_api_key).")

        # Normalize base URL and store retry/backoff config
        self.base_url = base_url.rstrip("/")
        self.max_retries = max(1, max_retries)
        self.backoff_factor = backoff_factor

        # Single reusable HTTP client with connection pooling and a global timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout_seconds),
            headers={"User-Agent": "weather-info-agent/0.1"},
        )

    async def aclose(self) -> None:
        # Explicitly close the underlying HTTP client (important on shutdown)
        await self._client.aclose()

    async def __aenter__(self) -> "OpenWeatherClient":
        # Enable "async with OpenWeatherClient() as ow:"
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        # Ensure clean teardown when used as a context manager
        await self.aclose()

    async def _get(self, path: str, params: Dict[str, Any]) -> Any:
        """GET with minimal retries, honoring 429 Retry-After when present."""
        # Always include the OpenWeather appid (API key)
        qp = dict(params or {})
        qp["appid"] = self.api_key

        attempt = 0
        last_exc: Optional[Exception] = None

        while attempt < self.max_retries:
            attempt += 1
            try:
                # Perform the HTTP GET; base_url joins with path
                resp = await self._client.get(path, params=qp)

                print(resp.url)

                # Retry on rate limits (429) and server errors (5xx)
                if resp.status_code in (429,) or 500 <= resp.status_code < 600:
                    delay = self._compute_delay(attempt, resp)
                    if attempt < self.max_retries:
                        await asyncio.sleep(delay)
                        continue

                # Raise for 4xx/5xx that we aren't retrying anymore
                resp.raise_for_status()

                # Return raw JSON payload
                return resp.json()

            except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteError, httpx.RemoteProtocolError) as e:
                # Network/transient transport errors: retry with backoff
                last_exc = e
                if attempt < self.max_retries:
                    await asyncio.sleep(self._compute_delay(attempt))
                    continue
                # Out of retries: bubble up the last transport error
                raise

            except httpx.HTTPStatusError:
                # Non-retriable HTTP errors (e.g., 400/401/404) bubble up to caller
                raise

        # Defensive: if loop exits without return/raise, raise the last seen error
        if last_exc:
            raise last_exc
        raise RuntimeError("OpenWeather request failed without an exception.")

    def _compute_delay(self, attempt: int, resp: Optional[httpx.Response] = None) -> float:
        # Simple exponential backoff: factor * 2^(attempt-1)
        base = self.backoff_factor * (2 ** (attempt - 1))

        # If rate limited (429) and server provided Retry-After, respect it
        if resp is not None and resp.status_code == 429:
            ra = resp.headers.get("Retry-After")
            if ra:
                try:
                    seconds = float(ra)
                    # Use the greater of Retry-After and our base backoff
                    return max(seconds, base)
                except ValueError:
                    # If Retry-After isn't a number, ignore and use base
                    pass
        return base

    async def geocode_direct(
        self,
        q: str,
        *,
        limit: int = 1,
        lang: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        OpenWeather Geocoding API (Direct).
        Returns a list of place candidates (raw JSON).
        """
        # Build query params and call the internal GET helper
        params: Dict[str, Any] = {"q": q, "limit": limit}
        if lang:
            params["lang"] = lang
        return await self._get("/geo/1.0/direct", params)

    async def current_weather(
        self,
        *,
        lat: float,
        lon: float,
        units: str = "metric",  # "standard" | "metric" | "imperial"
        lang: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        OpenWeather Current Weather Data (One location).
        Returns the current weather object (raw JSON).
        """
        # Build query params with coordinates and optional localization
        params: Dict[str, Any] = {"lat": lat, "lon": lon, "units": units}
        if lang:
            params["lang"] = lang
        return await self._get("/data/2.5/weather", params)
