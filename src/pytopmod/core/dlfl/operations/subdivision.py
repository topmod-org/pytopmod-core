"""Subdivision operations for DLFL Meshes."""
from typing import Tuple, cast

from pytopmod.core import geometry
from pytopmod.core.dlfl import mesh as dlfl_mesh
from pytopmod.core.dlfl import operators
from pytopmod.core.face import FaceKey
from pytopmod.core.geometry import Point3D
from pytopmod.core.vertex import VertexKey
from pytopmod.core import corner


def subdivide_edge(
    mesh: dlfl_mesh.Mesh, corner_1: corner.Corner, corner_2: corner.Corner
) -> Tuple[VertexKey, Tuple[FaceKey, FaceKey]]:
    """Subdivides an edge at its midpoint.

    Returns the vertex created at the midpoint and the new faces.
    """
    # Delete the old edge.
    deletion_face_1_key, _ = operators.delete_edge(mesh, corner_1, corner_2)

    # Create a point-sphere at the old edge's midpoint.
    new_corner = operators.create_point_sphere(
        mesh,
        cast(
            Point3D,
            geometry.midpoint(
                mesh.vertex_coordinates[corner_1.vertex_key],
                mesh.vertex_coordinates[corner_2.vertex_key],
            ),
        ),
    )

    # Insert an edge from the first vertex to the midpoint.
    insertion_1_face_keys = operators.insert_edge(
        mesh,
        operators.corner_from_face_vertex(
            mesh, deletion_face_1_key, corner_1.vertex_key
        ),
        new_corner,
    )

    # Insert an edge from the midpoint to the second vertex.
    insertion_2_face_keys = operators.insert_edge(
        mesh,
        operators.corner_from_face_vertex(
            mesh, insertion_1_face_keys[0], new_corner.vertex_key
        ),
        operators.corner_from_face_vertex(
            mesh, insertion_1_face_keys[1], corner_2.vertex_key
        ),
    )

    return (new_corner.vertex_key, insertion_2_face_keys)


def triangulate_face(
    mesh: dlfl_mesh.Mesh, face_key: FaceKey
) -> Tuple[VertexKey, set[FaceKey]]:
    """Performs a triangular subdivision of a face from its centroid.

    Returns the vertex created as the face's centroid and the set of new faces.
    """
    result_face_keys: set[FaceKey] = set()
    face_vertex_keys = mesh.face_vertices[face_key]

    # Create a point sphere at the centroid of the face.
    centroid_corner = operators.create_point_sphere(
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
        mesh,
        operators.corner_from_face_vertex(mesh, face_key, face_vertex_keys[0]),
        centroid_corner,
    )

    insert_face_keys = []
    # Insert an edge between each remaining vertex in the face and the centroid.
    for vertex_key in face_vertex_keys[1:]:
        insert_face_keys = list(
            operators.insert_edge(
                mesh,
                operators.corner_from_face_vertex(mesh, insert_face_key, vertex_key),
                operators.corner_from_face_vertex(
                    mesh, insert_face_key, centroid_corner.vertex_key
                ),
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

    return (centroid_corner.vertex_key, result_face_keys)
