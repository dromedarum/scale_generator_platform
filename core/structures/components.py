from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class GeometryComponent:
    """
    One physical solid component in a butterfly structure.
    Components are the canonical interface used by downstream material,
    pigment, and simulation systems.
    """
    name: str
    mesh: Any
    role: str

    material_id: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    