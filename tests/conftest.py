"""Pytest configuration for loading integration modules without Home Assistant."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT_ROOT = ROOT / "custom_components" / "sony_adcp"


def _ensure_package(name: str, path: Path) -> types.ModuleType:
    if name in sys.modules:
        return sys.modules[name]
    module = types.ModuleType(name)
    module.__path__ = [str(path)]  # type: ignore[attr-defined]
    sys.modules[name] = module
    return module


def _load_module(qualified_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(
        qualified_name, COMPONENT_ROOT / filename
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {qualified_name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[qualified_name] = module
    spec.loader.exec_module(module)
    return module


_ensure_package("custom_components", ROOT / "custom_components")
_ensure_package("custom_components.sony_adcp", COMPONENT_ROOT)
_load_module("custom_components.sony_adcp.const", "const.py")
_load_module("custom_components.sony_adcp.adcp_client", "adcp_client.py")
