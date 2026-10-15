from core.structures import ButterflyStructure
from core.structures.ridges import RidgeSystem
from core.structures.enums import RidgeMode
from generators.ridges.openings import get_void_polygons, opening_widths_x, interior_voids
import numpy as np

class RidgeBuilder:

    @staticmethod
    def generate(
        structure: ButterflyStructure,
    ) -> ButterflyStructure:

        params = structure.parameters

        if not params.ridges_enabled:
            return structure
        
        centerlines = []

        #fixed spacing branch
        if params.ridge_mode == RidgeMode.FIXED_SPACING:
            spacing = params.ridge_spacing_um
            x_positions = np.arange(0.0, params.Lx_um + spacing, spacing)

        #network derived branch
        elif params.ridge_mode == RidgeMode.NETWORK_DERIVED:
            voids = get_void_polygons(structure.network_footprint, params.Lx_um, params.Ly_um)
            statistical_voids = interior_voids(voids, params.Lx_um, params.Ly_um)
            if not statistical_voids:
                raise ValueError("No complete interior openings are available for network-derived ridge placement")

            widths = opening_widths_x(statistical_voids)
            mean_opening_width = float(widths.mean())
            target_spacing = (params.target_openings_between_ridges * mean_opening_width)
            variation = params.ridge_placement_variation
            x_positions = [0.0]
            sampled_spacings = []
            n_intervals = max(1, round(params.Lx_um / target_spacing))
            base_seed=params.random_seed
            for _ in range(n_intervals):
                if variation > 0:
                    while True:
                        ridge_seed = None if base_seed is None else base_seed + 1
                        rng = np.random.default_rng(ridge_seed)
                        spacing = rng.normal(loc=target_spacing, scale= variation * target_spacing)
                        if 0.5 * target_spacing <= spacing <= 1.5 * target_spacing : break
                    spacing = max(0.25 * target_spacing, spacing)
                else:
                    spacing = target_spacing
                
                sampled_spacings.append(spacing)

            sampled_spacings = np.asarray(sampled_spacings)
            sampled_mean = np.mean(sampled_spacings)
            correction = target_spacing / sampled_mean
            sampled_spacings *= correction
            for spacing in sampled_spacings:
                x_next = x_positions[-1] + spacing

                if x_next <= params.Lx_um:
                    x_positions.append(x_next)

        #error handling
        else:
            raise ValueError(f"Unsupported ridge mode: {params.ridge_mode}")
        
        for x in x_positions:
            centerline = np.array([[x,0.0], [x, params.Ly_um]])
            centerlines.append(centerline)

        #spacing diagnostics
        local_spacings = np.diff(np.asarray(x_positions))
        mean_spacing = None

        if len(x_positions) > 1:
            local_spacings = np.diff(np.asarray(x_positions))
            mean_spacing = float(np.mean(local_spacings))

        structure.ridges = RidgeSystem(
            centerlines=centerlines,
            local_spacings_um=local_spacings,
            openings_between_ridges=params.target_openings_between_ridges,
            mean_spacing_um=mean_spacing,
            spacing_std_um=float(np.std(local_spacings)),
            width_um=params.ridge_width_um,
            height_um=params.ridge_height_um, 
            embed_depth_um=params.ridge_embed_depth_um,
            root_width_um=params.ridge_root_width_um,
            root_mode=params.ridge_root_mode,
        )

        return structure