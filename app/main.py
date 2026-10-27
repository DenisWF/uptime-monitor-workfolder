"""Точка входа Uptime Monitor."""
import logging
import os
import signal
import sys
import time
from pathlib import Path

import httpx
import psycopg

from app.checker import check_url
from app.config import ConfigError, load_config
from app.storage import Storage

log = logging.getLogger("uptime-monitor")
_running = True


def _stop(*_: object) -> None:
    global _running
    _running = False


def connect_with_retry(dsn: str, attempts: int = 10, delay: float = 3.0) -> Storage:
    """БД в контейнере может стартовать дольше приложения, поэтому пробуем несколько раз."""
    for attempt in range(1, attempts + 1):
        try:
            return Storage(dsn)
        except psycopg.OperationalError as exc:
            log.warning("БД недоступна (%d/%d): %s", attempt, attempts, exc)
            time.sleep(delay)
    raise RuntimeError("Не удалось подключиться к БД")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    default_path = Path(__file__).resolve().parent.parent / "config.yaml"
    path = os.environ.get("CONFIG_PATH", str(default_path))
    try:
        config = load_config(path)
    except (ConfigError, FileNotFoundError) as exc:
        log.error("Не удалось загрузить конфиг %s: %s", path, exc)
        return 1

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        log.error("Не задана переменная окружения DATABASE_URL")
        return 1

    storage = connect_with_retry(dsn)
    target_ids = {t.url: storage.upsert_target(t.name, t.url) for t in config.targets}

    log.info("Старт: %d целей, интервал %ss", len(config.targets), config.interval_seconds)
    with httpx.Client(timeout=config.timeout_seconds, follow_redirects=True) as client:
        while _running:
            for target in config.targets:
                result = check_url(target.url, client=client)
                storage.save_check(target_ids[target.url], result)
                log.info(
                    "%s -> up=%s code=%s %dms %s",
                    target.name, result.is_up, result.status_code,
                    result.response_ms, result.error or "",
                )
            for _ in range(config.interval_seconds):
                if not _running:
                    break
                time.sleep(1)

    storage.close()
    log.info("Остановлено")
    return 0


if __name__ == "__main__":
    sys.exit(main())