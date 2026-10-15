from __future__ import annotations

import numpy as np
import trimesh
from shapely.geometry import Polygon

from core.structures import ButterflyStructure

def triangular_ridge_profile(
        width_um: float,
        visible_height_um: float,
        embed_depth_um: float,
) -> Polygon:
    """
    Create a triangular ridge profile in local x-z coordiantes.
    The nominal network top surface is z=0. The ridge bas is embedded 
    below that surface, while the apex extends above it
    """
    return Polygon([(-width_um / 2.0, -embed_depth_um), (width_um / 2.0, -embed_depth_um), (0.0, visible_height_um)])

def extrude_profile_along_y(
        profile_xz: Polygon,
        length_y_um: float,
) -> trimesh.Trimesh:
    """
    Extrude an x-z profile along the positive y direction.
    """

    vertices_2d, faces_2d = trimesh.creation.triangulate_polygon(profile_xz, engine="earcut")

    mesh = trimesh.creation.extrude_triangulation(vertices_2d, faces_2d, height=length_y_um)

    #extrude_triangulation extrudes along z. Rotate the extrusion direction from +z to +y.
    rotation = trimesh.transformations.rotation_matrix(np.pi / 2.0, [1.0, 0.0, 0.0])
    mesh.apply_transform(rotation)
    mesh.process(validate=True)
    mesh.fix_normals()

    return mesh

def visible_ridge_profile(
        width_um: float,
        height_um: float,
) -> Polygon:
    return Polygon([(-width_um / 2.0, 0.0), (width_um / 2.0, 0.0), (0.0, height_um)])

def ridge_root_profile(
        width_um: float,
        embed_depth: float,
) -> Polygon:
    return Polygon([(-width_um / 2.0, -embed_depth), (width_um / 2.0, -embed_depth), (width_um / 2.0, 0.0), (-width_um / 2.0, 0.0)])

class RidgeMeshBuilder:

    @staticmethod
    def build(
        structure: ButterflyStructure,
    ) -> ButterflyStructure:

        if structure.ridges is None:
            raise ValueError("No RidgeSystem is available.")
        if not structure.ridges.centerlines:
            raise ValueError("The RidgeSystem contains no centerlines.")
        if structure.network_mesh is None:
            raise ValueError("A network mesh is required to position ridge bases.")

        width = float(structure.ridges.width_um)
        height = float(structure.ridges.height_um)
        embed_depth = float(structure.ridges.embed_depth_um or 0.0)

        network_top_z = float(structure.network_mesh.bounds[1, 2])
        cap_profile = visible_ridge_profile(width_um=float(structure.ridges.width_um), height_um=float(structure.ridges.height_um))
        root_profile = ridge_root_profile(
            width_um=float(structure.ridges.root_width_um),
            embed_depth=float(structure.ridges.embed_depth_um or 0.0)
        )

        ridge_meshes = []
        for centerline in structure.ridges.centerlines:
            start = np.asarray(centerline[0], dtype=float)
            end = np.asarray(centerline[-1], dtype=float)

            delta = end - start
            length_y = float(np.linalg.norm(delta))
            if length_y <= 0:
                raise ValueError("A ridge centerline has zero length.")

            #This first implementation assumes y-directed ridges.
            if not np.isclose(delta[0],0.0):
                raise ValueError("The current ridge mesh builder only supports centerlines parallel to the y-axis.")

            cap_mesh = extrude_profile_along_y(cap_profile, length_y_um=length_y)
            root_mesh = extrude_profile_along_y(root_profile, length_y_um=length_y)
            translation = [float(start[0]), float(end[1]), network_top_z]
            cap_mesh.apply_translation(translation)
            root_mesh.apply_translation(translation)
            try:
                ridge_component = trimesh.boolean.union([root_mesh, cap_mesh], engine="manifold")
            except Exception:
                ridge_component = trimesh.util.concatenate([root_mesh, cap_mesh])
            

            ridge_meshes.append(ridge_component)

        structure.ridge_mesh = trimesh.util.concatenate(ridge_meshes)
        structure.ridge_mesh.process(validate=True)
        structure.ridge_mesh.fix_normals()

        return structure
