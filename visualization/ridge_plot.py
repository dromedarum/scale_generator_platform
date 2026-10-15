import matplotlib.pyplot as plt
import numpy as np
from core.structures import ButterflyStructure

def plot_ridges(structure: ButterflyStructure, opening_centers=None):
    fig, ax = plt.subplots(figsize=(8,8))

    #Network
    if(structure.network is not None and structure.network.vertices is not None):
        vertices = structure.network.vertices
        for i,j in structure.network.edges:
            p1 = vertices[i]
            p2 = vertices[j]

            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="lightgray", linewidth=0.5)

    #Opening centers
    if opening_centers is not None:
        ax.scatter(opening_centers[:,0], opening_centers[:,1], color="blue", s=15, label="Opening centers", zorder=3)


    #Ridge centerlines
    if(structure.ridges is not None and structure.ridges.centerlines is not None):
        for centerline in structure.ridges.centerlines:
            ax.plot(centerline[:,0], centerline[:,1], color= "red", linewidth=2, label=None, zorder=4)

    ax.set_xlim(0, structure.parameters.Lx_um)
    ax.set_xlim(0, structure.parameters.Ly_um)

    ax.set_aspect("equal")
    ax.set_xlabel("x (um)")
    ax.set_ylabel("y (um)")
    ax.set_title("Network-derived ridge placement")
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels,handles))
    ax.legend(by_label.values(), by_label.keys())

    plt.tight_layout()
    plt.show()