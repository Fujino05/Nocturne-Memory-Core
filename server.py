"""Headless MCP entry point for the Nocturne Memory Core.

The service intentionally contains no dashboard, persona, desire simulation,
room state, speech analysis, or device telemetry. Dream, latent notes, and
thoughts are optional, source-labelled fermentation layers over the core.
"""
from __future__ import annotations

import asyncio
import os
import random
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

from bucket_manager import BucketManager
from decay_engine import DecayEngine
from dehydrator import Dehydrator
from dream_engine import DreamEngine
from embedding_engine import EmbeddingEngine
from latent_pool import LatentPool
from thought_pool import ThoughtPool
from utils import load_config, setup_logging

config = load_config()
setup_logging(config.get("log_level", "INFO"))
embedding_engine = EmbeddingEngine(config)
bucket_manager = BucketManager(config, embedding_engine)
dehydrator = Dehydrator(config)
decay_engine = DecayEngine(config, bucket_manager)
thought_pool = ThoughtPool(config["buckets_dir"])
latent_pool = LatentPool(config["buckets_dir"])
dream_engine = DreamEngine(config["buckets_dir"], bucket_manager, dehydrator, thought_pool, latent_pool)
mcp = FastMCP("Nocturne Memory Core")


def _items(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(",") if x.strip()]


def _view(bucket: dict, include_content: bool = True) -> dict:
    meta = bucket.get("metadata", {})
    result = {"id": bucket.get("id"), "name": meta.get("name"),
              "type": meta.get("type"), "tags": meta.get("tags", []),
              "domain": meta.get("domain", []), "importance": meta.get("importance", 5),
              "created": meta.get("created"), "last_active": meta.get("last_active"),
              "resolved": bool(meta.get("resolved", False)),
              "pinned": bool(meta.get("pinned", False))}
    if "score" in bucket: result["score"] = bucket["score"]
    if include_content: result["content"] = bucket.get("content", "")
    return result


@mcp.custom_route("/", methods=["GET"])
async def root(_request):
    return JSONResponse({"name": "Nocturne Memory Core", "headless": True,
                         "layers": ["memory", "thought", "latent", "dream"]})


@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    stats = await bucket_manager.get_stats()
    return JSONResponse({"status": "ok", "memories": stats})


@mcp.tool()
async def hold(content: str, kind: Literal["memory", "feel", "writing", "unresolved", "window", "permanent"] = "memory",
               tags: str = "", domain: str = "", importance: int = 5,
               valence: Optional[float] = None, arousal: Optional[float] = None,
               name: str = "", pinned: bool = False, auto_analyze: bool = True,
               merge_similar: bool = True) -> dict:
    """Store a sourced memory. Analysis is optional; no API is required."""
    if not content.strip(): raise ValueError("content cannot be empty")
    analysis = {}
    if auto_analyze and dehydrator.api_available:
        analysis = await dehydrator.analyze(content)
    final_tags = _items(tags) or analysis.get("tags", [])
    final_domain = _items(domain) or analysis.get("domain", []) or ["uncategorized"]
    final_valence = 0.5 if valence is None else valence
    final_arousal = 0.3 if arousal is None else arousal
    if valence is None: final_valence = analysis.get("valence", final_valence)
    if arousal is None: final_arousal = analysis.get("arousal", final_arousal)
    final_name = name.strip() or analysis.get("suggested_name", "")
    bucket_type = "permanent" if kind == "permanent" else ("feel" if kind == "feel" else "dynamic")

    if merge_similar and kind == "memory" and dehydrator.api_available:
        candidates = await bucket_manager.search(content[:500], limit=1)
        if candidates and candidates[0].get("score", 0) >= config.get("merge_threshold", 75):
            target = candidates[0]
            merged = await dehydrator.merge(target.get("content", ""), content)
            await bucket_manager.update(target["id"], content=merged, tags=sorted(set(target["metadata"].get("tags", []) + final_tags)))
            await embedding_engine.generate_and_store(target["id"], merged)
            return {"status": "merged", "memory": _view(await bucket_manager.get(target["id"]))}

    bucket_id = await bucket_manager.create(content=content, tags=final_tags,
        importance=importance, domain=final_domain, valence=final_valence,
        arousal=final_arousal, bucket_type=bucket_type, name=final_name or None,
        pinned=pinned, protected=False, record_kind=kind)
    if kind == "unresolved": await bucket_manager.update(bucket_id, resolved=False)
    await embedding_engine.generate_and_store(bucket_id, content)
    return {"status": "created", "memory": _view(await bucket_manager.get(bucket_id))}


@mcp.tool()
async def breath(query: str = "", limit: int = 5, include_fermentation: bool = True) -> dict:
    """Recall relevant or vivid memories and touch the returned active records."""
    limit = max(1, min(20, limit))
    if query.strip():
        buckets = await bucket_manager.search(query, limit=limit)
    else:
        buckets = await bucket_manager.list_all(False)
        buckets.sort(key=lambda b: (bool(b.get("metadata", {}).get("pinned")),
                                    b.get("metadata", {}).get("last_active", "")), reverse=True)
        buckets = buckets[:limit]
    for bucket in buckets: await bucket_manager.touch(bucket["id"])
    result = {"memories": [_view(b) for b in buckets]}
    if include_fermentation:
        result.update({"latent": latent_pool.list(3, status="approved"),
                       "thoughts": thought_pool.list(3), "dream": dream_engine.latest()})
    return result


