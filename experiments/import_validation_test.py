from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

import trimesh
from core.structures import GeometryImportConfig, LengthUnit, ComponentRole

from core.structures.validation import validate_mesh
from generators.imported.loader import import_structure

with TemporaryDirectory() as temporary_directory:
    temporary_path = Path(temporary_directory)

    source_mesh = trimesh.creation.box(extents=[7000.0, 5000.0, 2000.0])
    source_file = temporary_path/"validation_structure.stl"

    source_mesh.export(source_file)
    config = GeometryImportConfig(
        source_unit=LengthUnit.NANOMETER,
        component_name="validated_import",
        component_role=ComponentRole.SCAFFOLD,
        process_mesh=True,
        require_watertight=True,
        require_volume=True,
        center_xy=True,
        place_bottom_at_z_zero=True,
    )

    structure = import_structure(source_file, config)

    component = structure.components[0]
    report = validate_mesh(component.name, component.mesh)

    print(asdict(report))

    assert report.exists
    assert report.is_watertight
    assert report.is_volume
    assert report.component_count == 1
    assert report.vertex_count is not None
    assert report.vertex_count > 0
    assert report.face_count is not None
    assert report.face_count > 0

    print("PASS: imported component produces a valid geometry report.")