import numpy as np 
from core.structures import ButterflyStructure, StructureParameters
from core.structures.enums import RidgeMode
"""
from generators.network.builder import HyperuniformBuilder
from generators.network.footprint_builder import NetworkFootprintBuilder
from generators.network.mesh_builder import NetworkMeshBuilder
from generators.ridges.builder import RidgeBuilder
from generators.ridges.footprint_builder import RidgeFootprintBuilder
from generators.ridges.mesh_builder import RidgeMeshBuilder
from generators.assembly.scaffold_builder import ScaffoldBuilder """

from generators.pipeline import generate_structure

def generate_structure_with_seed(
        seed: int,
) -> ButterflyStructure:
    params = StructureParameters(
        ridges_enabled=True,
        ridge_mode=RidgeMode.NETWORK_DERIVED,
        ridge_placement_variation=0.15,
        random_seed=seed,
    )

    structure = generate_structure(params)
    return structure 

structure_a = generate_structure_with_seed(42)
structure_b = generate_structure_with_seed(42)
structure_c = generate_structure_with_seed(43)

np.testing.assert_allclose(structure_a.network.seed_points, structure_b.network.seed_points)
np.testing.assert_allclose(structure_a.network.relaxed_points, structure_b.network.relaxed_points)
np.testing.assert_allclose(structure_a.ridges.local_spacings_um, structure_b.ridges.local_spacings_um)

assert not np.allclose(structure_a.network.seed_points, structure_c.network.seed_points)
print("PASS: identical seeds reproduce the morphology.")
print("PASS: different seeds create different realizations.")

