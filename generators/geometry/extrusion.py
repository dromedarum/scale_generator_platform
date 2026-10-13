import trimesh
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry.polygon import orient
from shapely import set_precision

GEOMETRY_PRECISION = 1e-4

def extrude_polygon_robust(poly, height: float, engine: str):
    """
    Robust Polygon extrusion wrapper with geometry cleanup and normal correction
    """
    def extrude_single(p):
        p = orient(p, sign=1.0)

        V, F = trimesh.creation.triangulate_polygon(p, engine=engine)
        m = trimesh.creation.extrude_triangulation(V, F, height)

        m.process(validate=True)
        m.fix_normals()
        return m

    if isinstance(poly, Polygon):
        return extrude_single(poly)

    elif isinstance(poly, MultiPolygon):
        meshes = [extrude_single(p) for p in poly.geoms]
        return trimesh.util.concatenate(meshes)

    else:
        raise ValueError("Unsupported geometry")

def extrude_2d_solid(solid, height: float):
    """
    Convert a Polygon or MultiPolygon into a watertight trimesh by triangulating and
    extruding each component.
    """
    if isinstance(solid, Polygon):
        solids = [solid]
    elif isinstance(solid, MultiPolygon):
        solids = list(solid.geoms)
    else:
        raise ValueError("Unsupported geometry")

    meshes = []

    for poly in solids:
        

        poly = set_precision(poly, grid_size=GEOMETRY_PRECISION).buffer(0)

        mesh = extrude_polygon_robust(poly, height, engine="earcut")
        meshes.append(mesh)

    result = trimesh.util.concatenate(meshes)
    #result.process(validate=True)
    #result.fix_normals()

    return result