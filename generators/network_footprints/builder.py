from core.structures import ButterflyStructure

class NetworkFootprintBuilder:

    @staticmethod
    def build(
        structure: ButterflyStructure,
        width: float
    ) -> ButterflyStructure:
            
        from shapely.geometry import LineString
        from shapely.ops import unary_union
        import numpy as np

        params = structure.parameters
        Lx = params.Lx_um
        Ly = params.Ly_um

        def periodic_delta(p1, p2, Lx, Ly):
            
            d = p2 - p1
            d[0] -= np.round(d[0] / Lx) * Lx
            d[1] -= np.round(d[1] / Ly) * Ly
            return d

        struts = []
        vertices = structure.network.vertices
        edges = structure.network.edges


        for i, j in edges:
            p1 = vertices[i]
            d = periodic_delta(p1, vertices[j], Lx, Ly)
            p2 = p1 + d

            line = LineString([p1, p2])
            struts.append(line.buffer(width/2, join_style=2, cap_style=2))

        structure.network_footprint = unary_union(struts)
        return structure
        

