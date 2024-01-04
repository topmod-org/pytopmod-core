"""Conversion functions between OBJ format and DLFL representation."""
from pytopmod.core.dlfl import mesh as dlfl_mesh
from pytopmod.core.vertex import VertexKey


def mesh_to_obj(mesh: dlfl_mesh.Mesh) -> str:
    """Converts a dlfl_mesh.Mesh to OBJ format."""
    vertex_index_map: dict[VertexKey, int] = {}

    obj_vertices: list[str] = []
    for index, vertex_key in enumerate(mesh.vertex_keys):
        vertex_index_map[vertex_key] = index
        coordinates = (str(coord) for coord in mesh.vertex_coordinates[vertex_key])
        obj_vertices.append(f'v {" ".join(coordinates)}')

    obj_faces: list[str] = []
    for face_key in mesh.face_keys:
        indices = (
            str(vertex_index_map[vertex_key] + 1)
            for vertex_key in mesh.face_vertices[face_key]
        )
        obj_faces.append(f'f {" ".join(indices)}')

    return "\n".join(obj_vertices) + "\n" + "\n".join(obj_faces)


def obj_to_mesh(obj: str) -> dlfl_mesh.Mesh:
    raise NotImplementedError()
