# Ombre Memory Core

A headless, local-first long-term memory service for AI agents.

It stores memories as Obsidian-compatible Markdown, exposes them through MCP,
and combines semantic retrieval with emotion, recency, importance, unresolved
state, optional decay, and an optional drive/weather layer.

> This repository is a clean public extraction of a larger private companion
> system. The private dashboard, animated opening sequence, household artwork,
> personal memory data, credentials, and local app integrations are deliberately
> not included.

## What is included

- `hold` — store a memory, feeling, writing fragment, unresolved thread, or window
- `breath` — surface a compact context bundle for a new/compacted agent session
- `wander` / `trace` — browse memories and inspect related trails
- Markdown + YAML frontmatter storage (works with or without Obsidian)
- configurable OpenAI-compatible compression and embedding providers
- hybrid retrieval: topic, emotional resonance, recency, and importance
- optional forgetting/archival engine
- optional drive, weather, residue, rhythm, and multi-agent room modules
- stdio and Streamable HTTP transports

## What is not included

- any web dashboard or opening animation
- private visual design and household assets
- real memory buckets or conversation archives
- API keys, passwords, push tokens, local paths, or signing material
- the private Nocturne app and its device-specific hooks

The service root intentionally returns a small JSON descriptor instead of a UI.

## Quick start (Python)

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
python server.py
```

The default config uses stdio. For HTTP:

```bash
OMBRE_TRANSPORT=streamable-http python server.py
```

Then verify:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/
```

## Quick start (Docker)

```bash
cp .env.example .env
# edit .env and set an API key if you want LLM compression/embeddings
docker compose up --build -d
curl http://localhost:8000/health
```

Memory data is written to `./buckets` by default and is ignored by Git.

## MCP configuration

### Streamable HTTP

```json
{
  "mcpServers": {
    "ombre-memory": {
      "type": "streamable-http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Local stdio

```json
{
  "mcpServers": {
    "ombre-memory": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "OMBRE_BUCKETS_DIR": "/absolute/path/to/private-memory-data"
      }
    }
  }
}
```

## Identity is configuration, not source code

The public core ships with neutral labels. Set these only in your local `.env`:

```bash
OMBRE_AGENT_NAME=Agent
OMBRE_HUMAN_NAME=Human
OMBRE_AGENT_PERSONA="A short first-person identity instruction"
```

Do not commit a real persona prompt if it contains private relationship history.

## Models

Compression and embeddings use OpenAI-compatible endpoints. The core supports
hosted providers as well as Ollama, LM Studio, or vLLM. See
[`config.example.yaml`](config.example.yaml) and [`ENV_VARS.md`](ENV_VARS.md).

Without a configured model, basic Markdown storage and non-model operations can
still be used; features that explicitly require model inference will return an
error instead of silently fabricating output.

## Public boundary and provenance

See [`PUBLIC_BOUNDARY.md`](PUBLIC_BOUNDARY.md) before publishing a derivative.
The original Ombre Brain foundation is MIT-licensed; its copyright notice is
retained in [`LICENSE`](LICENSE). This extraction adds a headless public boundary
around later companion-oriented work without relicensing the upstream code.

## Tests

```bash
python -m pytest -q
```

## Security

- Keep `buckets/`, `.env`, `config.yaml`, database files, and exports private.
- Bind HTTP to localhost unless you add authentication and TLS at the edge.
- Set `OMBRE_API_PASSWORD` before exposing protected `/api/*` routes.
- Treat memory files as sensitive personal data, not ordinary application logs.
- Run a secret scan before every public release.

## License

MIT. See [`LICENSE`](LICENSE).
