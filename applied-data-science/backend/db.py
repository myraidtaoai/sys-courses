from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


MODULE_DIR = Path(__file__).resolve().parent
DB_CANDIDATES = [
    MODULE_DIR / "database" / "bikes.db",
    Path.cwd() / "database" / "bikes.db",
    MODULE_DIR.parent / "database" / "bikes.db",
    Path("/var/task/backend/database/bikes.db"),
    Path("/var/task/database/bikes.db"),
    Path("/var/task/bikes.db"),
    Path("/var/database/bikes.db"),
]
DB_PATH = next((path for path in DB_CANDIDATES if path.exists()), DB_CANDIDATES[0])


def connect() -> sqlite3.Connection:
    # Use URI connection with mode=ro to prevent SQLite from attempting to 
    # write lock/journal files in Vercel's read-only filesystem.
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def rows(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with closing(connect()) as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def row(query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with closing(connect()) as conn:
        result = conn.execute(query, params).fetchone()
    return dict(result) if result else None


def scalar(query: str, params: tuple[Any, ...] = ()) -> Any:
    with closing(connect()) as conn:
        result = conn.execute(query, params).fetchone()
    return result[0] if result else None
