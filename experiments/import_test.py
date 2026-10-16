from pathlib import Path 
from tempfile import TemporaryDirectory

import numpy as np
import trimesh

from core.structures import (GeometryImportConfig, 
                            GeometryOrigin, 
                            LengthUnit, 
                            GeometryImportSpec, 
                            AssemblyImportConfig, 
                            ImportTransformMode,
                            ComponentRole)
from generators.imported.loader import import_structure_components, import_structure

with TemporaryDirectory() as temporary_directory:
    temporary_path = Path(temporary_directory)
    config = GeometryImportConfig(
        source_unit=LengthUnit.NANOMETER,
        component_name="imported_test_component",
        component_role=ComponentRole.SCAFFOLD,
        process_mesh=True,
        require_watertight=True,
        require_volume=True,
        center_xy=True,
        place_bottom_at_z_zero=True,
    )

    source = trimesh.creation.box(extents=[7000.0, 5000.0, 2000.0])
    source_file = temporary_path/"scaffold.stl"
    source.export(source_file)

    structure = import_structure(source_file, config)

    assert structure.origin == GeometryOrigin.IMPORTED
    assert structure.parameters is None
    assert len(structure.components) == 1

    component = structure.components[0]

    assert component.name == "imported_test_component"
    assert component.role == ComponentRole.SCAFFOLD

    np.testing.assert_allclose(
        component.mesh.extents,
        [7.0, 5.0, 2.0],
        atol=1e-9,
    )

    expected_bounds = np.asarray([[-3.5, -2.5, 0.0], [3.5, 2.5, 2.0]], dtype=float)

    np.testing.assert_allclose(
        component.mesh.bounds,
        expected_bounds,
        atol=1e-9
    )

    assert component.mesh.is_watertight
    assert component.mesh.is_volume

    assert(component.metadata["source_unit"] == "nm")

    expected_scale_to_um = {LengthUnit.NANOMETER: 1.0e-3,
                            LengthUnit.MICROMETER: 1.0,
                            LengthUnit.MILIMETER: 1.0e3,
                            LengthUnit.METER: 1.0e6
                            }[config.source_unit]
    np.testing.assert_allclose(component.metadata["scale_to_um"], expected_scale_to_um, atol=1e-15)

    source_hash = component.metadata["source_sha256"]
    assert isinstance(source_hash, str)
    assert len(source_hash) == 64

    int(source_hash, 16)

    print("PASS: one-file geometry import creates a canonical imported ButterflyStructure in micrometers.")

with TemporaryDirectory() as temporary_directory:
    temporary_path = Path(temporary_directory)

    scaffold_source = trimesh.creation.box(extents=[7000.0, 5000.0, 2000.0])
    lamina_source = trimesh.creation.box(extents=[7000.0, 5000.0, 120.0])
    
    lamina_source.apply_translation([0.0,0.0,-1705.0])
    scaffold_file = (temporary_path/"scaffold.stl")
    lamina_file = (temporary_path/"lamina.stl")

    assert scaffold_file != lamina_file

    scaffold_source.export(scaffold_file)
    lamina_source.export(lamina_file)

    specifications = [
        GeometryImportSpec(
            path=scaffold_file,
            config=GeometryImportConfig(
                source_unit=LengthUnit.NANOMETER,
                component_name="scaffold",
                component_role=ComponentRole.SCAFFOLD,
                process_mesh=True,
                require_watertight=True,
                require_volume=True,
                center_xy=False,
                place_bottom_at_z_zero=False,
            ),
        ),
        GeometryImportSpec(
            path=lamina_file,
            config=GeometryImportConfig(
                source_unit=LengthUnit.NANOMETER,
                component_name="lamina_1",
                component_role=ComponentRole.LAMINA,
                process_mesh=True,
                require_watertight=True,
                require_volume=True,
                center_xy=False,
                place_bottom_at_z_zero=False,
            ),
        ),
        ]

    structure = import_structure_components(
        specifications, 
        assembly_config=AssemblyImportConfig(
            transform_mode=(ImportTransformMode.NORMALIZE_ASSEMBLY),
            center_xy=True,
            place_bottom_at_z_zero=True,
        ))
    expected_gap_nm = 645
    expected_gap_um = expected_gap_nm * 1.0e-3

    scaffold_bottom_nm = -1000.0
    lamina_half_thickness = 60.0
    desired_lamina_top_nm = (scaffold_bottom_nm - expected_gap_nm)
    desired_lamina_center_nm = desired_lamina_top_nm - lamina_half_thickness
    lamina_source.apply_translation([0.0, 0.0, desired_lamina_center_nm])

    print("Name, Extents, Source Path, Original name")
    for component in structure.components:
        print(component.name, component.mesh.extents, component.metadata["source_path"], component.metadata["original_file_name"])
    assert structure.origin == GeometryOrigin.IMPORTED
    assert structure.parameters is None
    assert structure.source_path is None

    assert len(structure.components) == 2

    scaffold_component = structure.components[0]
    lamina_component = structure.components[1]

    assert scaffold_component.name == "scaffold"
    assert scaffold_component.role == ComponentRole.SCAFFOLD

    assert lamina_component.name == "lamina_1"
    assert lamina_component.role == ComponentRole.LAMINA
    scaffold_bottom = float(scaffold_component.mesh.bounds[0, 2])
    lamina_top = float(lamina_component.mesh.bounds[1, 2])
    acutal_gap_um = scaffold_bottom - lamina_top

    np.testing.assert_allclose(acutal_gap_um, expected_gap_um, atol=1e-9)
    np.testing.assert_allclose(scaffold_component.mesh.extents, [7.0, 5.0, 2.0], atol=1e-9)
    np.testing.assert_allclose(lamina_component.mesh.extents, [7.0, 5.0, 0.12], atol=1e-9)

    scaffold_translation = np.asarray(scaffold_component.metadata["assembly_translation_um"], dtype=float)
    lamina_translation = np.asarray(lamina_component.metadata["assembly_translation_um"], dtype=float)

    np.testing.assert_allclose(scaffold_translation, lamina_translation, atol=1e-12)
    assert all(component.mesh.is_watertight for component in structure.components)
    assert all(component.mesh.is_volume for component in structure.components)

    assert(scaffold_component.metadata["source_unit"] == "nm")
    assert(lamina_component.metadata["source_unit"] == "nm")

    assert scaffold_component.metadata["source_sha256"] != lamina_component.metadata["source_sha256"]

    print("PASS: multiple imported files retain independent canonical geometry components.")
    
    