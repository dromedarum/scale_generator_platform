from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .import_config import GeometryImportConfig

@dataclass
class GeometryImportSpec:
    path: str | Path
    config: GeometryImportConfig
    