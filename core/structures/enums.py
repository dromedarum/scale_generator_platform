from enum import Enum


class StructureType(str, Enum):
    HYPERUNIFORM = "hyperuniform"

class RidgeMode(str, Enum):
    NONE = "none"
    FIXED_SPACING = "fixed_spacing"
    NETWORK_DERIVED = "network_derived"

class RidgeRootMode(str, Enum):
    NONE = "none"
    RECTANGULAR_WALL ="rectangular_wall"

