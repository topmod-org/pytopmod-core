"""Conversion functions between OBJ format and DCEL representation."""
from typing import Tuple

from pytopmod.core.dcel import mesh as dcel_mesh
from pytopmod.core.dcel import operators
from pytopmod.core.vertex import VertexKey


def mesh_to_obj(mesh: dcel_mesh.Mesh) -> str:
    """Converts a dcel_mesh.Mesh to OBJ format."""
    vertex_map: dict[VertexKey, int] = {}

    obj_vertices: list[str] = []
    for index, vertex_key in enumerate(mesh.vertex_keys):
        vertex_map[vertex_key] = index
        coordinates = (str(coord) for coord in mesh.vertex_coordinates[vertex_key])
        obj_vertices.append(f'v {" ".join(coordinates)}')

    obj_faces: list[str] = []
    for face_key in mesh.face_keys:
        edge_keys = [
            corner.edge_1_key for corner in operators.face_trace(mesh, face_key)
        ]
        vertex_key_pairs: list[Tuple[VertexKey, VertexKey]] = []

        for i in range(len(edge_keys) - 1):
            edge_node_1 = mesh.edge_nodes[edge_keys[i]]
            edge_node_2 = mesh.edge_nodes[edge_keys[i + 1]]
            vertex_key_pairs.append(
                (edge_node_1.vertex_1_key, edge_node_1.vertex_2_key)
                if edge_node_1.vertex_2_key
                in (edge_node_2.vertex_1_key, edge_node_2.vertex_2_key)
                else (edge_node_1.vertex_2_key, edge_node_1.vertex_1_key)
            )

        vertex_keys = [pair[0] for pair in vertex_key_pairs] + [
            vertex_key_pairs[-1][-1]
        ]

        indices = list(str(vertex_map[vertex_key] + 1) for vertex_key in vertex_keys)
        obj_faces.append(f'f {" ".join(indices)}')

    return "\n".join(obj_vertices) + "\n" + "\n".join(obj_faces)
