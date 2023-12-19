"""Subdivision operations for DLFL Meshes."""
from typing import Tuple, cast

from pytopmod.core import geometry
from pytopmod.core.dlfl import mesh as dlfl_mesh
from pytopmod.core.dlfl import operators
from pytopmod.core.face import FaceKey
from pytopmod.core.geometry import Point3D
from pytopmod.core.vertex import VertexKey


def subdivide_edge(
    mesh: dlfl_mesh.Mesh,
    vertex_1_key: VertexKey,
    face_1_key: FaceKey,
    vertex_2_key: VertexKey,
    face_2_key: FaceKey,
) -> Tuple[VertexKey, Tuple[FaceKey, FaceKey]]:
    """Subdivides an edge at its midpoint.

    Returns the vertex created at the midpoint and the new faces.
    """
    # Delete the old edge.
    deletion_face_keys = operators.delete_edge(
        mesh, vertex_1_key, face_1_key, vertex_2_key, face_2_key
    )

    # Create a point-sphere at the old edge's midpoint.
    new_vertex_key, new_face_key = operators.create_point_sphere(
        mesh,
        cast(
            Point3D,
            geometry.midpoint(
                mesh.vertex_coordinates[vertex_1_key],
                mesh.vertex_coordinates[vertex_2_key],
            ),
        ),
    )

    # Insert an edge from the first vertex to the midpoint.
    insertion_1_face_keys = operators.insert_edge(
        mesh, vertex_1_key, deletion_face_keys[0], new_vertex_key, new_face_key
    )

    # Insert an edge from the midpoint to the second vertex.
    insertion_2_face_keys = operators.insert_edge(
        mesh,
        new_vertex_key,
        insertion_1_face_keys[0],
        vertex_2_key,
        insertion_1_face_keys[1],
    )

    return (new_vertex_key, insertion_2_face_keys)


def triangulate_face(
    mesh: dlfl_mesh.Mesh, face_key: FaceKey
) -> Tuple[VertexKey, set[FaceKey]]:
    """Performs a triangular subdivision of a face from its centroid.

    Returns the vertex created as the face's centroid and the set of new faces.
    """
    result_face_keys: set[FaceKey] = set()
    face_vertex_keys = mesh.face_vertices[face_key]

    # Create a point sphere at the centroid of the face.
    centroid_vertex, centroid_face = operators.create_point_sphere(
        mesh,
        cast(
            Tuple[float, float, float],
            geometry.centroid(
                mesh.vertex_coordinates[vertex_key] for vertex_key in face_vertex_keys
            ),
        ),
    )

    # Insert an edge between a vertex picked from the face and the centroid.
    insert_face_key, _ = operators.insert_edge(
        mesh, face_vertex_keys[0], face_key, centroid_vertex, centroid_face
    )

    insert_face_keys = []
    # Insert an edge between each remaining vertex in the face and the centroid.
    for vertex_key in face_vertex_keys[1:]:
        insert_face_keys = list(
            operators.insert_edge(
                mesh, vertex_key, insert_face_key, centroid_vertex, insert_face_key
            )
        )
        # Pick the face with the most vertices for the next insertion.
        if len(mesh.face_vertices[insert_face_keys[0]]) > len(
            mesh.face_vertices[insert_face_keys[1]]
        ):
            insert_face_key = insert_face_keys[0]
            result_face_keys.add(insert_face_keys[1])
        else:
            insert_face_key = insert_face_keys[1]
            result_face_keys.add(insert_face_keys[0])

    result_face_keys.update(insert_face_keys)

    return (centroid_vertex, result_face_keys)