@mcp.tool()
async def wander(mode: Literal["recent", "random", "archive", "unresolved", "all"] = "recent",
                 query: str = "", limit: int = 10) -> dict:
    """Browse memories without mutating them."""
    limit = max(1, min(100, limit))
    buckets = await bucket_manager.list_all(include_archive=(mode in {"archive", "all"}))
    if mode == "archive": buckets = [b for b in buckets if "/archive/" in b.get("path", "").replace("\\", "/")]
    elif mode != "all": buckets = [b for b in buckets if "/archive/" not in b.get("path", "").replace("\\", "/")]
    if mode == "unresolved": buckets = [b for b in buckets if not b.get("metadata", {}).get("resolved", False) and b.get("metadata", {}).get("kind") == "unresolved"]
    if query.strip():
        q = query.lower()
        buckets = [b for b in buckets if q in (b.get("content", "") + " " + str(b.get("metadata", {}))).lower()]
    if mode == "random": random.shuffle(buckets)
    else: buckets.sort(key=lambda b: b.get("metadata", {}).get("created", ""), reverse=True)
    return {"mode": mode, "memories": [_view(b) for b in buckets[:limit]]}


@mcp.tool()
async def trace(query: str, limit: int = 30) -> dict:
    """Return a chronological, source-preserving timeline for a literal query."""
    if not query.strip(): raise ValueError("query cannot be empty")
    buckets = await bucket_manager.list_all(include_archive=True)
    q = query.lower()
    matches = [b for b in buckets if q in (b.get("content", "") + " " + str(b.get("metadata", {}))).lower()]
    matches.sort(key=lambda b: b.get("metadata", {}).get("created", ""))
    return {"query": query, "timeline": [_view(b) for b in matches[:max(1, min(200, limit))]]}


@mcp.tool()
async def memory(action: Literal["resolve", "unresolve", "pin", "unpin", "archive", "delete"], memory_id: str) -> dict:
    """Apply an explicit lifecycle action to one memory."""
    if action == "archive": ok = await bucket_manager.archive(memory_id)
    elif action == "delete":
        ok = await bucket_manager.delete(memory_id)
        if ok: embedding_engine.delete_embedding(memory_id)
    else:
        values = {"resolve": {"resolved": True}, "unresolve": {"resolved": False},
                  "pin": {"pinned": True}, "unpin": {"pinned": False}}
        ok = await bucket_manager.update(memory_id, **values[action])
    return {"ok": bool(ok), "action": action, "id": memory_id}


@mcp.tool()
async def thought(action: Literal["add", "list", "update", "delete"] = "list", thought_id: str = "",
                  text: str = "", kind: str = "", weight: float = 0.5,
                  source: str = "manual", limit: int = 20) -> dict:
    """Operate the independent thought pool."""
    if action == "add": return {"thought": thought_pool.add(text, kind or "flit", weight, source)}
    if action == "list": return {"thoughts": thought_pool.list(limit, kind if kind else None)}
    if action == "update": return {"thought": thought_pool.update(thought_id, text=text or None, kind=kind or None, weight=weight)}
    return {"deleted": thought_pool.delete(thought_id)}


@mcp.tool()
async def latent(action: Literal["add", "list", "approve", "consume", "delete"] = "list", note_id: str = "",
                 text: str = "", kind: str = "", source: str = "manual",
                 status: str = "", limit: int = 20) -> dict:
    """Operate explicit latent-note lifecycle states."""
    if action == "add": return {"note": latent_pool.add(text, kind or "fragment", source, status or "draft")}
    if action == "list": return {"notes": latent_pool.list(limit, status or None)}
    target = {"approve": "approved", "consume": "used", "delete": "deleted"}[action]
    return {"note": latent_pool.update(note_id, status=target)}


@mcp.tool()
async def dream(action: Literal["generate", "latest"] = "latest") -> dict:
    """Generate or read a sourced dream synthesis."""
    value = await dream_engine.generate() if action == "generate" else dream_engine.latest()
    return {"dream": value}


@mcp.tool()
async def memory_stats() -> dict:
    """Return storage counts and optional-layer counts."""
    stats = await bucket_manager.get_stats()
    stats.update({"thoughts": len(thought_pool.list(200)),
                  "latent_drafts": len(latent_pool.list(200, "draft")),
                  "latent_approved": len(latent_pool.list(200, "approved")),
                  "has_dream": dream_engine.latest() is not None})
    return stats


if __name__ == "__main__":
    transport = config.get("transport", "stdio")
    if transport in {"streamable-http", "sse"}:
        import uvicorn
        from starlette.middleware.cors import CORSMiddleware
        app = mcp.streamable_http_app() if transport == "streamable-http" else mcp.sse_app()
        app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
        uvicorn.run(app, host=os.environ.get("OMBRE_HOST", "0.0.0.0"), port=int(os.environ.get("PORT", "8000")))
    else:
        mcp.run(transport=transport)
