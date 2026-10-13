from __future__ import annotations

from .parameters import StructureParameters
from .network import HyperuniformNetwork
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
    ridge_mesh: Any | None = None
    mulitlayer_mesh: Any | None = None
    


    
