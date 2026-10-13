from core.structures import (StructureParameters, ButterflyStructure)
from generators.hyperuniform.builder import (HyperuniformBuilder)
from generators.network_footprints.builder import NetworkFootprintBuilder
from generators.network_mesh.builder import NetworkMeshBuilder
from visualization.network_plot import plot_network
from visualization.footprint_plot import plot_footprint

params = StructureParameters()

structure = ButterflyStructure(
    parameters=params
)
structure = HyperuniformBuilder.generate_seed_points(
    structure
)

structure = HyperuniformBuilder.relax_points(structure)

structure = HyperuniformBuilder.build_network(structure)
structure = NetworkFootprintBuilder.build(
    structure,
    width=params.strut_width_um,
)
footprint = structure.network_footprint
domain_area = (structure.parameters.Lx_um * structure.parameters.Ly_um)

structure = NetworkMeshBuilder.build(structure)
structure.network_mesh.show()

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
plot_network(structure)
plot_footprint(structure)


