from __future__ import annotations  
import numpy as np
import matplotlib.pyplot as plt

from core.structures import StructureParameters
from generators.pipeline import generate_structure


def generate_lamina_realization(
    seed: int,
):
    params = StructureParameters(
        network_enabled=True,
        ridges_enabled=True,
        multilayer_enabled=True,
        material_layers_um=[
            0.12,
            0.12,
            0.12,
        ],
        air_layers_um=[
            0.06,
            0.06,
        ],
        material_layer_variation=0.10,
        air_gap_variation=0.15,
        vertical_gap_um=0.645,
        random_seed=seed,
    )

    return generate_structure(params)


structure_a = generate_lamina_realization(42)
structure_b = generate_lamina_realization(42)
structure_c = generate_lamina_realization(43)


np.testing.assert_allclose(
    structure_a.laminae.material_layer_thickness_um,
    structure_b.laminae.material_layer_thickness_um,
)

np.testing.assert_allclose(
    structure_a.laminae.air_gap_thickness_um,
    structure_b.laminae.air_gap_thickness_um,
)


same_layers_for_different_seed = np.allclose(
    structure_a.laminae.material_layer_thickness_um,
    structure_c.laminae.material_layer_thickness_um,
)

same_gaps_for_different_seed = np.allclose(
    structure_a.laminae.air_gap_thickness_um,
    structure_c.laminae.air_gap_thickness_um,
)

assert not (
    same_layers_for_different_seed
    and same_gaps_for_different_seed
)


print(
    "PASS: lamina morphology is reproducible for the same "
    "seed and changes for a different seed."
)

""" params = StructureParameters(
    network_enabled=True,
    ridges_enabled=True,
    multilayer_enabled=True,
    material_layers_um=[0.12, 0.12, 0.12],
    air_layers_um=[0.06, 0.06],
    material_layer_variation=0.0,
    air_gap_variation=0.0,
    vertical_gap_um=0.645,
    random_seed=42,
)

structure = generate_scaffold(params)

assert structure.laminae is not None
assert structure.lamina_mesh is not None

print("realized material layers:", structure.laminae.material_layer_thickness_um)
print("realized air gaps:", structure.laminae.air_gap_thickness_um)
print("layer bottoms:", structure.laminae.layer_bottom_z_um)
print("layer tops", structure.laminae.layer_top_z_um)
print("lamina mesh bounds:", structure.lamina_mesh.bounds)
print("lamina components:", len(structure.lamina_mesh.split(only_watertight=False)))

expected_layer_count = len(params.material_layers_um)
assert len(structure.laminae.layer_meshes) == expected_layer_count
assert len(structure.lamina_mesh.split(only_watertight=False)) == expected_layer_count

expected_top = - params.vertical_gap_um

np.testing.assert_allclose(structure.laminae.layer_top_z_um[0], expected_top)
print("PASS: lamina system generated with correct layer count and scaffold separation")

plot_xz_cross_section(
    structure,
    y_um=0.5 * params.Ly_um,
    show_components=False,
    show_scaffold=True,
    show_laminae=True,
)

plt.show() """