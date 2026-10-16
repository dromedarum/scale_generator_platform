from __future__ import annotations

from dataclasses import dataclass
from .enums import ImportTransformMode

@dataclass
class AssemblyImportConfig:
    transform_mode: ImportTransformMode = (
        ImportTransformMode.PRESERVE
    )

    center_xy: bool = False
    place_bottom_at_z_zero: bool = False