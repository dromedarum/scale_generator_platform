def periodic_voronoi_network(points, Lx=1.0, Ly=1.0):
    import numpy as np
    from scipy.spatial import Voronoi

    points = np.asarray(points, float)
    N = len(points)

    # --- periodic tiling (correct)
    shifts = [(dx, dy) for dx in (-Lx, 0, Lx)
                        for dy in (-Ly, 0, Ly)]

    tiled = np.vstack([points + [dx, dy] for dx, dy in shifts])

    vor = Voronoi(tiled)

    center_start = 4 * N
    center = set(range(center_start, center_start + N))

    vertex_map = {}
    vertices = []
    edges = set()   # ✅ deduplicate

    def get_idx(v):
        v = np.array([v[0] % Lx, v[1] % Ly])
        key = tuple(np.round(v, 10))   # slightly looser
        if key not in vertex_map:
            vertex_map[key] = len(vertices)
            vertices.append(v)
        return vertex_map[key]

    for (p1, p2), ridge in zip(vor.ridge_points, vor.ridge_vertices):
        if p1 not in center and p2 not in center:
            continue
        if -1 in ridge:
            continue

        i1 = get_idx(vor.vertices[ridge[0]])
        i2 = get_idx(vor.vertices[ridge[1]])

        # ✅ canonical ordering
        edges.add(tuple(sorted((i1, i2))))

    return np.array(vertices), list(edges)
