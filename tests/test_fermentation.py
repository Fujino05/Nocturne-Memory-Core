import asyncio
from pathlib import Path

from bucket_manager import BucketManager
from dehydrator import Dehydrator
from dream_engine import DreamEngine
from latent_pool import LatentPool
from thought_pool import ThoughtPool


def config(tmp_path):
    return {"buckets_dir": str(tmp_path), "matching": {"fuzzy_threshold": 0},
            "dehydration": {"api_key": ""}}


def test_thought_pool_crud(tmp_path):
    pool = ThoughtPool(str(tmp_path))
    item = pool.add("A loose question", "question", .8, "test")
    assert pool.get(item["id"])["source"] == "test"
    assert pool.update(item["id"], weight=.2)["weight"] == .2
    assert pool.delete(item["id"])


def test_latent_lifecycle(tmp_path):
    pool = LatentPool(str(tmp_path))
    note = pool.add("not ready yet", source="test")
    assert note["status"] == "draft"
    assert pool.update(note["id"], status="approved")["status"] == "approved"
    assert pool.consume(note["id"])["status"] == "used"


def test_dream_is_sourced_and_works_without_api(tmp_path):
    cfg = config(tmp_path)
    manager = BucketManager(cfg)
    thought = ThoughtPool(str(tmp_path)); latent = LatentPool(str(tmp_path))
    thought.add("a brass stair", source="test")
    note = latent.add("rain behind glass", source="test", status="approved")
    asyncio.run(manager.create("a remembered station", domain=["place"]))
    engine = DreamEngine(tmp_path, manager, Dehydrator(cfg), thought, latent)
    dream = asyncio.run(engine.generate())
    assert dream["mode"] == "deterministic-collage"
    assert dream["sources"]["latent"][0]["id"] == note["id"]
    assert engine.latest()["text"] == dream["text"]
