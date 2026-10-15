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
        seed = structure.parameters.random_seed
        rng = np.random.default_rng(seed)

        points = rng.random((params.network_points,2))

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
        if structure.network is None:
            raise ValueError("No HyperuniformNetwork exists. Generate seed points before relaxation.")
        params = structure.parameters
        seed_points = np.asarray(structure.network.seed_points, dtype=float)

        if seed_points.ndim != 2 or seed_points.shape[1] != 2:
            raise ValueError("seed_points must have shape (N,2), got", seed_points.shape)

        relaxed_points = lloyd_relaxation(
            seed_points,
            Lx=params.Lx_um,
            Ly=params.Ly_um,
            iterations=params.lloyd_iterations,
        )

        relaxed_points = np.asarray(relaxed_points, dtype=float)

        if relaxed_points.ndim != 2 or relaxed_points.shape != seed_points.shape:
            raise ValueError(f"Lloyd relaxation returned an invalid array. Expected {seed_points.shape}, got {relaxed_points.shape}.")
        
        structure.network.relaxed_points = relaxed_points
        
        return structure


    @staticmethod
    def build_network(
        structure: ButterflyStructure,
    ) -> ButterflyStructure:
        params = structure.parameters

        if structure.network is None:
            raise ValueError("No HyperuniformNetwork exists. Generate seed points and relax them before building the Voronoi network.")

        if structure.network.relaxed_points is None:
            raise ValueError("No relaxed points are available. Call HyperuniformBuilder.relax_points() before HyperuniformBuilder.build_network().")

        points = np.asarray(structure.network.relaxed_points, dtype=float)

        if points.ndim != 2 or points.shape[1] != 2:
            raise ValueError("relaxed_points must have shape (N,2), got shape ",points.shape)

        if not np.all(np.isfinite(points)):
            raise ValueError("relaxed_points contains non-finite coordinates.")
        
        vertices, edges = periodic_voronoi_network(points, params.Lx_um, params.Ly_um)

        structure.network.vertices = vertices
        structure.network.edges = edges

        return structure
