from __future__ import annotations

from .parameters import StructureParameters
from .network import HyperuniformNetwork
from .ridges import RidgeSystem
from .laminae import LaminaSystem
from .components import GeometryComponent
from .enums import GeometryOrigin

from dataclasses import dataclass, field

from typing import Any

@dataclass
class ButterflyStructure:
    """
    Scientific representation of a butterfly wing sclae morphology.
    Geometry may be attached later by builders.
    """

    parameters: StructureParameters | None = None

    origin: GeometryOrigin = GeometryOrigin.GENERATED
    source_path: str | None = None

    network: HyperuniformNetwork | None = None
    network_footprint: Any | None = None
    network_mesh: Any | None = None
    ridges: RidgeSystem | None = None 
    ridge_footprint: Any | None = None
    ridge_mesh: Any | None = None
    laminae: LaminaSystem | None = None
    lamina_mesh: Any | None = None
    scaffold_mesh: Any | None = None

    components: list[GeometryComponent] = field(default_factory=list)
    


    
