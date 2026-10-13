from __future__ import annotations

from dataclasses import dataclass, field

from .enums import (
    StructureType,
    RidgeMode,
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
    ridge_mode: RidgeMode = RidgeMode.FIXED_SPACING

    ridge_height_um: float = 0.84
    ridge_width_um: float = 0.30
    ridge_spacing_um: float = 1.0

    target_openings_between_ridges: int = 2

    #Multilayer
    multilayer_enabled: bool = True

    material_layers_um: list[float] = field(
        default_factory=lambda: [0.12, 0.12, 0.12]
    )
    air_layers_um: list[float] = field(
        default_factory=lambda: [0.06, 0.06, 0.06]
    )

    vertical_gap_um: float = 0.645

    add_bottom_cap: bool = True

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

        #Hyperuniform network slab validation
        if self.network_enabled:

            if self.network_points <=0:
                        raise ValueError(f"network_points must be positive, got {self.network_points} ")

            if self.slab_thickness_um <= 0:
                        raise ValueError(f"slab_thickness must be positive, got {self.slab_thickness_um}")

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

        #Multilayer validation
        if self.multilayer_enabled:

            if(len(self.air_layers_um) > len(self.material_layers_um)):
                   raise ValueError("There cannot be more air layers than material layers.")

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

        #Consistency check 
        if self.network_enabled and self.ridges_enabled:
               if self.ridge_height_um > 5 * self.slab_thickness_um:
                      raise ValueError("ridge_height_um is unrealistically large compared to slab_thickness_um.")


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