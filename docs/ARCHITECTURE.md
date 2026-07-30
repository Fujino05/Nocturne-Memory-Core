# Architecture

```text
MCP tools
  ├─ memory core ── BucketManager ── Markdown/YAML buckets
  │                    ├─ optional EmbeddingEngine ── embeddings.db
  │                    └─ optional DecayEngine ── archive/
  └─ fermentation
       ├─ ThoughtPool ── thoughts.db
       ├─ LatentPool ── latent_notes.json
       └─ DreamEngine ── latest_dream.json
             reads: memory + approved latent + thought
```

## Invariants

1. Stored memories remain readable without this service.
2. Every generated dream carries the exact source records used.
3. Thought and latent pools do not depend on emotion drives or persona state.
4. Latent transitions are explicit; drafts cannot enter dreams until approved.
5. No model is required for baseline operation.
6. Deletion, archival, pinning, and resolution are explicit MCP actions.
7. The public server has no presentation layer, device hooks, or hidden heartbeat.

## Retrieval

`BucketManager.search` combines fuzzy topic relevance, optional embedding
pre-filtering, emotion coordinates when supplied, time proximity, and declared
importance. `trace` is deliberately simpler: it performs literal matching over
content and metadata, includes archives, then sorts chronologically.

## Fermentation versus memory

Thoughts and latent notes are not silently promoted to durable memories. Dreams
are derived artifacts, not evidence. Consumers should show the `mode` and source
IDs if dream text is presented to a person or fed back to another model.
