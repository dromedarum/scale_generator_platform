from __future__ import annotations

import numpy as np
import trimesh

from core.structures import ButterflyStructure
from core.structures.laminae import LaminaSystem


def _sample_positive_values(
        nominal_values: list[float],
        *,
        relative_variation: float,
        rng: np.random.Generator,
        minimum_fraction: float = 0.5,
        maximum_fraction: float = 1.5,
) -> list[float]:
    """
    Generate realized positive values around nominal morphology values.

    Parameters
    ----------
    nominal_values
        Requested material-layer or air-gap thicknesses in micrometers.

    relative_variation
        Relative standard deviation used for sampling. For example,
        0.10 corresponds to a standard deviation of 10% of each nominal
        value.

    rng
        Seeded NumPy random-number generator.

    minimum_fraction
        Smallest permitted realized value relative to its nominal value.

    maximum_fraction
        Largest permitted realized value relative to its nominal value.

    Returns
    -------
    list[float]
        Realized thicknesses in micrometers.
    """
    if relative_variation < 0:
        raise ValueError("relative_variation must be greater than or equal "
            f"to zero, got {relative_variation}")

    if minimum_fraction <= 0:
        raise ValueError("minimum_fraction must be positive, "
            f"got {minimum_fraction}")

    if maximum_fraction < minimum_fraction:
        raise ValueError("maximum_fraction must be greater than or equal to minimum_fraction.")
    
    realized_values: list[float] = []

    for nominal_value in nominal_values:
        nominal_value = float(nominal_value)

        if nominal_value <= 0:
            raise ValueError(f"All nominal values must be positive, got {nominal_value}")

        if relative_variation == 0.0:
            realized_values.append(nominal_value)
            continue

        lower = minimum_fraction * nominal_value
        upper = maximum_fraction * nominal_value 

        while True:
            sampled_value = float(rng.normal(loc=nominal_value,scale=relative_variation * nominal_value))
            if lower <= sampled_value <= upper:
                realized_values.append(sampled_value)
                break

    return realized_values

class LaminaBuilder:
    """
    Generate the basal lamina system below the main scaffold.

    Solid material layers are represented explicitly as meshes. Air gaps
    are represented by distances between adjacent solid layers and are
    not generated as meshes.
    """
        
    @staticmethod
    def build(
        structure: ButterflyStructure,
    )-> ButterflyStructure:
        params = structure.parameters

        if not params.multilayer_enabled:
            return structure

        if not params.material_layers_um:
            raise ValueError("At least one material layer is required when multilayer_enabled is True")

        expected_gap_count = max(0, len(params.material_layers_um) - 1)

        if len(params.air_layers_um) != expected_gap_count:
            raise ValueError("The lamina system requires exactly one internal air gap between neighboring material" 
            f"Expected {expected_gap_count} gaps, got {len(params.air_layers_um)}.")
        
        lamina_seed = None if params.random_seed is None else params.random_seed + 2

        rng = np.random.default_rng(lamina_seed)

        realized_material_layers = (_sample_positive_values(params.material_layers_um, relative_variation=params.material_layer_variation, rng=rng))
        realized_air_gaps = _sample_positive_values(params.air_layers_um, relative_variation=params.air_gap_variation, rng=rng) 

        layer_meshes: list[trimesh.Trimesh] = []
        layer_bottoms: list[float] = []
        layer_tops: list[float] = []
        #The top of the uppermost lamina is seperated below z = 0 by vertical_gap_um. The stack is built downward.
        current_top_z = -float(params.vertical_gap_um)

        for index, thickness in enumerate(realized_material_layers):
            top_z = current_top_z
            thickness = float(thickness)
            bottom_z = top_z - thickness
            center_z = 0.5 * (current_top_z + bottom_z)
            layer = trimesh.creation.box(
                extents=[
                    float(params.Lx_um),
                    float(params.Ly_um),
                    thickness,
                ]
            )       

            layer.apply_translation([0.5 * params.Lx_um, 0.5 * params.Ly_um, center_z])
            layer.process(validate=True)
            layer.fix_normals()

            layer_meshes.append(layer)
            layer_bottoms.append(bottom_z)
            layer_tops.append(top_z)

            if index < len(realized_air_gaps):
                current_top_z = bottom_z - realized_air_gaps[index]
            else:
                current_top_z = bottom_z

        if not layer_meshes:
            raise RuntimeError("No lamina meshes were generated.")
        
        combined_mesh = trimesh.util.concatenate(layer_meshes)
        combined_mesh.process(validate=True)

        combined_mesh.fix_normals()

        structure.laminae = LaminaSystem(
            material_layer_thickness_um=realized_material_layers,
            air_gap_thickness_um=realized_air_gaps,
            layer_bottom_z_um=layer_bottoms,
            layer_top_z_um=layer_tops,
            separation_from_scaffold_um=float(params.vertical_gap_um),
            layer_meshes=layer_meshes,
            combined_mesh=combined_mesh,
        )

        structure.lamina_mesh = combined_mesh

        return structure