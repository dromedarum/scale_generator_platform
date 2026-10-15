from __future__ import annotations

from .parameters import StructureParameters
from .network import HyperuniformNetwork
from .ridges import RidgeSystem
from .laminae import LaminaSystem
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ButterflyStructure:
    """
    Scientific representation of a butterfly wing sclae morphology.
    Geometry may be attached later by builders.
    """

    parameters: StructureParameters

    network: HyperuniformNetwork | None = None
    network_footprint: Any | None = None
    network_mesh: Any | None = None
    ridges: RidgeSystem | None = None 
    ridge_footprint: Any | None = None
    ridge_mesh: Any | None = None
    laminae: LaminaSystem | None = None
    lamina_mesh: Any | None = None
    scaffold_mesh: Any | None = None
    


    
