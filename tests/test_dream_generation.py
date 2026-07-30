import json

import pytest

import server


def _dream_text(length):
    seed = "我推开会呼吸的门，桃香沿着楼梯往上走，黑猫踩住一片发热的月光。"
    return (seed * ((length // len(seed)) + 1))[:length]


class _FakeResponse:
    def __init__(self, content):
        self.content = content

    def json(self):
        return {"choices": [{"message": {"content": self.content}}]}


class _FakeClient:
    responses = []
    payloads = []

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, *, headers, json):
        type(self).payloads.append(json)
        index = min(len(type(self).payloads) - 1, len(type(self).responses) - 1)
        return _FakeResponse(type(self).responses[index])


@pytest.fixture
def dream_setup(monkeypatch, tmp_path):
    bucket = {
        "id": "memory-1",
        "content": "Human把一只脆桃递过来，果肉边缘是浅粉到乳白的渐变。",
        "metadata": {
            "created": "2026-07-27T09:00:00",
            "name": "脆桃",
            "type": "dynamic",
        },
    }

    async def list_all(**kwargs):
        return [bucket]

    _FakeClient.responses = []
    _FakeClient.payloads = []
    monkeypatch.setattr(server.bucket_mgr, "list_all", list_all)
    monkeypatch.setattr(server, "_dream_atmosphere_line", lambda: "Banked Heat")
    monkeypatch.setattr(server, "BUCKETS_DIR", str(tmp_path))
    monkeypatch.setattr(server.httpx, "AsyncClient", _FakeClient)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    return tmp_path


@pytest.mark.asyncio
async def test_dream_first_full_paragraph_is_cached_without_retry(dream_setup):
    compliant = _dream_text(140)
    assert 120 <= len(compliant) <= 180
    _FakeClient.responses = [compliant]

    dream, _, recent, _ = await server._refresh_dream_cache()

    assert len(_FakeClient.payloads) == 1
    prompt = _FakeClient.payloads[0]["messages"][0]["content"]
    assert "约120-180个中文字符" in prompt
    assert "不要少于120个中文字符" in prompt
    assert _FakeClient.payloads[0]["max_tokens"] == 300
    assert _FakeClient.payloads[0]["thinking"] == {"type": "disabled"}
    assert dream == compliant
    assert [item["id"] for item in recent] == ["memory-1"]
    cached = json.loads((dream_setup / "latest_dream.json").read_text())
    assert cached["dream"] == compliant


@pytest.mark.asyncio
async def test_dream_120_character_first_answer_does_not_retry(dream_setup):
    boundary = _dream_text(120)
    assert len(boundary) == 120
    _FakeClient.responses = [boundary]

    dream, _, _, _ = await server._refresh_dream_cache()

    assert len(_FakeClient.payloads) == 1
    assert dream == boundary


@pytest.mark.asyncio
async def test_dream_119_character_first_answer_retries(dream_setup):
    below_boundary = _dream_text(119)
    rewritten = _dream_text(130)
    assert len(below_boundary) == 119
    assert 120 <= len(rewritten) <= 180
    _FakeClient.responses = [below_boundary, rewritten]

    dream, _, _, _ = await server._refresh_dream_cache()

    assert len(_FakeClient.payloads) == 2
    assert dream == rewritten


@pytest.mark.asyncio
async def test_dream_short_first_answer_is_rewritten_once_and_cached(dream_setup):
    short = _dream_text(64)
    rewritten = _dream_text(150)
    assert len(short) == 64
    assert 120 <= len(rewritten) <= 180
    _FakeClient.responses = [short, rewritten]

    dream, _, _, _ = await server._refresh_dream_cache()

    assert len(_FakeClient.payloads) == 2
    retry_messages = _FakeClient.payloads[1]["messages"]
    assert retry_messages[1] == {"role": "assistant", "content": short}
    assert "上一版过短" in retry_messages[2]["content"]
    assert dream == rewritten
    cached = json.loads((dream_setup / "latest_dream.json").read_text())
    assert cached["dream"] == rewritten


@pytest.mark.asyncio
async def test_dream_never_requests_more_than_two_answers(dream_setup):
    first = _dream_text(64)
    second = _dream_text(80)
    _FakeClient.responses = [first, second, _dream_text(140)]

    dream, _, _, _ = await server._refresh_dream_cache()

    assert len(_FakeClient.payloads) == 2
    assert dream == second
    cached = json.loads((dream_setup / "latest_dream.json").read_text())
    assert cached["dream"] == second
