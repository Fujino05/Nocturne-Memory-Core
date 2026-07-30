# Environment variables

## Core

| Variable | Purpose | Default |
|---|---|---|
| `OMBRE_TRANSPORT` | `stdio` or `streamable-http` | config file / `stdio` |
| `OMBRE_PORT` | HTTP port | `8000` |
| `OMBRE_BUCKETS_DIR` | private Markdown/data directory | `./buckets` |
| `OMBRE_API_KEY` | OpenAI-compatible model key | empty |
| `OMBRE_BASE_URL` | OpenAI-compatible base URL | config file |
| `OMBRE_MODEL` | compression model | config file |
| `OMBRE_API_PASSWORD` | protects administrative `/api/*` routes | empty |

`OMBRE_DASHBOARD_PASSWORD` is accepted only as a compatibility alias. There is
no dashboard in the public core.

## Identity

| Variable | Purpose | Default |
|---|---|---|
| `OMBRE_AGENT_NAME` | agent display label used in generated prompts | `Agent` |
| `OMBRE_HUMAN_NAME` | human display label used in generated prompts | `Human` |
| `OMBRE_AGENT_PERSONA` | short first-person persona instruction | neutral built-in text |

## Optional integrations

| Variable | Purpose |
|---|---|
| `OMBRE_HOOK_URL` | fire-and-forget event webhook |
| `OMBRE_HOOK_SKIP` | disable the webhook |
| `OMBRE_RHYTHM_TOKEN` | token for rhythm HTTP writes |
| `BARK_KEY` | optional Bark device key |
| `BARK_ICON_URL` | optional public Bark icon URL |
| `OMBRE_APP_SCHEME` | allowed deep-link scheme for optional pushes |
| `OMBRE_NOW_PLAYING_COMMAND` | optional local executable for now-playing data |
| `OMBRE_SPEAK_URL` | optional external speech endpoint |
| `OMBRE_SPEAK_TOKEN` | token for the optional speech endpoint |

Keep all values in an untracked `.env` or your secret manager.
