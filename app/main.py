import logging
import os
import sys

from app.config import ConfigError, load_config

log = logging.getLogger("uptime-monitor")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    path = os.environ.get("CONFIG_PATH", "config.yaml")
    try:
        config = load_config(path)
    except (ConfigError, FileNotFoundError) as exc:
        log.error("Не удалось загрузить конфиг %s: %s", path, exc)
        return 1

    log.info("Uptime Monitor запущен: %d целей, интервал %ss", len(config.targets), config.interval_seconds)
    for target in config.targets:
        log.info("цель: %s -> %s", target.name, target.url)
    return 0


if __name__ == "__main__":
    sys.exit(main())