import matplotlib.pyplot as plt

from core.structures import ButterflyStructure


def plot_footprint(
    structure: ButterflyStructure,
):

    footprint = structure.network_footprint

    fig, ax = plt.subplots(figsize=(8, 8))

    if footprint.geom_type == "Polygon":

        x, y = footprint.exterior.xy

        ax.fill(x,y,color="black")

    elif footprint.geom_type == "MultiPolygon":

        for poly in footprint.geoms:

            x, y = poly.exterior.xy

            ax.fill(x,y,color="black")

    ax.set_aspect("equal")

    plt.show()
