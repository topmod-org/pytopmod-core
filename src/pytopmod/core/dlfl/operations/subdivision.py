"""Subdivision operations for DLFL Meshes."""
from typing import Tuple, cast

from pytopmod.core import geometry
from pytopmod.core.dlfl import operators
from pytopmod.core.dlfl.mesh import DLFLMesh
from pytopmod.core.face import FaceKey
from pytopmod.core.geometry import Point3D
from pytopmod.core.vertex import VertexKey


def subdivide_edge(
    mesh: DLFLMesh,
    vertex_1: VertexKey,
    face_1: FaceKey,
    vertex_2: VertexKey,
    face_2: FaceKey,
) -> Tuple[VertexKey, Tuple[FaceKey, FaceKey]]:
    """Subdivides an edge at its midpoint.

    Returns the vertex created at the midpoint and the new faces.
    """
    # Delete the old edge.
    deletion_faces = operators.delete_edge(mesh, vertex_1, face_1, vertex_2, face_2)

    # Create a point-sphere at the old edge's midpoint.
    new_vertex, new_face = operators.create_point_sphere(
        mesh,
        cast(
            Point3D,
            geometry.midpoint(
                mesh.vertex_coordinates[vertex_1], mesh.vertex_coordinates[vertex_2]
            ),
        ),
    )

    # Insert an edge from the first vertex to the midpoint.
    insertion_1_faces = operators.insert_edge(
        mesh, vertex_1, deletion_faces[0], new_vertex, new_face
    )

    # Insert an edge from the midpoint to the second vertex.
    insertion_2_faces = operators.insert_edge(
        mesh, new_vertex, insertion_1_faces[0], vertex_2, insertion_1_faces[1]
    )

    return (new_vertex, insertion_2_faces)


def triangulate_face(mesh: DLFLMesh, face: FaceKey) -> Tuple[VertexKey, set[FaceKey]]:
    """Performs a triangular subdivision of a face from its centroid.

    Returns the vertex created as the face's centroid and the set of new faces.
    """
    result_faces: set[FaceKey] = set()
    face_vertices = mesh.face_vertices[face]

    # Create a point sphere at the centroid of the face.
    centroid_vertex, centroid_face = operators.create_point_sphere(
        mesh,
        cast(
            Tuple[float, float, float],
            geometry.centroid(
                mesh.vertex_coordinates[vertex] for vertex in face_vertices
            ),
        ),
    )

    # Insert an edge between a vertex picked from the face and the centroid.
    insert_face, _ = operators.insert_edge(
        mesh, face_vertices[0], face, centroid_vertex, centroid_face
    )

    insert_faces = []
    # Insert an edge between each remaining vertex in the face and the centroid.
    for vertex in face_vertices[1:]:
        insert_faces = list(
            operators.insert_edge(
                mesh, vertex, insert_face, centroid_vertex, insert_face
            )
        )
        # Pick the face with the most vertices for the next insertion.
        if len(mesh.face_vertices[insert_faces[0]]) > len(
            mesh.face_vertices[insert_faces[1]]
        ):
            insert_face = insert_faces[0]
            result_faces.add(insert_faces[1])
        else:
            insert_face = insert_faces[1]
            result_faces.add(insert_faces[0])

    result_faces.update(insert_faces)

    return (centroid_vertex, result_faces)
