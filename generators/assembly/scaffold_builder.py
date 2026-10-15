from __future__ import annotations

import trimesh
from core.structures import ButterflyStructure

class ScaffoldBuilder:
    @staticmethod
    def build(
        structure: ButterflyStructure
    ) -> ButterflyStructure:

        if structure.network_mesh is None:
            raise ValueError("No network mesh available")
        if structure.ridge_mesh is None:
            structure.scaffold_mesh = structure.network_mesh.copy()
            return structure

        try: 
            scaffold = trimesh.boolean.union([structure.network_mesh, structure.ridge_mesh], engine="manifold")
            if scaffold is None:
                raise RuntimeError("Boolean union returned no mesh")
        except Exception as exc:
            raise RuntimeError(
                "Could not create a continous scaffold mesh. Keep the component meshes for diagnostics, " \
                "but do not yet use their overlapping concatenation as production simulation geometry."
           ) from exc

        scaffold.process(validate=True)
        scaffold.fix_normals()

        structure.scaffold_mesh = scaffold
        return structure
    