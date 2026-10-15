from __future__ import annotations

from core.structures import ButterflyStructure, StructureParameters

from generators.network.builder import HyperuniformBuilder
from generators.network.footprint_builder import NetworkFootprintBuilder
from generators.network.mesh_builder import NetworkMeshBuilder
from generators.ridges.builder import RidgeBuilder
from generators.ridges.footprint_builder import RidgeFootprintBuilder
from generators.ridges.mesh_builder import RidgeMeshBuilder
from generators.assembly.scaffold_builder import ScaffoldBuilder
from generators.laminae.builder import LaminaBuilder

def generate_scaffold(
        parameters: StructureParameters,
) -> ButterflyStructure:
    """
    Generate the current network and ridge scaffold
    
    This function is the application-level orchestration entry point.
    Individual builders remain responsible for one transformation each.
    """

    structure = ButterflyStructure(parameters=parameters)

    if parameters.network_enabled:
        structure = HyperuniformBuilder.generate_seed_points(structure)
        structure = HyperuniformBuilder.relax_points(structure)
        structure = HyperuniformBuilder.build_network(structure)
        structure = NetworkFootprintBuilder.build(structure, width=parameters.strut_width_um)
        structure = NetworkMeshBuilder.build(structure)

    if parameters.ridges_enabled:
        structure = RidgeBuilder.generate(structure)
        structure = RidgeFootprintBuilder.build(structure)
        structure = RidgeMeshBuilder.build(structure)

    if structure.network_mesh is not None or structure.ridge_mesh is not None:
        structure = ScaffoldBuilder.build(structure)

    if parameters.multilayer_enabled:
        structure = LaminaBuilder.build(structure)

    return structure
