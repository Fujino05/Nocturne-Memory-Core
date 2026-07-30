import pytest
import ast
from pathlib import Path

import desire_engine
import server as server_mod


def test_hold_tool_signature_stays_lean():
    tree = ast.parse(Path("server.py").read_text(encoding="utf-8"))
    hold_node = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "hold"
    )
    arg_names = [arg.arg for arg in hold_node.args.args]

    assert "chord" in arg_names
    assert "drive" in arg_names
    assert "drives" in arg_names
    assert "valence" not in arg_names
    assert "arousal" not in arg_names
    assert "feel" not in arg_names
    assert "source_bucket" not in arg_names
    assert "pinned" not in arg_names
    assert "domain" not in arg_names
    assert "created_at" not in arg_names
    assert "drive_level" not in arg_names


def test_hold_kind_help_exposes_unresolved_not_private():
    tree = ast.parse(Path("server.py").read_text(encoding="utf-8"))
    hold_node = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "hold"
    )
    doc = ast.get_docstring(hold_node) or ""

    assert "unresolved" in doc
    assert "private" not in doc
    assert "九维" in doc or "attachment" in doc
    assert "C6" in doc


def test_parse_hold_drive_tags_primary_wins_and_dedupes_secondary():
    mid = server_mod.SIGNAL_LEVEL_VALUES["mid"]
    tags = server_mod._parse_hold_drive_tags(
        "attachment",
        ["attachment", "libido", "libido", "curiosity"],
    )
    assert list(tags.keys())[0] == "attachment"
    assert tags == {
        "attachment": mid,
        "libido": mid,
        "curiosity": mid,
    }


def test_parse_hold_drive_tags_accepts_legacy_secondary_string():
    mid = server_mod.SIGNAL_LEVEL_VALUES["mid"]
    tags = server_mod._parse_hold_drive_tags("possessiveness", "possessiveness,stewardship")
    assert tags == {
        "possessiveness": mid,
        "stewardship": mid,
    }


def test_normalize_hold_chord_rejects_atmosphere_labels():
    assert server_mod._normalize_tool_chord("C6") == "C6"
    assert server_mod._normalize_hold_chord("c6") == "C6"
    assert server_mod._normalize_hold_chord("Drift→Clutch") == ""
    assert server_mod._normalize_hold_chord("阴湿") == ""
    assert server_mod._normalize_hold_chord(None) == ""


def test_chord_keys_cover_weather_regions():
    assert set(desire_engine.CHORD_KEYS) == (
        desire_engine.WEATHER_WARM_CHORDS
        | desire_engine.WEATHER_SHADOW_CHORDS
        | desire_engine.WEATHER_LIMINAL_CHORDS
    )


def test_stir_thought_chord_shares_hold_gate(tmp_path, monkeypatch):
    """stir/settle thought 的 chord 与 hold 同一道闸：合法进 echo，氛围词不进。"""
    pytest.importorskip("mcp.server.fastmcp")
    engine = desire_engine.DesireEngine(db_path=str(tmp_path / "desire-stir-chord.db"))
    monkeypatch.setattr(server_mod, "_desire", engine)

    bad = server_mod.stir(
        "curiosity",
        thought="质检飞鼠炸毛",
        chord="Drift→Clutch",  # type: ignore[arg-type]
    )
    assert bad.get("chord_echo") is not True
    assert bad.get("thought_pooled") is True

    good = server_mod.stir(
        "attachment",
        thought="转头那一下",
        chord="C6",
    )
    assert good.get("chord_echo") is True
    assert good.get("thought_pooled") is True

    via_drive = server_mod.drive(
        action="stir",
        drive_key="possessiveness",
        thought="领地被碰了一下",
        chord="Am7",
    )
    assert via_drive.get("chord_echo") is True
    assert via_drive.get("thought_pooled") is True


def test_breath_tool_signature_stays_zero_arg():
    tree = ast.parse(Path("server.py").read_text(encoding="utf-8"))
    breath_node = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "breath"
    )

    assert [arg.arg for arg in breath_node.args.args] == []


@pytest.mark.asyncio
async def test_bucket_create_persists_drive_tags(bucket_mgr):
    bucket_id = await bucket_mgr.create(
        content="一条带Drive纹理的记忆",
        tags=[],
        importance=6,
        domain=["memory"],
        drive_tags={"possessiveness": 0.86, "stewardship": 0.62},
    )

    bucket = await bucket_mgr.get(bucket_id)

    assert bucket["metadata"]["drive_tags"] == {
        "possessiveness": 0.86,
        "stewardship": 0.62,
    }
