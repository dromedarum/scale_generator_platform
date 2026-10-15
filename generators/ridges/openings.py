import numpy as np
from shapely.geometry import box

def get_void_polygons(footprint, Lx, Ly):
    """
    Return all void polygons inside the domain
    """
    domain = box(0, 0, Lx, Ly)
    voids = domain.difference(footprint)

    if voids.geom_type == "Polygon":
        return [voids]

    elif voids.geom_type == "MultiPolygon":
        return list(voids.geoms)

    else:
        return []

def opening_widths_x(voids):
    widths = []
    for v in voids:
        xmin, ymin, xmax, ymax = v.bounds
        widths.append(xmax - xmin)

    return np.asarray(widths)

def opening_centers(voids):
    """
    Return opening centroids as an (N,2) array
    """

    centers = []
    for v in voids:
        c = v.centroid
        centers.append([c.x, c.y])

    return np.asarray(centers)

def sort_openings_by_x(centers):
    order = np.argsort(centers[:,0])
    return centers[order]

def interior_voids(
        voids,
        Lx: float,
        Ly: float,
        tolerance: float = 1e-9,
):
    """
    Return openings that do not intersect the rectangular domain boundary.

    Boundary-truncated openings remain useful for visualization, but should not
    contribute to opening-width statistics used for morphology generation.
    """
    selected = []

    for void in voids:
        xmin, ymin, xmax, ymax = void.bounds

        touches_boundary = (
            xmin <= tolerance or ymin <= tolerance or xmax >= Lx - tolerance or ymax >= Ly - tolerance
        )

        if not touches_boundary:
            selected.append(void)

    return selected

