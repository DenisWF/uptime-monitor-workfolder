import time
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class CheckResult:
    is_up: bool
    status_code: int | None
    response_ms: int
    error: str | None = None


def check_url(
    url: str,
    timeout: float = 5.0,
    client: httpx.Client | None = None,
) -> CheckResult:
    """Выполняет GET и возвращает результат. Сетевые ошибки не пробрасываются."""
    own_client = client is None
    if client is None:
        client = httpx.Client(timeout=timeout, follow_redirects=True)

    start = time.perf_counter()
    try:
        response = client.get(url)
        elapsed = int((time.perf_counter() - start) * 1000)
        return CheckResult(
            is_up=response.status_code < 400,
            status_code=response.status_code,
            response_ms=elapsed,
        )
    except httpx.HTTPError as exc:
        elapsed = int((time.perf_counter() - start) * 1000)
        return CheckResult(
            is_up=False,
            status_code=None,
            response_ms=elapsed,
            error=f"{type(exc).__name__}: {exc}",
        )
    finally:
        if own_client:
            client.close()