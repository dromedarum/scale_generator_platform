from __future__ import annotations

from pathlib import Path
from hashlib import sha256

import numpy as np
import trimesh

from core.structures import (
    ButterflyStructure,
    GeometryComponent, 
    GeometryImportConfig, 
    GeometryOrigin, 
    GeometryImportSpec, 
    LengthUnit,
    ImportTransformMode,
    AssemblyImportConfig,
)


_UNIT_TO_MICROMETER = {
    LengthUnit.NANOMETER: 1.0e-3,
    LengthUnit.MICROMETER: 1.0,
    LengthUnit.MILIMETER: 1.0e3,
    LengthUnit.METER: 1.0e6,
}

def _unit_scale_to_um(unit: LengthUnit) -> float:
    try:
        return _UNIT_TO_MICROMETER[unit]
    except KeyError as exc:
        raise ValueError(f"Unsupported source unit: {unit}") from exc

def _load_single_mesh(path: Path, *, process_mesh: bool) -> trimesh.Trimesh:
    loaded = trimesh.load(path, force="mesh", process=process_mesh)

    if isinstance(loaded, trimesh.Scene):
        geometries = [geometry for geometry in loaded.geometry.values() if isinstance(geometry, trimesh.Trimesh)]
        if not geometries:
            raise ValueError(f"No mesh geometry was found in {path}.")
        loaded = trimesh.util.concatenate(geometries)

    if not isinstance(loaded, trimesh.Trimesh):
        raise TypeError(f"Expected a Trimesh after loading {path}, got {type(loaded).__name__}.")

    if loaded.vertices.size == 0:
        raise ValueError(f"Imported mesh contains no vertices: {path}")
    if loaded.faces.size == 0:
        raise ValueError(f"Imported mesh contains no faces: {path}")
    if not np.all(np.isfinite(loaded.vertices)):
        raise ValueError(f"Imported mesh contains non-finite coordinates: {path}")

    return loaded

def _sha256_file(path: Path,) -> str:
    hasher = sha256()

    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _import_component(path: str | Path, config: GeometryImportConfig) -> GeometryComponent:
    source_path = Path(path)

    if not source_path.exists():
        raise FileNotFoundError(f"Geometry file was not found: {source_path}")

    if source_path.suffix.lower() not in {".stl", ".obj"}:
        raise ValueError(f"Supported geometry formats are STL and OBJ, got {source_path.suffix!r}.")

    mesh = _load_single_mesh(source_path, process_mesh=config.process_mesh)
    scale_to_um = _unit_scale_to_um(config.source_unit)

    mesh.apply_scale(scale_to_um)
    if config.center_xy:
        bounds = np.asarray(mesh.bounds, dtype=float)

        center_x = 0.5 * (bounds[0, 0] + bounds[1, 0])
        center_y = 0.5 * (bounds[0, 1] + bounds[1, 1])

        mesh.apply_translation([-center_x, -center_y, 0.0])

        if config.place_bottom_at_z_zero:
            bottom_z = float(mesh.bounds[0, 2])
            mesh.apply_translation([0.0, 0.0, -bottom_z])

        if config.require_watertight and not mesh.is_watertight:
            raise ValueError(f"Imported mesh is not watertight: {source_path}")
        if config.require_volume and not mesh.is_volume:
            raise ValueError(f"Imported mesh is not recognized as a closed volume: {source_path}")

    source_hash = _sha256_file(source_path)
    return GeometryComponent(
        name=config.component_name,
        mesh=mesh,
        role=config.component_role,
        metadata={
            "source_path": str(source_path.resolve()),
            "source_unit": config.source_unit.value,
            "scale_to_um": scale_to_um,
            "process_mesh": config.process_mesh,
            "watertight_after_import": bool(mesh.is_watertight),
            "volume_after_import": mesh.is_volume,
            "vertex_count_after_import": int(len(mesh.vertices)),
            "face_count_after_import": int(len(mesh.faces)),
            "original_file_name": source_path.name,
            "source_sha256": source_hash,
        }
    )

def import_structure(path: str | Path, config: GeometryImportConfig) -> ButterflyStructure:
    """
    Import one mesh file into the canonical ButterflyStructure model.
    """

    component = _import_component(path, config)

    return ButterflyStructure(
        parameters=None,
        origin=GeometryOrigin.IMPORTED,
        source_path=str(Path(path).resolve()),
        components=[component],
    )

def import_structure_components(
        specifications: list[GeometryImportSpec], 
        assembly_config: AssemblyImportConfig | None = None
        ) -> ButterflyStructure:
    """
    Import multiple mesh files into one canonical structure.
    All components remain seperate and retain their own role,
    name and source-file metadata.
    """
    if assembly_config is None:
        assembly_config = AssemblyImportConfig()
    if not specifications:
        raise ValueError("At least one geometry import specification is required.")

    components: list[GeometryComponent] = []
    component_names: set[str] = set()

    for specification in specifications:
        component = _import_component(
            specification.path,
            specification.config,
        )

        if component.name in component_names:
            raise ValueError(f"Imported component names must be unique. Duplicate name: {component.name!r}")

        component_names.add(component.name)
        components.append(component)

    all_bounds = np.asarray([component.mesh.bounds for component in components], dtype=float)
    assembly_min = np.min(all_bounds[:, 0, :], axis=0)
    assembly_max = np.max(all_bounds[:, 1, :], axis=0)

    translation = np.zeros(3, dtype=float)

    if assembly_config.center_xy:
        translation[0] = -0.5 * (assembly_min[0] + assembly_max[0])
        translation[1] = -0.5 * (assembly_min[1] + assembly_max[1])

    if assembly_config.place_bottom_at_z_zero:
        translation[2] = -assembly_min[2]

    if not np.allclose(translation, 0.0):
        for component in components:
            component.mesh.apply_translation(translation)
            component.metadata["assembly_translation_um"] = translation.tolist()
    else:
        for component in components:
            component.metadata["assembly_translation_um"] = [0.0, 0.0, 0.0]

    assembly_config=AssemblyImportConfig(
        transform_mode=ImportTransformMode.NORMALIZE_ASSEMBLY,
        center_xy=True,
        place_bottom_at_z_zero=True,
    )

    return ButterflyStructure(
        parameters=None,
        origin=GeometryOrigin.IMPORTED,
        source_path=None,
        components=components,
    )



