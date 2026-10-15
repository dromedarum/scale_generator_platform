from __future__ import annotations 

from dataclasses import dataclass, field
from typing import Any

@dataclass
class LaminaSystem:
    """"
    Scientific representation of the basal lamina system.

    Material-layer thicknesses and air-gap thicknesses store the realized
    morphology after any seeded variability is applied.
    """

    material_layer_thickness_um: list[float] = field(default_factory=list)

    air_gap_thickness_um: list[float] = field(default_factory=list)

    layer_bottom_z_um: list[float] = field(default_factory=list)

    layer_top_z_um: list[float] = field(default_factory=list)

    separation_from_scaffold_um: float = 0.0

    layer_meshes: list[Any] = field(default_factory=list)

    combined_mesh: Any | None = None

    @property
    def solid_thickness_um(self) -> float:
        return float(sum(self.material_layer_thickness_um))

    @property
    def total_air_gap_um(self) -> float:
        return float(sum(self.air_gap_thickness_um))

    @property
    def total_stack_height(self) -> float:
        return float(self.solid_thickness_um + self.total_air_gap_um)

    @property
    def number_of_material_layers(self) -> int:
        return len(self.material_layer_thickness_um)
