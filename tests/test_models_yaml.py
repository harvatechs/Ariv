from pathlib import Path

from ariv.models import ModelRegistry


def test_models_yaml_parsing() -> None:
    registry = ModelRegistry.from_yaml(Path("ariv/models/models.yaml"))
    sarvam = registry.get("sarvam-2b-q4_k_m")
    assert sarvam.quant == "Q4_K_M"
    assert sarvam.vram_mb > 0


def test_models_available_local() -> None:
    registry = ModelRegistry.from_yaml(Path("ariv/models/models.yaml"))
    available = registry.available_local()
    names = {model.name for model in available}
    assert "mock-0.1b-q4_0" in names
