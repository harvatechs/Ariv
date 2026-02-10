from pathlib import Path

from ariv.models import ModelRegistry
from ariv.orchestrator import HardwareProfile, ModelManager, Router


def test_router_selects_indic_model() -> None:
    registry = ModelRegistry.from_yaml(Path("ariv/models/models.yaml"))
    router = Router(registry)
    hardware = HardwareProfile(gpu=True, vram_mb=4096, cpu_mem_mb=16384, device_name="gpu")
    decision = router.choose_model(
        hardware=hardware,
        preferred_lang="hi",
        task_hint=None,
        text="नमस्ते",
    )
    assert decision.model.name.startswith("sarvam")


def test_router_selects_code_model() -> None:
    registry = ModelRegistry.from_yaml(Path("ariv/models/models.yaml"))
    router = Router(registry)
    hardware = HardwareProfile(gpu=True, vram_mb=4096, cpu_mem_mb=16384, device_name="gpu")
    decision = router.choose_model(
        hardware=hardware,
        preferred_lang=None,
        task_hint="code",
        text="def add(a, b):",
    )
    assert decision.model.name.startswith("qwen")


def test_model_manager_lru() -> None:
    manager = ModelManager(max_loaded=1)
    manager.touch("a")
    evicted = manager.touch("b")
    assert evicted == ["a"]
