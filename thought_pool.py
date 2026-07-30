"""Standalone, source-labelled thought pool.

Thoughts are small transient notes. They are deliberately independent from
memory scoring, drives, mood, persona, or any other application runtime.
"""
from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path
from typing import Optional

from utils import now_iso

VALID_KINDS = {"flit", "rumination", "question", "observation"}


class ThoughtPool:
    def __init__(self, buckets_dir: str):
        self.path = Path(buckets_dir) / "thoughts.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS thoughts (
                id TEXT PRIMARY KEY, text TEXT NOT NULL, kind TEXT NOT NULL,
                weight REAL NOT NULL, source TEXT NOT NULL,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            )""")

    def add(self, text: str, kind: str = "flit", weight: float = 0.5,
            source: str = "manual") -> dict:
        text = text.strip()
        if not text:
            raise ValueError("thought text cannot be empty")
        if kind not in VALID_KINDS:
            raise ValueError(f"kind must be one of {sorted(VALID_KINDS)}")
        item = {"id": uuid.uuid4().hex[:12], "text": text, "kind": kind,
                "weight": max(0.0, min(1.0, float(weight))),
                "source": source.strip() or "manual", "created_at": now_iso(),
                "updated_at": now_iso()}
        with self._connect() as conn:
            conn.execute("INSERT INTO thoughts VALUES (:id,:text,:kind,:weight,:source,:created_at,:updated_at)", item)
        return item

    def list(self, limit: int = 20, kind: Optional[str] = None) -> list[dict]:
        sql, args = "SELECT * FROM thoughts", []
        if kind:
            sql += " WHERE kind = ?"; args.append(kind)
        sql += " ORDER BY weight DESC, updated_at DESC LIMIT ?"; args.append(max(1, min(200, limit)))
        with self._connect() as conn:
            return [dict(r) for r in conn.execute(sql, args)]

    def update(self, thought_id: str, *, text: Optional[str] = None,
               kind: Optional[str] = None, weight: Optional[float] = None) -> Optional[dict]:
        current = self.get(thought_id)
        if not current:
            return None
        if text is not None:
            if not text.strip(): raise ValueError("thought text cannot be empty")
            current["text"] = text.strip()
        if kind is not None:
            if kind not in VALID_KINDS: raise ValueError(f"kind must be one of {sorted(VALID_KINDS)}")
            current["kind"] = kind
        if weight is not None: current["weight"] = max(0.0, min(1.0, float(weight)))
        current["updated_at"] = now_iso()
        with self._connect() as conn:
            conn.execute("""UPDATE thoughts SET text=:text,kind=:kind,weight=:weight,
                source=:source,created_at=:created_at,updated_at=:updated_at WHERE id=:id""", current)
        return current

    def get(self, thought_id: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM thoughts WHERE id = ?", (thought_id,)).fetchone()
            return dict(row) if row else None

    def delete(self, thought_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM thoughts WHERE id = ?", (thought_id,))
            return cur.rowcount > 0
