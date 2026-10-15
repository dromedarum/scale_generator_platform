import matplotlib.pyplot as plt

def plot_ridge_footprint(structure):
    footprint = structure.ridge_footprint

    fig, ax = plt.subplots(figsize=(8, 8))
    
    if footprint.geom_type == "Polygon":
        x, y = footprint.exterior.xy
        ax.fill(x, y, color="red", alpha=0.8)

    elif footprint.geom_type == "MultiPolygon":
        for poly in footprint.geoms:

            x, y = poly.exterior.xy
            ax.fill(x, y, color="red", alpha=0.8)

    ax.set_aspect("equal")

    plt.show()


