"""Sourced dream synthesis over memories, latent notes, and thoughts only."""
from __future__ import annotations

import json
import random
from pathlib import Path

from utils import now_iso


class DreamEngine:
    def __init__(self, buckets_dir, bucket_manager, dehydrator, thought_pool, latent_pool):
        self.path = Path(buckets_dir) / "latest_dream.json"
        self.bucket_manager = bucket_manager
        self.dehydrator = dehydrator
        self.thought_pool = thought_pool
        self.latent_pool = latent_pool

    async def generate(self, memory_limit: int = 5, thought_limit: int = 4,
                       latent_limit: int = 4) -> dict:
        buckets = await self.bucket_manager.list_all(include_archive=False)
        buckets.sort(key=lambda b: b.get("metadata", {}).get("last_active", ""), reverse=True)
        memories = buckets[:max(1, min(20, memory_limit))]
        thoughts = self.thought_pool.list(thought_limit)
        latent = self.latent_pool.list(latent_limit, status="approved")
        sources = {
            "memories": [{"id": b["id"], "text": b.get("content", "")[:600]} for b in memories],
            "thoughts": [{"id": x["id"], "text": x["text"]} for x in thoughts],
            "latent": [{"id": x["id"], "text": x["text"]} for x in latent],
        }
        if not any(sources.values()): raise ValueError("dream needs at least one memory, thought, or approved latent note")

        if self.dehydrator.api_available:
            prompt = (
                "Create a short dreamlike synthesis from only the supplied sources. "
                "Do not invent biographical facts. Preserve ambiguity. Return plain text.\n\n" +
                json.dumps(sources, ensure_ascii=False)
            )
            response = await self.dehydrator.client.chat.completions.create(
                model=self.dehydrator.model,
                messages=[{"role": "system", "content": "You compose sourced, compact dream fragments."},
                          {"role": "user", "content": prompt}],
                max_tokens=500, temperature=0.8)
            text = (response.choices[0].message.content or "").strip()
            mode = "model"
        else:
            fragments = [x["text"] for group in sources.values() for x in group if x.get("text")]
            random.shuffle(fragments)
            text = " / ".join(fragments[:6])
            mode = "deterministic-collage"
        dream = {"created_at": now_iso(), "mode": mode, "text": text, "sources": sources}
        self.path.write_text(json.dumps(dream, ensure_ascii=False, indent=2), "utf-8")
        return dream

    def latest(self):
        try: return json.loads(self.path.read_text("utf-8"))
        except (OSError, json.JSONDecodeError): return None
