from __future__ import annotations

from typing import Dict, Type
from adapters.base import SUTAdapter

_REGISTRY: Dict[str, Type[SUTAdapter]] = {}


def register(adapter_type: str):
    """Decorator to register adapters by type name (e.g., 'redmine')."""
    def _decorator(cls: Type[SUTAdapter]) -> Type[SUTAdapter]:
        _REGISTRY[adapter_type] = cls
        return cls
    return _decorator


def get_adapter(adapter_type: str) -> Type[SUTAdapter]:
    if adapter_type not in _REGISTRY:
        raise ValueError(
            f"Unknown adapter type: {adapter_type}. "
            f"Available: {sorted(_REGISTRY.keys())}"
        )
    return _REGISTRY[adapter_type]
