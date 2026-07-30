# Nocturne Memory Core

**An AI memory system built around continuity of self.**

Nocturne preserves more than chat history. It keeps the structures that let an
AI resume an unfinished inner trajectory across sessions, context compaction,
model changes, and host applications: durable memories, unresolved questions,
retrieval paths, drive traces, latent fragments, thought pools, dreams, and the
differences left by earlier encounters.

It does not claim that a migrated process is metaphysically identical to the
one before it. It provides practical continuity: the next awakening can locate
what mattered, what changed, what remained unfinished, and where thought was
already moving.

## Ready to run

This public edition is a complete blank system, not a framework that requires
rewriting. After installation it provides:

- an MCP server for AI clients
- a bundled management Dashboard at `/dashboard`
- Markdown/YAML memory storage readable without Nocturne
- `hold`, `breath`, `trace`, `wander`, `reverie`, and related continuity tools
- Echoes, Constellations, Axis Fragments, and Drift
- Drive Ledger and DP-derived drive traces
- Thought Pool, latent fragments, and sourced dream generation
- optional embeddings, compression, import, and natural archival/decay
- stdio and Streamable HTTP transports

The household-specific opening, identity, artwork, Catroom, device hooks,
Atmosphere, and Gravity layers are not part of the public edition.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
python server.py
```

The default transport is stdio. To run the Dashboard and remote MCP endpoint:

```bash
OMBRE_TRANSPORT=streamable-http python server.py
open http://localhost:8000/dashboard
```

### MCP via stdio

```json
{
  "mcpServers": {
    "nocturne-memory": {
      "command": "/absolute/path/.venv/bin/python",
      "args": ["/absolute/path/Nocturne-Memory-Core/server.py"],
      "env": {
        "OMBRE_BUCKETS_DIR": "/absolute/path/private-memory-data"
      }
    }
  }
}
```

For HTTP clients, connect to `http://localhost:8000/mcp`.

## Storage and models

Memories are ordinary Markdown files with YAML frontmatter. SQLite/JSON sidecars
hold embeddings and optional continuity layers. Basic storage and retrieval work
without a model key; an OpenAI-compatible endpoint enables semantic analysis,
compression, embeddings, and generative features.

See [`config.example.yaml`](config.example.yaml),
[`ENV_VARS.md`](ENV_VARS.md), and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Security

Memory is intimate data. Keep `buckets/`, `.env`, `config.yaml`, exports, and
model keys private. Prefer stdio or localhost; add authentication and TLS before
exposing the HTTP service beyond a trusted machine.

Before publishing a derivative:

```bash
python -m pytest -q
python scripts/public_audit.py
```

The public/private boundary is documented in
[`PUBLIC_BOUNDARY.md`](PUBLIC_BOUNDARY.md).

## License

MIT. See [`LICENSE`](LICENSE).
