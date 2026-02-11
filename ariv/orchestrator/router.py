"""Routing and model selection for ARIV."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ariv.models import ModelRegistry, ModelSpec

INDIC_LANGS = {
    "hi",
    "ta",
    "te",
    "kn",
    "bn",
    "ml",
    "gu",
    "pa",
    "mr",
    "ur",
}

CODE_HINTS = {"code", "python", "java", "sql", "debug", "logic", "reasoning"}


@dataclass
class HardwareProfile:
    gpu: bool
    vram_mb: int
    cpu_mem_mb: int
    device_name: str


@dataclass
class RouteDecision:
    model: ModelSpec
    fallback: Optional[str]
    num_gpu_layers: int
    estimated_vram_mb: int
    reason: str


def _classify_task(task_hint: Optional[str], text: str) -> str:
    hint = (task_hint or "").lower()
    if any(token in hint for token in CODE_HINTS):
        return "code_logic"
    if any(token in text.lower() for token in ["def ", "class ", "```", "import "]):
        return "code_logic"
    return "indic"


def _detect_indic(preferred_lang: Optional[str], text: str) -> bool:
    if preferred_lang and preferred_lang.lower() in INDIC_LANGS:
        return True
    for char in text:
        if "\u0900" <= char <= "\u0dff":
            return True
    return False


def _estimate_gpu_layers(vram_mb: int, model_vram_mb: int) -> int:
    if vram_mb <= 0:
        return 0
    if vram_mb >= model_vram_mb:
        return 999
    ratio = max(vram_mb / max(model_vram_mb, 1), 0.05)
    return max(int(40 * ratio), 1)


class Router:
    """Deterministic router based on task + language + VRAM."""

    def __init__(self, registry: ModelRegistry) -> None:
        self._registry = registry

    def choose_model(
        self,
        hardware: HardwareProfile,
        preferred_lang: Optional[str],
        task_hint: Optional[str],
        text: str,
    ) -> RouteDecision:
        is_indic = _detect_indic(preferred_lang, text)
        task_type = _classify_task(task_hint, text)
        if task_type == "code_logic":
            primary = "qwen-2.5-3b-q4_k_m"
        elif is_indic:
            primary = "sarvam-2b-q4_k_m"
        else:
            primary = "llama-3.2-1b-q4_k_m"

        selected = self._registry.get(primary)
        fallback = None
        if hardware.vram_mb and selected.vram_mb > hardware.vram_mb:
            for candidate in selected.fallback:
                if self._registry.has(candidate):
                    alt = self._registry.get(candidate)
                    if alt.vram_mb <= hardware.vram_mb:
                        fallback = selected.name
                        selected = alt
                        break
        if hardware.vram_mb < selected.vram_mb:
            fallback = fallback or selected.name
            if self._registry.has("llama-3.2-1b-q4_k_m"):
                selected = self._registry.get("llama-3.2-1b-q4_k_m")

        num_gpu_layers = _estimate_gpu_layers(hardware.vram_mb, selected.vram_mb)
        reason = f"task={task_type}, indic={is_indic}, vram={hardware.vram_mb}"
        return RouteDecision(
            model=selected,
            fallback=fallback,
            num_gpu_layers=num_gpu_layers,
            estimated_vram_mb=selected.vram_mb,
            reason=reason,
        )


class ModelManager:
    """Track loaded models with a simple LRU eviction policy."""

    def __init__(self, max_loaded: int = 2) -> None:
        self._max_loaded = max_loaded
        self._loaded: Dict[str, int] = {}
        self._counter = 0

    def touch(self, model_name: str) -> List[str]:
        self._counter += 1
        self._loaded[model_name] = self._counter
        evicted: List[str] = []
        while len(self._loaded) > self._max_loaded:
            lru_name = min(self._loaded, key=self._loaded.get)
            del self._loaded[lru_name]
            evicted.append(lru_name)
        return evicted

    def loaded(self) -> List[str]:
        return sorted(self._loaded.keys())
