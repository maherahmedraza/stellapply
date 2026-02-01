
from aiolimiter import AsyncLimiter


class RateLimiter:
    """
    Manages rate limits for different domains/sources.
    Uses aiolimiter to enforce strict rate limits per source.
    """

    def __init__(self):
        self._limiters: dict[str, AsyncLimiter] = {}
        # Default policy: 2 requests per second to be safe
        self._default_rate = 2
        self._default_period = 1.0

    def configure(self, source: str, rate: float, period: float = 1.0):
        """Configure custom rate limit for a specific source"""
        self._limiters[source] = AsyncLimiter(rate, period)

    def _get_limiter(self, source: str) -> AsyncLimiter:
        if source not in self._limiters:
            self._limiters[source] = AsyncLimiter(
                self._default_rate, self._default_period
            )
        return self._limiters[source]

    async def acquire(self, source: str):
        """Acquire a token for the specified source"""
        await self._get_limiter(source).acquire()
