import matplotlib.pyplot as plt
from core.structures import ButterflyStructure

def plot_openings(structure: ButterflyStructure, centers):

    fig, ax = plt.subplots(figsize=(8, 8))
    #Draw network edges
    vertices = structure.network.vertices
    for i, j in structure.network.edges:
        p1 = vertices[i]
        p2 = vertices[j]

        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="lightgray", linewidth=0.5)

    #Opening centers
    ax.scatter(centers[:,0], centers[:,1], color="red", s=15, zorder=5, label="Opening centroids")
    ax.scatter(structure.network.relaxed_points[:,0],structure.network.relaxed_points[:,1],color="blue",s=8,label="Relaxed points")
    ax.scatter(centers[:,0],centers[:,1],color="red",s=15,label="Opening centers")
    ax.set_aspect("equal")