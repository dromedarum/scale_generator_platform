from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import trimesh

from .enums import ComponentRole

@dataclass
class GeometryComponent:
    """
    One physical solid component in a butterfly structure.
    Components are the canonical interface used by downstream material,
    pigment, and simulation systems.
    """
    name: str
    mesh: trimesh.Trimesh
    role: ComponentRole

    material_id: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Component name cannot be empty.")

        if not isinstance(self.mesh,trimesh.Trimesh):
            raise TypeError(f"Component mesh must be a trimesh.Trimesh, got {type(self.mesh).__name__}.")

        if not isinstance(self.role,ComponentRole,):
            raise TypeError("Component role must be a ComponentRole, "f"got {type(self.role).__name__}.")