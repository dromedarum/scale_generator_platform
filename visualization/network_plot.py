import matplotlib.pyplot as plt
import numpy as np

from core.structures import ButterflyStructure

def plot_network(
        structure: ButterflyStructure,
        show_seed_points: bool = True,
        show_relaxed_points: bool = True,
):
    """
    Visualize the hyperuniform network
    """

    if structure.network is None:
        raise ValueError("Structure has no network.")

    fig, ax = plt.subplots(figsize=(8,8))


    # ---------------------------------
    # Draw edges
    # ---------------------------------

    if (structure.network.vertices is not None and structure.network.edges is not None):

        params = structure.parameters
        vertices = structure.network.vertices

        for i, j in structure.network.edges:

            p1 = vertices[i]
            p2 = vertices[j]

            dx = abs(p2[0] - p1[0])
            dy = abs(p2[1] - p1[1])

            if dx > params.Lx_um / 2:
                continue

            if dy > params.Ly_um /2:
                continue

            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="black", linewidth=0.8, alpha=0.7)

    # ---------------------------------
    # Draw relaxed points
    # ---------------------------------

    if (show_relaxed_points and structure.network.relaxed_points is not None):

        pts = structure.network.relaxed_points

        ax.scatter(pts[:, 0], pts[:, 1], s=12, color="red", label="Relaxed points", zorder=3)

    # ---------------------------------
    # Draw seed points
    # ---------------------------------

    if (show_seed_points and structure.network.seed_points is not None):

        pts = structure.network.seed_points

        ax.scatter(pts[:, 0], pts[:, 1], s=8, color="blue", alpha=0.5, label="Seed points", zorder=2)

    params = structure.parameters

    ax.set_xlim(0, params.Lx_um)
    ax.set_ylim(0, params.Ly_um)

    ax.set_aspect("equal")

    ax.set_xlabel("x (µm)")
    ax.set_ylabel("y (µm)")

    ax.set_title("Hyperuniform Network")

    ax.legend()

    plt.tight_layout()
    plt.show()