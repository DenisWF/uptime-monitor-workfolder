from app.checker import CheckResult


def test_upsert_target_is_idempotent(storage):
    first = storage.upsert_target("Example", "https://example.com")
    second = storage.upsert_target("Example renamed", "https://example.com")
    assert first == second


def test_uptime_percent(storage):
    tid = storage.upsert_target("Example", "https://example.com")
    storage.save_check(tid, CheckResult(True, 200, 120))
    storage.save_check(tid, CheckResult(True, 200, 100))
    storage.save_check(tid, CheckResult(True, 200, 90))
    storage.save_check(tid, CheckResult(False, 500, 300, "HTTP 500"))
    assert storage.uptime_percent(tid) == 75.0


def test_uptime_none_without_checks(storage):
    tid = storage.upsert_target("Empty", "https://empty.local")
    assert storage.uptime_percent(tid) is None