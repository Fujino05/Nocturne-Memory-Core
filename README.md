# Nocturne Memory Core

A headless, local-first long-term memory service for AI agents. It stores
source-preserving memories as Obsidian-compatible Markdown and exposes a small
MCP surface for recall, browsing, lifecycle changes, and optional fermentation.

This is a clean public extraction. It contains no companion persona, private
prose, dashboard, room, desire/weather system, speech pipeline, telemetry, or
personal memory data.

## Included layers

### Memory core
- `hold` — store memory, feeling, writing, unresolved, window, or permanent material
- `breath` — recall relevant/vivid records as a compact context bundle
- `wander` — browse recent, random, unresolved, archived, or all records
- `trace` — build a literal, chronological, source-preserving timeline
- `memory` — resolve, pin, archive, or explicitly delete one record
- `memory_stats` — inspect local storage counts
- Markdown + YAML frontmatter, hybrid fuzzy/semantic retrieval, optional decay

### Optional fermentation
- `thought` — an independent SQLite pool of small sourced thoughts
- `latent` — an independent JSON lifecycle: draft → approved → used/deleted
- `dream` — a synthesis fed **only** by memories, approved latent notes, and thoughts

Dream output always includes its source IDs. With no model configured it creates
an explicitly labelled deterministic collage rather than pretending an LLM ran.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
python server.py
```

The default transport is stdio. For HTTP:

```bash
OMBRE_TRANSPORT=streamable-http python server.py
curl http://localhost:8000/health
```

MCP configuration:

```json
{
  "mcpServers": {
    "nocturne-memory": {
      "command": "/absolute/path/.venv/bin/python",
      "args": ["/absolute/path/Nocturne-Memory-Core/server.py"],
      "env": {"OMBRE_BUCKETS_DIR": "/absolute/path/private-memory-data"}
    }
  }
}
```

Or connect to `http://localhost:8000/mcp` when using Streamable HTTP.

## Models are optional

Plain storage, browsing, lifecycle operations, thought/latent pools, and collage
dreams work offline. An OpenAI-compatible chat endpoint enables automatic
metadata analysis, model-assisted merging, and generated dream prose. An
embedding endpoint can independently enable semantic pre-filtering.

See [`config.example.yaml`](config.example.yaml) and [`ENV_VARS.md`](ENV_VARS.md).

## Security

This server intentionally has no built-in account system. Keep it on stdio or
localhost, or place authentication and TLS in a trusted reverse proxy. Never
commit `buckets/`, `.env`, `config.yaml`, exports, or model keys.

Run before publication:

```bash
python -m pytest -q
python scripts/public_audit.py
```

See [`PUBLIC_BOUNDARY.md`](PUBLIC_BOUNDARY.md) and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the extraction boundary.

## License

MIT. See [`LICENSE`](LICENSE).
