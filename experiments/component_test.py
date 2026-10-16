from core.structures import GeometryOrigin, StructureParameters, ComponentRole
from generators.pipeline import generate_structure

import numpy as np

params = StructureParameters(
    network_enabled=True,
    ridges_enabled=True,
    multilayer_enabled=True,
)

structure = generate_structure(params)

assert structure.origin == GeometryOrigin.GENERATED
assert structure.laminae is not None, ("Expected a LaminaSystem, but no laminae were generated.")

expected_lamina_count = len(structure.laminae.layer_meshes)
expected_component_count = 1 + expected_lamina_count
assert len(structure.components) == expected_component_count

scaffold_component = structure.components[0]
lamina_components = structure.components[1:]

assert scaffold_component.name == "scaffold"
assert scaffold_component.role == ComponentRole.SCAFFOLD

assert scaffold_component.mesh is structure.scaffold_mesh

assert len(lamina_components) == expected_lamina_count
#Validate each lamina component dynamically
for index, component in enumerate(lamina_components):
    expected_name = f"lamina_{index + 1}"
    expected_thickness = float(structure.laminae.material_layer_thickness_um[index])
    expected_bottom_z = float(structure.laminae.layer_bottom_z_um[index])
    expected_top_z = float(structure.laminae.layer_top_z_um[index])

    assert component.name == expected_name
    assert component.role == ComponentRole.LAMINA

    assert component.metadata["layer_index"] == index
    assert np.isscalar(component.metadata["thickness_um"])
    assert np.isscalar(component.metadata["bottom_z_um"])
    assert np.isscalar(component.metadata["top_z_um"])
    np.testing.assert_allclose(component.metadata["thickness_um"], expected_thickness, atol=1e-12)
    np.testing.assert_allclose(component.metadata["bottom_z_um"], expected_bottom_z, atol=1e-12)
    np.testing.assert_allclose(component.metadata["top_z_um"], expected_top_z, atol=1e-12)

    #validate metadata against actual component geometry.
    mesh_bottom_z = float(component.mesh.bounds[0,2])
    mesh_top_z = float(component.mesh.bounds[1,2])
    mesh_thickness = mesh_top_z - mesh_bottom_z

    np.testing.assert_allclose(mesh_bottom_z, expected_bottom_z, atol=1e-9)
    np.testing.assert_allclose(mesh_top_z, expected_top_z, atol=1e-9)
    np.testing.assert_allclose(mesh_thickness, expected_thickness, atol=1e-9)

    assert component.mesh.is_watertight
    assert component.mesh.is_volume

assert all(component.mesh.is_watertight for component in structure.components)
assert all(component.mesh.is_volume for component in structure.components)

print("Structure Origin:", structure.origin)
print("Number of canonical components:", len(structure.components))

for component in structure.components:
    print(component.name, component.role.value, component.mesh.bounds, component.metadata)

print("PASS: generated structure exposes canonical simulation components.")

