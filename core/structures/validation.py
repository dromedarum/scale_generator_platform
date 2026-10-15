from __future__ import annotations

from dataclasses import dataclass
from typing import Any 

import numpy as np
import trimesh

@dataclass
class MeshValidationReport:
    name: str

    exists: bool

    vertex_count: int | None = None 
    face_count: int | None = None
    
    is_watertight: bool | None = None
    is_volume: bool | None = None

    component_count: int | None = None

    bounds_um: list[list[float]] | None = None
    extents_um: list[float] | None = None

    volume_um3: float | None = None

def validate_mesh(
        name: str,
        mesh: trimesh.Trimesh | None,
) -> MeshValidationReport:
    if mesh is None:
        return MeshValidationReport(
            name=name,
            exists=False,
        )

    bounds = np.asarray(mesh.bounds, dtype=float)
    extents = np.asarray(mesh.extents, dtype=float)
    components = mesh.split(only_watertight=False)
    return MeshValidationReport(
        name=name,
        exists=True,
        vertex_count=int(len(mesh.vertices)),
        face_count=int(len(mesh.faces)),
        is_watertight=bool(mesh.is_watertight),
        is_volume=bool(mesh.is_volume),
        component_count=int(len(components)),
        bounds_um=bounds.tolist(),
        extents_um=extents.tolist(),
        volume_um3=float(mesh.volume),
    )

@dataclass
class StructureValidationReport:
    network: MeshValidationReport
    ridges: MeshValidationReport
    scaffold: MeshValidationReport
    laminae: MeshValidationReport

    network_ridge_overlap_um3: float | None = None
    scaffold_solid_fraction_nominal: float | None = None

def validate_structure_geometry(
        structure,
) -> StructureValidationReport:

    network_report = validate_mesh("network", structure.network_mesh)
    ridge_report = validate_mesh("ridges",structure.ridge_mesh)
    scaffold_report = validate_mesh("scaffold",structure.scaffold_mesh)
    lamina_report = validate_mesh("laminae", structure.lamina_mesh)

    overlap_volume = None

    if network_report.volume_um3 is not None and ridge_report.volume_um3 is not None and scaffold_report.volume_um3 is not None:
        overlap_volume = float(network_report.volume_um3 + ridge_report.volume_um3 - scaffold_report.volume_um3)

    nominal_solid_fraction = None

    if scaffold_report.volume_um3 is not None:
        params = structure.parameters

        nominal_bounding_volume = params.Lx_um * params.Ly_um * params.total_structure_height_um

        if nominal_bounding_volume > 0:
            nominal_solid_fraction = float(scaffold_report.volume_um3 / nominal_bounding_volume)

    return StructureValidationReport(
            network=network_report,
            ridges=ridge_report,
            scaffold=scaffold_report,
            laminae=lamina_report,
            network_ridge_overlap_um3=overlap_volume,
            scaffold_solid_fraction_nominal=nominal_solid_fraction,
    )
