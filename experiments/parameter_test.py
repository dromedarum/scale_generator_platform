from core.structures import (
    StructureParameters,
    RidgeMode,
)
from pathlib import Path

def print_header(title: str):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


# ==========================================================
# Test 1: Default parameters
# ==========================================================

print_header("TEST 1 - DEFAULT PARAMETERS")

params = StructureParameters()

print(params)

print("total_material_thickness_um =", params.total_material_thickness_um)
print("total_air_thickness_um      =", params.total_air_thickness_um)
print("multilayer_height_um        =", params.multilayer_height_um)
print("multilayer_period_um        =", params.multilayer_period_um)
print("total_structure_height_um   =", params.total_structure_height_um)


# ==========================================================
# Test 2: Invalid slab thickness
# ==========================================================

print_header("TEST 2 - INVALID SLAB THICKNESS")

try:
    bad = StructureParameters(
        slab_thickness_um=-1.0
    )

    print("ERROR: validation should have failed")

except ValueError as exc:
    print("PASS")
    print(exc)


# ==========================================================
# Test 3: Invalid ridge spacing
# ==========================================================

print_header("TEST 3 - INVALID RIDGE SPACING")

try:
    bad = StructureParameters(
        ridges_enabled=True,
        ridge_mode=RidgeMode.FIXED_SPACING,
        ridge_spacing_um=0.0,
    )

    print("ERROR: validation should have failed")

except ValueError as exc:
    print("PASS")
    print(exc)


# ==========================================================
# Test 4: Ridge wider than spacing
# ==========================================================

print_header("TEST 4 - RIDGE WIDTH > SPACING")

try:
    bad = StructureParameters(
        ridges_enabled=True,
        ridge_width_um=2.0,
        ridge_spacing_um=1.0,
    )

    print("ERROR: validation should have failed")

except ValueError as exc:
    print("PASS")
    print(exc)


# ==========================================================
# Test 5: Negative multilayer thickness
# ==========================================================

print_header("TEST 5 - NEGATIVE MULTILAYER THICKNESS")

try:
    bad = StructureParameters(
        material_layers_um=[0.12, -0.05, 0.12]
    )

    print("ERROR: validation should have failed")

except ValueError as exc:
    print("PASS")
    print(exc)


# ==========================================================
# Test 6: Custom realistic structure
# ==========================================================

print_header("TEST 6 - CUSTOM STRUCTURE")

structure = StructureParameters(
    network_enabled=True,
    ridges_enabled=True,
    multilayer_enabled=True,
    network_points=300,
    ridge_spacing_um=1.2,
    ridge_width_um=0.25,
    ridge_height_um=0.8,
)

print(structure)

print("total_material_thickness_um =", structure.total_material_thickness_um)
print("total_air_thickness_um      =", structure.total_air_thickness_um)
print("multilayer_height_um        =", structure.multilayer_height_um)
print("multilayer_period_um        =", structure.multilayer_period_um)
print("total_structure_height_um   =", structure.total_structure_height_um)

# ==========================================================
# Test 7: Serialization roundtrip
# ==========================================================

from core.structures import (save_structure_parameters, load_structure_parameters)

print_header("TEST 7 - SERIALIZATION")
params = StructureParameters()

save_structure_parameters(params, "test_params.json")
loaded = load_structure_parameters("test_params.json")

print("Loaded object:")
print(loaded)

print()
print("Objects identical:")
print(params == loaded)

print()
print("All parameter tests completed.")

test_path = Path("test_params.json")
if test_path.exists():
    test_path.unlink()