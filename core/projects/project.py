from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from core.structures import ButterflyStructure
from .json_types import JsonValue, validate_json_value
from .readiness import ProjectReadiness

@dataclass
class ButterflyProject:
    """"
    Top-level research project for one butterfly-structure study.
    The project owns the selected structure and will later contain materials, pigments, simulation configurations, and results.
    """
    
    name: str

    schema_version: str = "1.0"

    project_id: str = field(default_factory=lambda: str(uuid4()))

    structure: ButterflyStructure | None = None
    description: str = "" 

    metadata: dict[str, JsonValue] = field(default_factory=dict)

    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    
    

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """
        Validate the basic project metadata
        """
        if not isinstance(self.name, str):
            raise TypeError("Project name must be a string.")
        if not self.name.strip():
            raise ValueError("Project name cannot be empty.")
        if not isinstance(self.description, str):
            raise TypeError("Project description must be a string.")
        if not isinstance(self.metadata, dict):
            raise TypeError("Project metadata must be a dictionary.")
        if not isinstance(self.schema_version, str):
            raise TypeError("schema_version must be astring.")
        if not self.schema_version.strip():
            raise ValueError("schema_version cannot be empty.")
        validate_json_value(self.metadata, path="project.metadata")

    def touch(self) -> None:
        """
        Update the project modification timestamp
        """

        self.updated_at = datetime.now(timezone.utc).isoformat()

    def attach_structure(
            self,
            structure: ButterflyStructure,
    ) -> None:
        """
        Attach or replace the project's active structure.
        """
        if not isinstance(structure, ButterflyStructure):
            raise TypeError(f"structure must be a ButterflyStructure, got {type(structure).__name}.")
        if not structure.components:
            raise ValueError("The structure has no canonical geometry components.")

        component_names = [component.name for component in structure.components]
        if len(component_names) != len(set(component_names)):
            raise ValueError("Structure component names must be unique.")
        self.structure = structure
        self.touch()

    def detach_structure(self) -> None:
        """
        Remove the currently attached structure.
        """
        self.structure = None
        self.touch()

    def summary(self) -> dict[str, Any]:
        """
        Return a JSON-friendly summary of the project.
        Mesh vertices and faces are intentionally excluded.
        """

        structure_summary = None
        if self.structure is not None:
            structure_summary = {
                "origin": self.structure.origin.value,
                "source_path": self.structure.source_path,
                "component_count": len(self.structure.components),
                "components": [
                    {
                        "name": component.name,
                        "role": component.role.value,
                        "material_id": component.material_id,
                    }    
                    for component in self.structure.components
                ],
            }

        return {
            "schema_version": self.schema_version,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": dict(self.metadata),
            "structure": structure_summary,
        }

    def readiness(self) -> ProjectReadiness:
        if self.structure is None:
            return ProjectReadiness(
                has_structure=False,
                has_components=False,
                geometry_watertight=False,
                geometry_volumetric=False,
                component_names_unique=False,
                materials_complete=False,
                simulation_ready=False,
            )

        components = self.structure.components
        has_components = bool(components)

        component_names = [component.name for component in components]
        names_unique = len(component_names) == len(set(component_names))

        geometry_watertight = has_components and all(component.mesh.is_watertight for component in components)
        geometry_volumetric = has_components and all(component.mesh.is_volume for component in components)

        material_complete = has_components and all(component.material_id is not None for component in components)

        simulation_ready =(
            has_components
            and names_unique
            and geometry_watertight
            and geometry_volumetric
            and material_complete
        )

        return ProjectReadiness(
            has_structure=True,
            has_components=has_components,
            geometry_watertight=geometry_watertight,
            geometry_volumetric=geometry_volumetric,
            component_names_unique=names_unique,
            materials_complete=material_complete,
            simulation_ready=simulation_ready,
        )