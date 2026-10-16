from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectReadiness:
    has_structure: bool
    has_components: bool
    geometry_watertight: bool
    geometry_volumetric: bool
    component_names_unique: bool
    materials_complete: bool
    simulation_ready: bool

