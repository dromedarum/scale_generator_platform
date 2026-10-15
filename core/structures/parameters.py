from __future__ import annotations

from dataclasses import dataclass, field

from .enums import (
    StructureType,
    RidgeMode,
    RidgeRootMode,
)
import numpy as np

@dataclass
class StructureParameters:
    """
    Scientific description of a butterfly photonic structure.
    This class is intended to be the single source for truth for all geometry-generation workflows.
    It contains only parameters and validation logic, not geometry-generation code.
    """
    structure_type: StructureType = StructureType.HYPERUNIFORM
    #random seeding
    random_seed: int | None = 42
    lloyd_iterations: int = 100
    #Domain
    Lx_um: float = 7.0
    Ly_um: float = 7.0

    #Network
    network_enabled: bool = True
    network_points: int = 200
    slab_thickness_um: float = 2.093
    strut_width_um: float = 0.01
    

    #Ridges
    ridges_enabled: bool = False
    ridge_mode: RidgeMode = RidgeMode.NETWORK_DERIVED

    ridge_height_um: float = 0.84
    ridge_width_um: float = 0.30
    ridge_spacing_um: float = 1.0

    target_openings_between_ridges: float = 2.0
    ridge_placement_variation: float = 0.3

    ridge_root_mode: RidgeRootMode = (RidgeRootMode.RECTANGULAR_WALL)
    ridge_embed_depth_um: float = 2.0
    ridge_root_width_um: float = 0.30

    #Basal laminae / Multilayer
    multilayer_enabled: bool = True

    material_layers_um: list[float] = field(
        default_factory=lambda: [0.12, 0.12, 0.12]
    )
    material_layer_variation: float = 0.0
    air_layers_um: list[float] = field(
        default_factory=lambda: [0.06, 0.06]
    )
    air_gap_variation: float = 0.0
    vertical_gap_um: float = 0.645

    include_continuous_basal_layer: bool = True

    #Initialization

    def __post_init__(self) -> None:
           self.validate()

    def validate(self) -> None: 
        """
        Validate physical consistency of structure parameters.
        
        Raises ValueError if one or more parameters are physically invalid.
        """

        #Domain validation
        if self.Lx_um <= 0:
            raise ValueError(f"Lx_um must be positive, got {self.Lx_um}")

        if self.Ly_um <= 0:
                    raise ValueError(f"Ly_um must be positive, got {self.Ly_um}")

        if self.random_seed is not None and self.random_seed < 0:
              raise ValueError("random_seed must be non-negative or None,"
              f" got {self.random_seed}")

        #Hyperuniform network slab validation
        if self.lloyd_iterations < 0:
            raise ValueError(f"lloyd_iterations must be greater than or equal to zero, got {self.lloyd_iterations}")
        
        if self.network_enabled:

            if self.network_points <=0:
                        raise ValueError(f"network_points must be positive, got {self.network_points} ")

            if self.slab_thickness_um <= 0:
                        raise ValueError(f"slab_thickness must be positive, got {self.slab_thickness_um}")
            if self.strut_width_um <= 0:
                  raise ValueError(f"strut_width_um must be positive, fot {self.strut_width_um}")

            if self.ridge_placement_variation < 0:
                  raise ValueError(f"ridge_placement_variation must be greater than or equal to zero, got {self.ridge_placement_variation}")

        #structure_type validation
        supported = {
               StructureType.HYPERUNIFORM,
        }
        if self.structure_type not in supported:
               raise ValueError(f"Unsupported structure_type: {self.structure_type}, supported structure_types are {supported}")

        #Ridge validation
        if self.ridges_enabled:

            if self.ridge_width_um <= 0:
                  raise ValueError(f"ridge_width_um must be positive, got {self.ridge_width_um}")
            if self.ridge_height_um <= 0:
                    raise ValueError(f"ridge_height_um must be positive, got {self.ridge_height_um}")
            if self.ridge_mode == RidgeMode.FIXED_SPACING and self.ridge_spacing_um <= 0:
                      raise ValueError(f"ridge_spacing_um must be positive, got {self.ridge_spacing_um}")
            #sanity check
            if self.ridge_width_um >= self.ridge_spacing_um:
                   raise ValueError("ridge_width_um must be smaller than ridge_spacing_um.")
            if self.ridge_mode == RidgeMode.NETWORK_DERIVED and self.target_openings_between_ridges < 1:
                   raise ValueError("target_openings_between_ridges must be >= 1.")
            if self.ridge_embed_depth_um < 0:
                  raise ValueError(f"ridge_embed_depth_um must be greater than or equal to zero, got {self.ridge_embed_depth_um}.")
            if self.ridge_root_width_um <= 0:
                  raise ValueError(f"ridge_root_width_um must be positive, got {self.ridge_root_width_um}.")
            
        #Basal laminae / multilayer system validation
        if self.multilayer_enabled:
            expected_gap_count = max(0, len(self.material_layers_um) - 1)


            if len(self.air_layers_um) != expected_gap_count:
                   raise ValueError("The current lamina model requires exactly on internal air gap between adjacent material layers."
                   f"Expected {expected_gap_count} air gaps for {len(self.material_layers_um)} material layers, got {len(self.air_layers_um)}.")

            if not self.material_layers_um:
                      raise ValueError("At least one material layer is required.")

            for i, thickness in enumerate(self.material_layers_um):
                      if thickness <= 0:
                             raise ValueError(f"material_layers_um[{i}] must be positive, got {thickness}")

            for i, gap in enumerate(self.air_layers_um):
                      if gap < 0:
                             raise ValueError(f"air_layers_um[{i}] must be >= 0, got {gap}")
            if self.vertical_gap_um < 0:
                   raise ValueError(f"vertical_gap_um must be >= 0, got {self.vertical_gap_um}")
            
            if self.material_layer_variation < 0:
                  raise ValueError(f"material_layer_variation must be greater than or equal to zero, got {self.material_layer_variation}")

            if self.air_gap_variation < 0:
                  raise ValueError(f"air_gap_variation must be greater than or equal to zero, got {self.air_gap_variation}")

            

        #Consistency check 
        if self.network_enabled and self.ridges_enabled:
               if self.ridge_height_um > 5 * self.slab_thickness_um:
                      raise ValueError("ridge_height_um is unrealistically large compared to slab_thickness_um.")
               if self.network_enabled and self.ridge_embed_depth_um > self.slab_thickness_um:
                     raise ValueError("ridge_embed_depth_um cannot exceed slab_thickness_um")

    def scientific_warnings(self) -> list[str]:
          warnings: list[str] = []

          if self.network_enabled and self.ridges_enabled and self.ridge_embed_fraction > 0.8:
                warnings.append("The ridge root occupies more than 80% of the network slab thickness. "
                "This models a deep, nearily full-depth supporting wall and should be validated")

          return warnings

    #Derived Properties

    @property
    def total_material_thickness_um(self) -> float:
        """
        Total thickess of all material layers.
        """
        return float(sum(self.material_layers_um))

    @property
    def total_air_thickness_um(self) -> float:
        """
        Total thickness of all air gaps.
        """
        return float(sum(self.air_layers_um))

    @property
    def multilayer_height_um(self) -> float:
        """
        Total multilayer stack height.
        """
        return float(self.total_air_thickness_um + self.total_material_thickness_um)

    @property
    def multilayer_period_um(self) -> float:
        """
        Mean multilayer period thickness
        """
        if not self.material_layers_um:
               return 0.0

        n_periods = min(len(self.material_layers_um), len(self.air_layers_um))

        if n_periods == 0:
               return float(np.mean(self.material_layers_um))

        periods=[]

        for i in range(n_periods):
               periods.append(self.material_layers_um[i] + self.air_layers_um[i])

        return float(sum(periods) / len(periods))        

    @property
    def total_structure_height_um(self) -> float:
        height = 0.0
        if self.network_enabled:
            height += self.slab_thickness_um 
        if self.ridges_enabled:
            height += self.ridge_height_um
        if self.multilayer_enabled:
            height += (self.vertical_gap_um + self.multilayer_height_um)

        return height 

    @property
    def footprint_area_um2(self) -> float: 
        return self.Lx_um * self.Ly_um

    @property
    def total_ridge_profile_height_um(self) -> float:
        return self.ridge_height_um + self.ridge_embed_depth_um

    @property
    def ridge_embed_fraction(self) -> float:
        """
        Fraction of network slab thickness occupied by the ridge root.
        """
        if not self.network_enabled:
            return 0.0

        if self.slab_thickness_um <= 0:
            return 0.0

        return float(self.ridge_embed_depth_um / self.slab_thickness_um)
        