from dataclasses import asdict

import matplotlib.pyplot as plt

from core.structures import StructureParameters
from core.structures.enums import RidgeMode
from core.structures.validation import validate_structure_geometry

from generators.pipeline import generate_structure

from visualization.xz_cross_section import plot_xz_cross_section

params = StructureParameters(
    ridges_enabled=True,
    ridge_mode=RidgeMode.NETWORK_DERIVED,
    ridge_placement_variation=0.0
    )

structure = generate_structure(params)
structure.scaffold_mesh.show()
report = validate_structure_geometry(structure)

print(asdict(report))
plot_xz_cross_section(structure,y_um=params.Ly_um / 2.0,show_components=False,show_scaffold=True)
plt.show()


"""
#ridge diagnostics
voids = get_void_polygons(structure.network_footprint, structure.parameters.Lx_um, structure.parameters.Ly_um)
widths = opening_widths_x(voids)
centers = opening_centers(voids)
ridge_footprint = structure.ridge_footprint
expected_ridge_area = (len(structure.ridges.centerlines) * structure.ridges.width_um * params.Ly_um)
network_top_z = structure.network_mesh.bounds[1, 2]
expected_root_bottom_z = network_top_z - params.ridge_embed_depth_um
ridge_bottom_z = structure.ridge_mesh.bounds[0, 2]
expected_ridge_top_z = network_top_z + params.ridge_height_um
ridge_top_z = structure.ridge_mesh.bounds[1, 2]
measured_embed_depth = (network_top_z - ridge_bottom_z)
measured_visible_height = ( ridge_top_z - network_top_z)
network_bounds = structure.network_mesh.bounds
ridge_bounds = structure.ridge_mesh.bounds

np.testing.assert_allclose(ridge_bottom_z, expected_ridge_top_z, atol=1e-6)
np.testing.assert_allclose(ridge_top_z, expected_ridge_top_z, atol=1e-6)
print("PASS: ridge root bottom and exposed apex match the requested morphology.")

print(params.ridge_mode)
print("number of voids:", len(voids))
print("mean width:", widths.mean())
print("std width:", widths.std())
print("Number of Ridges", len(structure.ridges.centerlines))
print("ridge_placement_variation", params.ridge_placement_variation)
print("Ridge spacing std:", structure.ridges.spacing_std_um)
print("ridge_footprint type", type(structure.ridge_footprint))
print("number of opening centers:",len(centers))
print("ridge_footprint type:", type(ridge_footprint))
print("ride_footprint area:", ridge_footprint.area)
print("expected uncliipped ridge area:", expected_ridge_area)
print("ridge area ratio:", ridge_footprint.area / expected_ridge_area)
print("ridge_mesh type:", type(structure.ridge_mesh))
print("ridge mesh vertices:", len(structure.ridge_mesh.vertices))
print("ridge mesh faces:", len(structure.ridge_mesh.faces))
print("network top z:", network_top_z)
print("ridge bottom z:", ridge_bottom_z)
print("ridge top z:", ridge_top_z)
print("network mesh bounds:", network_bounds)
print("ridge mesh boudns:", ridge_bounds)
print("network x range:", network_bounds[:, 0])
print("ridge x range:", ridge_bounds[:, 0])
print("network y range:", network_bounds[:, 1])
print("ridge y range:", ridge_bounds[:, 1])
print("network z range:", network_bounds[:, 2])
print("ridge z range:",ridge_bounds[:, 2])
print("measured ridge embed depth:",measured_embed_depth)
print("measured visible ridge height:", measured_visible_height)

#Network diagnostics
print("footprint area:", footprint.area)
print("fill fraction:", footprint.area / domain_area)
print("network_mesh type:", type(structure.network_mesh))
print("vertices:", len(structure.network_mesh.vertices))
print("faces:", len(structure.network_mesh.faces))
print("seed_points.shape:")
print(structure.network.seed_points.shape)
print("relaxed_points.shape:")
print(structure.network.relaxed_points.shape)
print("vertices.shape:")
print(structure.network.vertices.shape)
print("number of edges:")
print(len(structure.network.edges))
print("network_footprint structure type")
print(type(structure.network_footprint))

#scaffold diagonstics
print("scaffold mesh type:", type(structure.scaffold_mesh))
print("scaffold watertight:", structure.scaffold_mesh.is_watertight)
print("scaffold volume:", structure.scaffold_mesh.is_volume)
print("scaffold components:", len(structure.scaffold_mesh.split(only_watertight=False)))
"""
""" 
slice_positions_um = [
    0.25 * params.Ly_um,
    0.50 * params.Ly_um,
    0.75 * params.Ly_um,
]

for y_um in slice_positions_um:
    plot_xz_cross_section(
        structure,
        y_um=y_um,
        show_components=True,
        show_scaffold=True,
    )

plt.show()
plot_xz_cross_section(
    structure,
    y_um=params.Ly_um / 2.0,
    show_components=False,
    show_scaffold=True,
)

plt.show() """


#plot_ridge_footprint(structure)
#plot_network(structure)
#plot_footprint(structure)
#plot_openings(structure, centers)
#plot_ridges(structure, centers)
#combined_preview = trimesh.util.concatenate([structure.network_mesh.copy(), structure.ridge_mesh.copy()])
#combined_preview.show()

