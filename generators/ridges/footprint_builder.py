from shapely.geometry import LineString
from shapely.ops import unary_union

from core.structures import ButterflyStructure

class RidgeFootprintBuilder:

    @staticmethod
    def build(
        structure: ButterflyStructure,
    ) -> ButterflyStructure:

        if structure.ridges is None or structure.ridges.centerlines is None:
            raise ValueError("no ridges available.")

        width = structure.ridges.width_um
        ridge_polygons  = []
        for centerline in structure.ridges.centerlines:
            line = LineString(centerline)
            ridge_polygons.append(line.buffer(width / 2, cap_style="flat"))

        structure.ridge_footprint = unary_union(ridge_polygons) 
        return structure