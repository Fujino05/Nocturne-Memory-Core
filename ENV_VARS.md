# Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `OMBRE_TRANSPORT` | `stdio`, `streamable-http`, or `sse` | `stdio` |
| `OMBRE_BUCKETS_DIR` | Private data directory | `./buckets` |
| `OMBRE_API_KEY` | Optional OpenAI-compatible chat/embedding key | empty |
| `OMBRE_BASE_URL` | Optional common API base URL | config value |
| `OMBRE_DEHYDRATION_MODEL` | Chat model for analysis/merge/dream | config value |
| `OMBRE_DEHYDRATION_BASE_URL` | Chat API base URL | config value |
| `OMBRE_EMBEDDING_MODEL` | Embedding model | config value |
| `OMBRE_EMBEDDING_BASE_URL` | Embedding API base URL | chat base URL |
| `OMBRE_HOST` | HTTP bind host | `0.0.0.0` |
| `PORT` | HTTP port | `8000` |

Keep keys in the environment or an untracked `.env`, never `config.yaml` in a
public checkout.
