from __future__ import annotations

from dataclasses import dataclass
from .enums import LengthUnit

@dataclass
class GeometryImportConfig:
    """
    Configuration for importing a mesh into the canonical structure model.
    Imported mesh coordinates are converted to micrometers internally..
    """
    source_unit: LengthUnit = LengthUnit.MICROMETER
    component_name: str = "imported_component"
    component_role: str = "imported"

    process_mesh: bool = True
    require_watertight: bool = True
    require_volume: bool = True

    center_xy: bool = False
    place_bottom_at_z_zero: bool = False 