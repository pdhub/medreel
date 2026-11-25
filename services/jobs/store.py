"""Job state and queue in one SQLite table.

shortcut: SQLite on a shared volume, one worker; move to Postgres (already in the target stack) for multiple hosts.
"""
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

# target status -> statuses it may come from
ALLOWED = {
    "uploaded": ("created", "uploaded"),
    "queued": ("uploaded", "failed"),
    "transcribing": ("queued",),
    "planning": ("transcribing",),
    "rendering": ("planning",),
    "done": ("rendering",),
    "failed": ("queued", "transcribing", "planning", "rendering"),
}


class JobNotFound(Exception):
    def __init__(self, job_id):
        super().__init__(job_id)
        self.job_id = job_id


class InvalidTransition(Exception):
    def __init__(self, job_id, current, target):
        super().__init__(f"job is {current}; cannot move to {target}")
        self.job_id, self.current, self.target = job_id, current, target


def _now():
    return datetime.now(timezone.utc).isoformat()


class JobStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._q("PRAGMA journal_mode=WAL")
        self._q("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, status TEXT NOT NULL, error TEXT,"
                " created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")

    def _q(self, sql, args=()):
        db = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            return [dict(r) for r in db.execute(sql, args).fetchall()]
        finally:
            db.close()

    def create(self) -> dict:
        job_id, now = str(uuid.uuid4()), _now()
        self._q("INSERT INTO jobs VALUES (?, 'created', NULL, ?, ?)", (job_id, now, now))
        return self.get(job_id)

    def get(self, job_id: str) -> dict:
        rows = self._q("SELECT * FROM jobs WHERE id = ?", (job_id,))
        if not rows:
            raise JobNotFound(job_id)
        return rows[0]

    def transition(self, job_id: str, target: str, error: str | None = None) -> dict:
        sources = ALLOWED[target]
        rows = self._q(f"UPDATE jobs SET status = ?, error = ?, updated_at = ? WHERE id = ? AND status IN"
                       f" ({','.join('?' * len(sources))}) RETURNING *", (target, error, _now(), job_id, *sources))
        if rows:
            return rows[0]
        raise InvalidTransition(job_id, self.get(job_id)["status"], target)

    def claim_next(self) -> str | None:
        """Atomically move the oldest queued job to transcribing and return its id."""
        rows = self._q("UPDATE jobs SET status = 'transcribing', updated_at = ? WHERE status = 'queued' AND id ="
                       " (SELECT id FROM jobs WHERE status = 'queued' ORDER BY updated_at LIMIT 1) RETURNING id",
                       (_now(),))
        return rows[0]["id"] if rows else None
