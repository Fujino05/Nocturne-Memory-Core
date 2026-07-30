"""Small JSON lifecycle store for latent notes.

A latent note remains visibly sourced and moves through explicit states:
draft -> approved -> used (or deleted). It has no hidden drive machinery.
"""
from __future__ import annotations

import json
import threading
import uuid
from pathlib import Path
from typing import Optional

from utils import now_iso

VALID_STATUSES = {"draft", "approved", "used", "deleted"}
VALID_KINDS = {"inward", "outward", "question", "fragment"}


class LatentPool:
    def __init__(self, buckets_dir: str):
        self.path = Path(buckets_dir) / "latent_notes.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        if not self.path.exists(): self._write([])

    def _read(self) -> list[dict]:
        with self._lock:
            try:
                value = json.loads(self.path.read_text("utf-8"))
                return value if isinstance(value, list) else []
            except (OSError, json.JSONDecodeError):
                return []

    def _write(self, notes: list[dict]):
        with self._lock:
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(notes, ensure_ascii=False, indent=2), "utf-8")
            tmp.replace(self.path)

    def add(self, text: str, kind: str = "fragment", source: str = "manual",
            status: str = "draft") -> dict:
        if not text.strip(): raise ValueError("latent note text cannot be empty")
        if kind not in VALID_KINDS: raise ValueError(f"kind must be one of {sorted(VALID_KINDS)}")
        if status not in {"draft", "approved"}: raise ValueError("new note status must be draft or approved")
        note = {"id": uuid.uuid4().hex[:12], "text": text.strip(), "kind": kind,
                "source": source.strip() or "manual", "status": status,
                "created_at": now_iso(), "updated_at": now_iso(), "used_at": None}
        notes = self._read(); notes.append(note); self._write(notes)
        return note

    def list(self, limit: int = 20, status: Optional[str] = None) -> list[dict]:
        notes = self._read()
        if status: notes = [n for n in notes if n.get("status") == status]
        notes.sort(key=lambda n: n.get("updated_at", ""), reverse=True)
        return notes[:max(1, min(200, limit))]

    def update(self, note_id: str, *, text: Optional[str] = None,
               kind: Optional[str] = None, status: Optional[str] = None) -> Optional[dict]:
        notes = self._read(); found = None
        for note in notes:
            if note.get("id") != note_id: continue
            if text is not None:
                if not text.strip(): raise ValueError("latent note text cannot be empty")
                note["text"] = text.strip()
            if kind is not None:
                if kind not in VALID_KINDS: raise ValueError(f"kind must be one of {sorted(VALID_KINDS)}")
                note["kind"] = kind
            if status is not None:
                if status not in VALID_STATUSES: raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
                note["status"] = status
                if status == "used": note["used_at"] = now_iso()
            note["updated_at"] = now_iso(); found = note; break
        if found: self._write(notes)
        return found

    def consume(self, note_id: str) -> Optional[dict]:
        return self.update(note_id, status="used")

    def delete(self, note_id: str) -> bool:
        return self.update(note_id, status="deleted") is not None
