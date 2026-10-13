

def polygon_centroid(vertices):
    """
    Compute the are-weighted centroid of a 2D polygon.

    :param vertices: (N, 2) array, ordered
    """
    import numpy as np

    x = vertices[:,0]
    y = vertices[:,1]

    #shoelace formula
    a = x[:-1] * y[1:] - x[1:] * y[:-1]
    A = a.sum() / 2.0

    if abs(A) < 1e-14:
        return None
    
    cx = ((x[:-1] + x[1:]) * a).sum() / (6 * A)
    cy = ((y[:-1] + y[1:]) * a).sum() / (6 * A)

    return np.array([cx, cy])

def lloyd_relaxation(points, Lx=1.0, Ly=1.0, iterations=20):
    import numpy as np
    from scipy.spatial import Voronoi

    points = np.asarray(points, float)
    N = len(points)

    shifts = [(dx, dy) for dx in (-Lx, 0, Lx)
                        for dy in (-Ly, 0, Ly)]

    for _ in range(iterations):

        tiled = np.vstack([points + [dx, dy] for dx, dy in shifts])
        vor = Voronoi(tiled)

        center_start = 4 * N
        new_points = points.copy()

        for i in range(N):
            gi = center_start + i

            region = vor.regions[vor.point_region[gi]]
            if not region or -1 in region:
                continue

            poly = vor.vertices[region]

            c = polygon_centroid(np.vstack([poly, poly[0]]))
            if c is None:
                continue

            new_points[i] = [c[0] % Lx, c[1] % Ly]

        points = new_points

    return points