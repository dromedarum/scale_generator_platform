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

class GeometryOrigin(str, Enum):
    GENERATED = "generated"
    IMPORTED = "imported"

class LengthUnit(str, Enum):
    MICROMETER = "um",
    NANOMETER = "nm",
    MILIMETER = "mm",
    METER = "m"

class ImportTransformMode(str, Enum):
    PRESERVE = "preserve"
    NORMALIZE_ASSEMBLY = "normalize_assembly"

class ComponentRole(str, Enum):
    SCAFFOLD = "scaffold"
    LAMINA = "lamina"
    SUBSTRATE = "substrate"
    IMPORTED = "imported"

