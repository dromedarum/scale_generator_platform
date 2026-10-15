from __future__ import annotations
from collections.abc import Iterable

import matplotlib.pyplot as plt
import numpy as np
import trimesh

from core.structures import ButterflyStructure

def plot_mesh_xz_section(
        ax,
        mesh: trimesh.Trimesh,
        *,
        y_um: float,
        color: str,
        label: str,
        linewidth: float = 1.5,
        alpha: float = 1.0
) -> bool:
    """
    Intersect a mesh with the plane y = y_um and plot the resulting section paths in physical x-z coordinates.
    Returns True if at least one section curve was plotted.
    """

    if mesh is None: 
        return False

    section = mesh.section(plane_origin=np.array([0.0, float(y_um), 0.0], dtype=float), plane_normal=np.array([0.0, 1.0, 0.0], dtype=float))

    if section is None:
        return False

    plotted = False 
    label_used = False

    for path in section.discrete:
        points = np.asarray(path, dtype=float)

        if points.ndim != 2 or points.shape[0] < 2:
            continue

        if points.shape[1] != 3:
            raise ValueError("Expected a 3D section path with shape (N, 3), got", points.shape)

        ax.plot(points[:, 0], points[:, 2], color=color, linewidth=linewidth, alpha=alpha, label=label if not label_used else None)
        plotted = True
        label_used = True

    return plotted

def plot_xz_cross_section(
        structure: ButterflyStructure,
        *,
        y_um: float | None = None,
        show_components: bool = True,
        show_scaffold: bool = True,
        show_nominal_network_top: bool = True,
        show_expected_root_bottom: bool = True,
        show_laminae: bool = True,
):
    """
    Plot an x-z cross-section through the generated butterly structure.
    Parameters
    ----------
    structure
        Butterfly structure containing generated network, ridge, and/or
        scaffold meshes.

    y_um
        Position of the slicing plane along y. If None, the midpoint of
        the structural domain is used.

    show_components
        If True, show the network and ridge component sections separately.

    show_scaffold
        If True, show the Boolean-unified scaffold section.

    show_nominal_network_top
        If True, draw the nominal upper surface of the network slab.

    show_expected_root_bottom
        If True, draw the expected lower boundary of the embedded ridge root.
    """

    params = structure.parameters
    if y_um is None:
        y_um = 0.5 * params.Ly_um

    y_um = float(y_um)
    if not 0.0 <= y_um <= params.Ly_um:
        raise ValueError(f"y_um must lie inside the nominal structural domain [0, {params.Ly_um}], got {y_um}.")

    if structure.network_mesh is None and structure.ridge_mesh is None and structure.scaffold_mesh is None:
        raise ValueError("No generated mesh is available for cross-section plotting")

    fig, ax = plt.subplots(figsize=(11, 6))
    section_found = False
    # ----------------------------------------------------------
    # Component sections
    # ----------------------------------------------------------

    if show_components:

        if structure.network_mesh is not None:
            section_found |= plot_mesh_xz_section(
                ax,
                structure.network_mesh,
                y_um=y_um,
                color="tab:blue",
                label="Network component",
                linewidth=1.2,
                alpha=0.8,
            )

        if structure.ridge_mesh is not None:
            section_found |= plot_mesh_xz_section(
                ax,
                structure.ridge_mesh,
                y_um=y_um,
                color="tab:red",
                label="Ridge component",
                linewidth=1.5,
                alpha=0.9,
            )

        if show_laminae and structure.lamina_mesh is not None:
            section_found |= plot_mesh_xz_section(ax, structure.lamina_mesh, y_um=y_um, color="tab:orange", label="Laminae", linewidth=1.5, alpha=0.9)

    # ----------------------------------------------------------
    # Unified scaffold section
    # ----------------------------------------------------------

    if show_scaffold and structure.scaffold_mesh is not None:
        section_found |= plot_mesh_xz_section(
            ax,
            structure.scaffold_mesh,
            y_um=y_um,
            color="black",
            label="Unified scaffold",
            linewidth=2.0,
            alpha=0.9,
        )

    if not section_found:
        plt.close(fig)

        raise ValueError(
            f"No mesh intersection was found at y = {y_um:.4f} um. "
            "Try a different y position."
        )

    # ----------------------------------------------------------
    # Reference elevations
    # ----------------------------------------------------------

    network_top_z = None

    if structure.network_mesh is not None:
        network_top_z = float(
            structure.network_mesh.bounds[1, 2]
        )

    if (
        show_nominal_network_top
        and network_top_z is not None
    ):
        ax.axhline(
            network_top_z,
            color="tab:green",
            linestyle="--",
            linewidth=1.2,
            label="Nominal network top",
        )

    if (
        show_expected_root_bottom
        and network_top_z is not None
        and structure.ridges is not None
        and structure.ridges.embed_depth_um is not None
    ):
        expected_root_bottom_z = (
            network_top_z
            - float(structure.ridges.embed_depth_um)
        )

        ax.axhline(
            expected_root_bottom_z,
            color="tab:purple",
            linestyle=":",
            linewidth=1.2,
            label="Expected ridge-root bottom",
        )

    # ----------------------------------------------------------
    # Plot formatting
    # ----------------------------------------------------------

    ax.set_aspect(
        "equal",
        adjustable="box",
    )

    ax.set_xlabel("x (um)")
    ax.set_ylabel("z (um)")

    ax.set_title(
        f"x-z cross-section at y = {y_um:.3f} um"
    )

    ax.grid(
        visible=True,
        alpha=0.2,
    )

    handles, labels = ax.get_legend_handles_labels()

    unique_entries = {}

    for handle, label in zip(handles, labels):
        if label and label not in unique_entries:
            unique_entries[label] = handle

    if unique_entries:
        ax.legend(
            unique_entries.values(),
            unique_entries.keys(),
            loc="best",
        )

    fig.tight_layout()

    return fig, ax