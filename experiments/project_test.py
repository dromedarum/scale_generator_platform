from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from core.projects import ButterflyProject
from core.structures import (GeometryOrigin, StructureParameters, GeometryImportConfig, LengthUnit, ComponentRole)
from generators.pipeline import generate_structure
from generators.imported.loader import import_structure

import trimesh

bad_metadata_rejected = False
try:
    ButterflyProject(
        name="Invalid metadata test",
        metadata={"invalid": object()}
    )
except TypeError:
    bad_metadata_rejected = True

assert bad_metadata_rejected

#Test 2: Empty-project readiness
empty_project = ButterflyProject(
    name="Empty project readiness test"
)

empty_readiness = empty_project.readiness()

assert not empty_readiness.has_structure
assert not empty_readiness.has_components
assert not empty_readiness.geometry_watertight
assert not empty_readiness.geometry_volumetric
assert not empty_readiness.component_names_unique
assert not empty_readiness.materials_complete
assert not empty_readiness.simulation_ready

#Test 3: Generated structure project
parameters = StructureParameters(
    network_enabled=True,
    ridges_enabled=True,
    multilayer_enabled=True,
    random_seed=42,
)

structure = generate_structure(parameters)

project = ButterflyProject(
    name="Generated morphology test", 
    description="Project-model test using a generated structure.",
    metadata={
        "species": "not_assigned",
        "purpose": "software_validation",
    }
)

project.attach_structure(structure)

assert project.structure is structure
assert project.structure.origin == GeometryOrigin.GENERATED
assert len(project.structure.components) == 4

summary = project.summary()

assert summary["schema_version"] == "1.0"
assert summary["project_id"] == project.project_id
assert summary["name"] == project.name

assert summary["structure"]["origin"] == "generated"
assert summary["structure"]["component_count"] == 4

summary_components = summary["structure"]["components"]
assert len(summary_components) == 4

component_names = [component["name"] for component in summary["structure"]["components"]]
component_roles = [component["role"] for component in summary["structure"]["components"]]

assert len(component_names)== len(set(component_names))

assert component_roles == [
    "scaffold",
    "lamina",
    "lamina",
    "lamina",
]

assert all(component["material_id"] is None for component in summary_components)
assert all(set(component.keys()) == {
    "name",
    "role",
    "material_id",
    }
    for component in summary_components
)

assert all(component.mesh.is_watertight for component in project.structure.components)
assert all(component.mesh.is_volume for component in (project.structure.components))

print("Project ID:", project.project_id)
print("Project name:", project.name)

print("Structure origin:", summary["structure"]["origin"])
print("Components:", component_names)
print("PASS: generated structure can be attached to a ButterflyProject.")

readiness = project.readiness()

assert readiness.has_structure
assert readiness.has_components
assert readiness.geometry_watertight
assert readiness.geometry_volumetric
assert readiness.component_names_unique

assert not readiness.materials_complete
assert not readiness.simulation_ready

with TemporaryDirectory() as temporary_directory:
    temporary_path = Path(temporary_directory)
    imported_source = trimesh.creation.box(extents=[7000.0, 5000.0, 2000.0])
    imported_file = temporary_path/"imported_project_structure.stl"
    imported_source.export(imported_file)
    imported_structure = import_structure(
        imported_file,
        GeometryImportConfig(
            source_unit=LengthUnit.NANOMETER,
            component_name="imported_scaffold",
            component_role=ComponentRole.SCAFFOLD,
            center_xy=True,
            place_bottom_at_z_zero=True,
        )
    )
    imported_project = ButterflyProject(
        name="Imported morpholgy test",
        description="Project-model test using imported geometry."
    )
    imported_project.attach_structure(imported_structure)
    imported_summary = imported_project.summary()

    assert(imported_summary["structure"]["origin"] == "imported")
    assert(imported_summary["structure"]["component_count"] == 1)

    assert(imported_summary["structure"]["components"][0]["name"] == "imported_scaffold")
    assert(imported_summary["structure"]["components"][0]["role"] == "scaffold")


    print("PASS: imported structure can be attached to a ButterflyProject.")

    original_updated_at = project.updated_at
    project.detach_structure()

    assert project.structure is  None
    assert project.updated_at >= original_updated_at

    assert datetime.fromisoformat(project.updated_at) >= datetime.fromisoformat(original_updated_at)

    readiness_after_detach = project.readiness()

    assert not readiness_after_detach.has_structure
    assert not readiness_after_detach.has_components
    assert not readiness_after_detach.simulation_ready

    project.attach_structure(structure)

    assert project.structure is structure
    readiness_after_reattach = project.readiness()

    assert readiness_after_reattach.has_structure
    assert readiness_after_reattach.has_components

    print("PASS: project structures can be detached and reattached")
