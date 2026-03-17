from __future__ import annotations

from ariv.scripts import probe_hw


class _VM:
    def __init__(self, total: int, available: int) -> None:
        self.total = total
        self.available = available


class _PSUtilStub:
    @staticmethod
    def virtual_memory() -> _VM:
        return _VM(total=16 * 1024 * 1024 * 1024, available=9 * 1024 * 1024 * 1024)

    @staticmethod
    def cpu_count(logical: bool = True) -> int:
        return 16 if logical else 8


def test_probe_hardware_gpu(monkeypatch):
    monkeypatch.setattr(probe_hw, "_load_psutil", lambda: _PSUtilStub)
    monkeypatch.setattr(probe_hw, "_probe_nvidia", lambda: ("RTX-3060", 6144))

    profile = probe_hw.probe_hardware_profile()

    assert profile.gpu is True
    assert profile.vram_mb == 6144
    assert profile.device_name == "RTX-3060"
    assert profile.supports_full_pipeline is True
    assert "sarvam-2b-q4_k_m" in profile.suggested_models
    assert "deepseek-r1-distill-qwen-7b" in profile.suggested_models


def test_probe_hardware_cpu_fallback(monkeypatch):
    monkeypatch.setattr(probe_hw, "_load_psutil", lambda: None)
    monkeypatch.setattr(probe_hw, "_probe_nvidia", lambda: None)
    monkeypatch.setenv("ARIV_FAKE_VRAM_MB", "0")

    data = probe_hw.probe_hardware()

    assert data["gpu"] is False
    assert data["vram_mb"] == 0
    assert data["device_name"] == "cpu"
    assert "llama-3.2-1b-q4_k_m" in data["suggested_models"]
    assert "smollm2-1.7b" in data["suggested_models"]


def test_probe_nvidia_parse_failure(monkeypatch):
    class _FakeResult:
        stdout = "garbled-output"

    def _fake_run(*args, **kwargs):
        return _FakeResult()

    monkeypatch.setattr(probe_hw.subprocess, "run", _fake_run)
    assert probe_hw._probe_nvidia() is None


def test_probe_hardware_invalid_fake_vram(monkeypatch):
    monkeypatch.setattr(probe_hw, "_probe_nvidia", lambda: None)
    monkeypatch.setenv("ARIV_FAKE_VRAM_MB", "not-an-int")

    profile = probe_hw.probe_hardware_profile()
    assert profile.vram_mb == 0
