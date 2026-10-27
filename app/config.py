"""Загрузка и валидация config.yaml."""
from dataclasses import dataclass
from pathlib import Path

import yaml


class ConfigError(ValueError):
    """Ошибка в конфиг файле."""


@dataclass(frozen=True)
class Target:
    name: str
    url: str


@dataclass(frozen=True)
class Config:
    interval_seconds: int
    timeout_seconds: float
    targets: list[Target]


def load_config(path: str | Path) -> Config:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"Некорректный YAML: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError("Конфиг должен быть словарём")

    raw_targets = raw.get("targets")
    if not raw_targets or not isinstance(raw_targets, list):
        raise ConfigError("Нужен непустой список targets")

    targets = []
    for item in raw_targets:
        if not isinstance(item, dict) or "name" not in item or "url" not in item:
            raise ConfigError("Каждая цель должна содержать name и url")
        if not str(item["url"]).startswith(("http://", "https://")):
            raise ConfigError(f"URL должен начинаться с http(s)://: {item['url']}")
        targets.append(Target(name=str(item["name"]), url=str(item["url"])))

    interval = int(raw.get("interval_seconds", 30))
    timeout = float(raw.get("timeout_seconds", 5))
    if interval <= 0 or timeout <= 0:
        raise ConfigError("interval_seconds и timeout_seconds должны быть > 0")

    return Config(interval_seconds=interval, timeout_seconds=timeout, targets=targets)