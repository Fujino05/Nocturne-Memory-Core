from pathlib import Path


def test_private_runtime_modules_are_absent():
    root = Path(__file__).parents[1]
    names = {p.name for p in root.glob("*.py")}
    forbidden = {"desire_engine.py", "speech_event_engine.py", "catroom_store.py",
                 "room_store.py", "rhythm_store.py", "dialogue_residue_engine.py",
                 "memory_residue_engine.py", "mood_pool.py"}
    assert not (names & forbidden)


def test_server_has_headless_tools_only():
    text = (Path(__file__).parents[1] / "server.py").read_text("utf-8")
    for name in ["hold", "breath", "wander", "trace", "thought", "latent", "dream"]:
        assert f"def {name}(" in text
    for private in ["CHORD_GRAVITY_POOLS", "DesireEngine", "CatroomStore", "speech_event_engine"]:
        assert private not in text


def test_server_registers_only_public_tools(tmp_path):
    import os
    import subprocess
    import sys
    root = Path(__file__).parents[1]
    env = dict(os.environ, OMBRE_BUCKETS_DIR=str(tmp_path))
    code = "import server; print(','.join(sorted(server.mcp._tool_manager._tools)))"
    result = subprocess.run([sys.executable, "-c", code], cwd=root, env=env,
                            text=True, capture_output=True, check=True)
    assert result.stdout.strip() == "breath,dream,hold,latent,memory,memory_stats,thought,trace,wander"
