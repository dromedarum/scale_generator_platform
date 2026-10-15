from core.structures import StructureParameters, ButterflyStructure
from generators.ridges.builder import RidgeBuilder
from visualization.ridge_plot import plot_ridges

params = StructureParameters(ridges_enabled=True)
structure = ButterflyStructure(parameters=params)
structure = RidgeBuilder.generate(structure)


plot_ridges(structure)

print(len(structure.ridges.centerlines))
print(structure.ridges.centerlines[0])