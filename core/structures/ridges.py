from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from .enums import RidgeRootMode

@dataclass
class RidgeSystem:
    """
    Scientific description of scale ridges.
    """

    centerlines: Any | None = None

    local_spacings_um: Any | None = None 
    openings_between_ridges: Any | None = None

    mean_spacing_um: float | None = None
    spacing_std_um: float | None = None

    width_um: float | None = None
    height_um: float | None = None

    root_mode: RidgeRootMode | None = None
    embed_depth_um: float | None = None
    root_width_um: float | None = None


