"""Model registry helpers for ARIV."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml


@dataclass(frozen=True)
class ModelSpec:
    name: str
    type: str
    family: str
    quant: str
    vram_mb: int
    task: str
    url: str
    license: str
    sha256: Optional[str]
    preferred_langs: List[str]
    fallback: List[str]
    local_path: Optional[str]


class ModelRegistry:
    """Load and query model specs from YAML."""

    def __init__(self, models: Dict[str, ModelSpec]) -> None:
        self._models = models

    @classmethod
    def from_yaml(cls, path: Path) -> "ModelRegistry":
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        models_data = data.get("models", {})
        models: Dict[str, ModelSpec] = {}
        for name, entry in models_data.items():
            models[name] = ModelSpec(
                name=name,
                type=str(entry.get("type", "gguf")),
                family=str(entry.get("family", "")),
                quant=str(entry.get("quant", "")),
                vram_mb=int(entry.get("vram_mb", 0)),
                task=str(entry.get("task", "general")),
                url=str(entry.get("url", "")),
                license=str(entry.get("license", "")),
                sha256=entry.get("sha256"),
                preferred_langs=list(entry.get("preferred_langs", [])),
                fallback=list(entry.get("fallback", [])),
                local_path=entry.get("local_path"),
            )
        return cls(models)

    def list_models(self) -> Iterable[ModelSpec]:
        return self._models.values()

    def get(self, name: str) -> ModelSpec:
        return self._models[name]

    def has(self, name: str) -> bool:
        return name in self._models

    def available_local(self) -> List[ModelSpec]:
        available: List[ModelSpec] = []
        for model in self._models.values():
            if model.local_path and Path(model.local_path).exists():
                available.append(model)
        return available
