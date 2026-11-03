"""SQLite persistence for the Aegis Health desktop app.

The app stores each domain collection as JSON records in a single table.
This keeps the nested clinical documents (vitals, notes, invoice line items)
intact while still giving us a real, durable database file.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR.parent
DATA_DIR = APP_DIR / "data"
DB_PATH = DATA_DIR / "aegis_health.db"
SEED_PATH = BASE_DIR / "seed_data.json"

KINDS = [
    "patients",
    "doctors",
    "beds",
    "appointments",
    "emergency_cases",
    "medicines",
    "lab_orders",
    "invoices",
]


class Database:
    def __init__(self, path: Path | None = None, seed_path: Path | None = None) -> None:
        self.path = Path(path or DB_PATH)
        self.seed_path = Path(seed_path or SEED_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()
        if self.is_empty():
            self.seed()

    # ------------------------------------------------------------------ setup
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    kind TEXT NOT NULL,
                    id TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    PRIMARY KEY (kind, id)
                )
                """
            )

    def is_empty(self) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM records").fetchone()
        return not row or row[0] == 0

    # ------------------------------------------------------------------- seed
    def _read_seed(self) -> dict[str, list[dict]]:
        with open(self.seed_path, encoding="utf-8") as handle:
            return json.load(handle)

    def seed(self) -> None:
        self.replace_all(self._read_seed())

    # --------------------------------------------------------------- queries
    def load_all(self) -> dict[str, list[dict]]:
        data: dict[str, list[dict]] = {kind: [] for kind in KINDS}
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT kind, data FROM records ORDER BY kind, position ASC"
            ).fetchall()
        for kind, payload in rows:
            if kind in data:
                data[kind].append(json.loads(payload))
        return data

    # --------------------------------------------------------------- writes
    def replace_kind(self, kind: str, records: list[dict]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM records WHERE kind = ?", (kind,))
            conn.executemany(
                "INSERT INTO records (kind, id, position, data) VALUES (?, ?, ?, ?)",
                [
                    (kind, str(record.get("id", position)), position,
                     json.dumps(record, ensure_ascii=False))
                    for position, record in enumerate(records)
                ],
            )

    def replace_all(self, data: dict[str, list[dict]]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM records")
            for kind in KINDS:
                conn.executemany(
                    "INSERT INTO records (kind, id, position, data) VALUES (?, ?, ?, ?)",
                    [
                        (kind, str(record.get("id", position)), position,
                         json.dumps(record, ensure_ascii=False))
                        for position, record in enumerate(data.get(kind, []))
                    ],
                )

    def reset(self) -> None:
        self.replace_all(self._read_seed())
# Implementation note 66: no functional change.
# Implementation note 67: no functional change.
# Implementation note 68: no functional change.
# Implementation note 69: no functional change.
# Implementation note 70: no functional change.
# Implementation note 151: no functional change.
# Implementation note 152: no functional change.
# Implementation note 153: no functional change.
# Implementation note 154: no functional change.
# Implementation note 155: no functional change.
# Implementation note 156: no functional change.
# Implementation note 157: no functional change.
# Implementation note 158: no functional change.
# Implementation note 159: no functional change.
# Implementation note 160: no functional change.
# Implementation note 161: no functional change.
# Implementation note 162: no functional change.
# Implementation note 163: no functional change.
# Implementation note 164: no functional change.
# Implementation note 165: no functional change.
# Implementation note 166: no functional change.
# Implementation note 167: no functional change.
# Implementation note 168: no functional change.
# Implementation note 169: no functional change.
# Implementation note 170: no functional change.
