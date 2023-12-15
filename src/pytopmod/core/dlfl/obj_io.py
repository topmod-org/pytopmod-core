"""Conversion functions between OBJ format and DLFL representation."""
from typing import cast

from pytopmod.core.dlfl.mesh import DLFLMesh
from pytopmod.core.dlfl.operations import construction
from pytopmod.core.geometry import Point3D
from pytopmod.core.vertex import VertexKey


def mesh_to_obj(mesh: DLFLMesh) -> str:
    """Converts a DLFLMesh to OBJ format."""
    vertex_index_map: dict[VertexKey, int] = {}

    obj_vertices: list[str] = []
    for index, vertex in enumerate(mesh.vertices):
        vertex_index_map[vertex] = index
        coordinates = (str(coord) for coord in mesh.vertex_coordinates[vertex])
        obj_vertices.append(f'v {" ".join(coordinates)}')

    obj_faces: list[str] = []
    for face in mesh.faces:
        indices = (
            str(vertex_index_map[vertex] + 1) for vertex in mesh.face_vertices[face]
        )
        obj_faces.append(f'f {" ".join(indices)}')

    return "\n".join(obj_vertices) + "\n" + "\n".join(obj_faces)


def obj_to_mesh(obj: str) -> DLFLMesh:
    points: list[Point3D] = []
    faces: list[list[int]] = []

    for line in obj.split("\n"):
        if line.startswith("v") and line[1].isspace():
            points.append(
                cast(
                    Point3D, tuple(float(coordinate) for coordinate in line[1:].split())
                )
            )
        if line.startswith("f") and line[1].isspace():
            faces.append([int(index) - 1 for index in line[1:].split()])

    return construction.construct_mesh(points, faces)
