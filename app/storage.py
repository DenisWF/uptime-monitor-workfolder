"""Работа с PostgreSQL."""
import psycopg

from app.checker import CheckResult


class Storage:
    def __init__(self, dsn: str) -> None:
        self._conn = psycopg.connect(dsn, autocommit=True)

    def upsert_target(self, name: str, url: str) -> int:
        row = self._conn.execute(
            """
            INSERT INTO targets (name, url) VALUES (%s, %s)
            ON CONFLICT (url) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            (name, url),
        ).fetchone()
        return row[0]

    def save_check(self, target_id: int, result: CheckResult) -> None:
        self._conn.execute(
            """
            INSERT INTO checks (target_id, status_code, response_ms, is_up, error)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (target_id, result.status_code, result.response_ms, result.is_up, result.error),
        )

    def uptime_percent(self, target_id: int, hours: int = 24) -> float | None:
        row = self._conn.execute(
            """
            SELECT ROUND(100.0 * AVG(is_up::int), 2)
            FROM checks
            WHERE target_id = %s
              AND checked_at > now() - make_interval(hours => %s)
            """,
            (target_id, hours),
        ).fetchone()
        return float(row[0]) if row[0] is not None else None

    def close(self) -> None:
        self._conn.close()