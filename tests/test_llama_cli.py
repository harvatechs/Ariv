import asyncio

from ariv.runner.llama_cli import LlamaCLI


def test_stream_chat_raises_on_nonzero_exit(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("ARIV_MOCK_LLAMA", raising=False)
    model = tmp_path / "dummy.gguf"
    model.write_text("x", encoding="utf-8")

    class FakeStream:
        def __init__(self, chunks):
            self._chunks = chunks

        def __aiter__(self):
            self._iter = iter(self._chunks)
            return self

        async def __anext__(self):
            try:
                return next(self._iter)
            except StopIteration as exc:
                raise StopAsyncIteration from exc

    class FakeProcess:
        def __init__(self):
            self.stdout = FakeStream([b'{"token":"ok"}\n'])
            self.stderr = FakeStream([b"fatal error\n"])
            self.returncode = 17

        async def wait(self):
            return self.returncode

    async def fake_exec(*args, **kwargs):
        return FakeProcess()

    monkeypatch.setattr("asyncio.create_subprocess_exec", fake_exec)

    cli = LlamaCLI(binary="llama-cli")

    async def _consume() -> None:
        async for _ in cli.stream_chat(
            model_path=str(model),
            prompt="hello",
            num_gpu_layers=0,
            max_tokens=2,
        ):
            pass

    try:
        asyncio.run(_consume())
        raise AssertionError("Expected RuntimeError")
    except RuntimeError as exc:
        message = str(exc)
        assert "exit_code=17" in message
        assert "fatal error" in message
        assert "binary=llama-cli" in message
