import numpy as np 
from core.structures import ButterflyStructure, StructureParameters
from core.structures.enums import RidgeMode

from generators.network.builder import HyperuniformBuilder
from generators.network.footprint_builder import NetworkFootprintBuilder
from generators.network.mesh_builder import NetworkMeshBuilder
from generators.ridges.builder import RidgeBuilder
from generators.ridges.footprint_builder import RidgeFootprintBuilder
from generators.ridges.mesh_builder import RidgeMeshBuilder
from generators.assembly.scaffold_builder import ScaffoldBuilder

def generate_structure(
        seed: int,
) -> ButterflyStructure:
    params = StructureParameters(
        ridges_enabled=True,
        ridge_mode=RidgeMode.NETWORK_DERIVED,
        ridge_placement_variation=0.15,
        random_seed=seed,
    )

    structure = ButterflyStructure(parameters=params)
    structure = HyperuniformBuilder.generate_seed_points(structure)
    structure = HyperuniformBuilder.relax_points(structure)
    structure = HyperuniformBuilder.build_network(structure)
    structure = NetworkFootprintBuilder.build(structure, width=params.strut_width_um)
    structure = NetworkMeshBuilder.build(structure)
    structure = RidgeBuilder.generate(structure)
    structure = RidgeFootprintBuilder.build(structure)
    structure = RidgeMeshBuilder.build(structure)
    structure = ScaffoldBuilder.build(structure)
    return structure

structure_a = generate_structure(42)
structure_b = generate_structure(42)
structure_c = generate_structure(43)

np.testing.assert_allclose(structure_a.network.seed_points, structure_b.network.seed_points)
np.testing.assert_allclose(structure_a.network.relaxed_points, structure_b.network.relaxed_points)
np.testing.assert_allclose(structure_a.ridges.local_spacings_um, structure_b.ridges.local_spacings_um)

assert not np.allclose(structure_a.network.seed_points, structure_c.network.seed_points)
print("PASS: identical seeds reproduce the morphology.")
print("PASS: different seeds create different realizations.")

