import numpy as np
from core.structures import ButterflyStructure
from core.structures.network import HyperuniformNetwork
from .lloyd import lloyd_relaxation
from .voronoi import periodic_voronoi_network


class HyperuniformBuilder: 

    @staticmethod
    def generate_seed_points(
        structure: ButterflyStructure,
    ) -> ButterflyStructure:
        """
        Generate the seed points for the Hyperunifrom Network,
        modelling the middle section of a butterfly wing scale
        """
        params = structure.parameters

        points = np.random.rand(
            params.network_points,
            2,
        )

        points[:,0] *= params.Lx_um
        points[:,1] *= params.Ly_um

        if structure.network is None:
            structure.network = HyperuniformNetwork()
        
        structure.network.seed_points = points
        
        return structure


    @staticmethod
    def relax_points(
            structure: ButterflyStructure,
    ) -> ButterflyStructure:
        """
        Use Lloyd-Relaxtion algorithm to relax point cloud for Hyperuniform Network
        """
        params = structure.parameters
        seed_points = structure.network.seed_points
        relaxed_points = lloyd_relaxation(
            seed_points,
            Lx=params.Lx_um,
            Ly=params.Ly_um,
            iterations=100,
        )

        structure.network.relaxed_points = (relaxed_points)
        return structure


    @staticmethod
    def build_network(
        structure: ButterflyStructure,
    ) -> ButterflyStructure:
        params = structure.parameters
        points = structure.network.relaxed_points

        vertices, edges = periodic_voronoi_network(points, params.Lx_um, params.Ly_um)

        structure.network.vertices = vertices
        structure.network.edges = edges

        return structure
