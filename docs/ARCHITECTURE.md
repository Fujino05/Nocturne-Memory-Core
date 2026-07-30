# Architecture

`server.py` is the MCP/HTTP composition root. It wires together:

- `bucket_manager.py`: Markdown bucket persistence, merge, and retrieval
- `dehydrator.py`: model-assisted compression and metadata extraction
- `embedding_engine.py`: optional semantic vectors
- `decay_engine.py`: optional forgetting/archive policy
- `desire_engine.py`: optional drive/weather state
- `dialogue_residue_engine.py` and `memory_residue_engine.py`: bounded analysis
- `rhythm_store.py`: optional external rhythm events and push bridge
- `catroom_store.py` and `room_store.py`: optional multi-agent notes

The private presentation layer is not part of this repository. Consumers should
build their own UI against MCP or the authenticated headless API.
