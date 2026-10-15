from core.structures import ButterflyStructure

from generators.geometry.extrusion import extrude_2d_solid

class NetworkMeshBuilder:
    @staticmethod
    def build(
        structure: ButterflyStructure,
    ) -> ButterflyStructure:

        if structure.network_footprint is None:
            raise ValueError("No network footprint available.")

        height = structure.parameters.slab_thickness_um
        mesh = extrude_2d_solid(structure.network_footprint, height)

        structure.network_mesh = mesh
        return structure

