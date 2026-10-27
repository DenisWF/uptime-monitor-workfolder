import pytest

from app.config import ConfigError, load_config


def write(tmp_path, text):
    p = tmp_path / "config.yaml"
    p.write_text(text, encoding="utf-8")
    return p


def test_valid_config(tmp_path):
    p = write(tmp_path, """
interval_seconds: 10
timeout_seconds: 2
targets:
  - {name: Example, url: "https://example.com"}
""")
    cfg = load_config(p)
    assert cfg.interval_seconds == 10
    assert cfg.timeout_seconds == 2.0
    assert cfg.targets[0].name == "Example"


def test_defaults(tmp_path):
    p = write(tmp_path, 'targets:\n  - {name: A, url: "http://a.local"}\n')
    cfg = load_config(p)
    assert cfg.interval_seconds == 30
    assert cfg.timeout_seconds == 5.0


def test_broken_yaml(tmp_path):
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, "targets: [unclosed"))


def test_empty_targets(tmp_path):
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, "targets: []"))


def test_bad_url(tmp_path):
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, "targets:\n  - {name: A, url: ftp://x}\n"))