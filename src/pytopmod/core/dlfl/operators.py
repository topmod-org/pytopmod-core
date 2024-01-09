"""Manifold-preserving operators on DLFL Meshes."""
from typing import Generator, Tuple

from pytopmod.core import circular_list, corner
from pytopmod.core.dlfl import mesh as dlfl_mesh
from pytopmod.core.edge import EdgeKey
from pytopmod.core.face import FaceKey
from pytopmod.core.geometry import Point3D
from pytopmod.core.vertex import VertexKey


def corner_from_face_vertex(
    mesh: dlfl_mesh.Mesh, face_key: FaceKey, vertex_key: VertexKey
) -> corner.Corner:
    """Returns the corner defined by a face and a vertex."""
    previous_vertex_key = circular_list.previous_item(
        mesh.face_vertices[face_key], vertex_key
    )
    next_vertex_key = circular_list.previous_item(
        mesh.face_vertices[face_key], vertex_key
    )
    return corner.Corner(
        vertex_key=vertex_key,
        face_key=face_key,
        edge_1_key=EdgeKey(frozenset((vertex_key, next_vertex_key))),
        edge_2_key=EdgeKey(frozenset((previous_vertex_key, vertex_key))),
    )


def face_edges(
    mesh: dlfl_mesh.Mesh, face_key: FaceKey
) -> Generator[EdgeKey, None, None]:
    """Returns a generator over the edges of a face."""
    return (
        frozenset(pair) for pair in circular_list.pairs(mesh.face_vertices[face_key])
    )


def corner_from_edge_vertex(
    mesh: dlfl_mesh.Mesh, edge_key: EdgeKey, vertex_key: VertexKey
) -> corner.Corner:
    """Returns the corner defined by an edge and a vertex."""
    face_key = next(
        face_key
        for face_key in mesh.vertex_faces[vertex_key]
        if edge_key in list(face_edges(mesh, face_key))
    )
    return corner_from_face_vertex(mesh, face_key, vertex_key)


def face_trace(
    mesh: dlfl_mesh.Mesh, face_key: FaceKey
) -> Generator[corner.Corner, None, None]:
    """Returns a generator over the corners of a face boundary."""

    for edge_2_vertex_keys, edge_1_vertex_keys in circular_list.pairs(
        list(circular_list.pairs(mesh.face_vertices[face_key]))
    ):
        yield corner.Corner(
            vertex_key=edge_1_vertex_keys[0],
            face_key=face_key,
            edge_1_key=EdgeKey(frozenset(edge_1_vertex_keys)),
            edge_2_key=EdgeKey(frozenset(edge_2_vertex_keys)),
        )


def vertex_trace(
    mesh: dlfl_mesh.Mesh, vertex_key: VertexKey
) -> Generator[corner.Corner, None, None]:
    """Returns a generator over the corners of a vertex rotation."""
    start_corner = corner_from_face_vertex(
        mesh, next(iter(mesh.vertex_faces[vertex_key])), vertex_key
    )
    yield start_corner

    current_corner = corner_from_face_vertex(
        mesh,
        next(
            face_key
            for face_key in mesh.vertex_faces[vertex_key]
            if start_corner.edge_1_key in list(face_edges(mesh, face_key))
            and face_key != start_corner.face_key
        ),
        vertex_key,
    )

    while current_corner != start_corner:
        yield current_corner
        current_corner = corner_from_face_vertex(
            mesh,
            next(
                face_key
                for face_key in mesh.vertex_faces[vertex_key]
                if current_corner.edge_1_key in list(face_edges(mesh, face_key))
                and face_key != current_corner.face_key
            ),
            vertex_key,
        )


def create_point_sphere(mesh: dlfl_mesh.Mesh, position: Point3D) -> corner.Corner:
    """Creates a point-sphere in the passed mesh.

    Creates a face and a vertex at the passed position, set the vertex as the
    only element in the created face's boundary, and set the face as the only
    element in the created vertex's face rotation.
    """
    vertex_key = mesh.create_vertex(position)
    face_key = mesh.create_face()
    mesh.face_vertices[face_key].append(vertex_key)
    mesh.vertex_faces[vertex_key].add(face_key)
    mesh.create_edge(vertex_key, vertex_key)
    return corner_from_face_vertex(mesh, face_key, vertex_key)


def insert_edge(
    mesh: dlfl_mesh.Mesh,
    corner_1: corner.Corner,
    corner_2: corner.Corner,
) -> Tuple[FaceKey, FaceKey]:
    """Inserts an edge between two corners.

    Returns the faces created as a result of this operation:
     - A tuple of (new_face_1_key, new_face_2_key) for a cofacial insertion.
     - A tuple of (new_face_key, new_face_key) for a non-cofacial insertion.
    """
    return (
        _insert_edge_cofacial
        if corner_1.face_key == corner_2.face_key
        else _insert_edge_non_cofacial
    )(mesh, corner_1, corner_2)


def _insert_edge_cofacial(
    mesh: dlfl_mesh.Mesh,
    corner_1: corner.Corner,
    corner_2: corner.Corner,
) -> Tuple[FaceKey, FaceKey]:
    """Inserts an edge between two corners in the same face.

    This will split the old face into two new ones.
    """
    old_face_key = corner_1.face_key  # == corner_2.face_key.

    # Create two new faces.
    new_face_1_key = mesh.create_face()
    new_face_2_key = mesh.create_face()

    # Compute the boundaries of the newly created faces as the boundary of the old
    # face circulated to end with vertex_2 and split at vertex_1.
    new_face_1_vertices, new_face_2_vertices = circular_list.split_at_item(
        circular_list.circulated_to_item(
            mesh.face_vertices[old_face_key], corner_2.vertex_key
        ),
        corner_1.vertex_key,
    )

    # Append vertex_2 to new_face_1's boundary (resp. vertex_1 to new_face_2).
    mesh.face_vertices[new_face_1_key] = new_face_1_vertices + [corner_2.vertex_key]
    mesh.face_vertices[new_face_2_key] = new_face_2_vertices + [corner_1.vertex_key]

    # Update the vertices face rotations:
    # Replace old_face with new_face_1 for each vertex in new_face_1.
    for vertex_key in mesh.face_vertices[new_face_1_key]:
        mesh.vertex_faces[vertex_key].discard(old_face_key)
        mesh.vertex_faces[vertex_key].add(new_face_1_key)

    # Replace old_face with new_face_2 for each vertex in new_face_2.
    for vertex_key in mesh.face_vertices[new_face_2_key]:
        mesh.vertex_faces[vertex_key].discard(old_face_key)
        mesh.vertex_faces[vertex_key].add(new_face_2_key)

    # Delete the old face.
    mesh.delete_face(old_face_key)

    # Create the edge.
    mesh.create_edge(corner_1.vertex_key, corner_2.vertex_key)

    return (new_face_1_key, new_face_2_key)


def _insert_edge_non_cofacial(
    mesh: dlfl_mesh.Mesh,
    corner_1: corner.Corner,
    corner_2: corner.Corner,
) -> Tuple[FaceKey, FaceKey]:
    """Inserts an edge between two corners of two different faces.

    This will merge the two old faces into a new one.
    """
    old_face_1_vertices = mesh.face_vertices[corner_1.face_key]
    old_face_2_vertices = mesh.face_vertices[corner_2.face_key]

    # Create a new face.
    new_face_key = mesh.create_face()

    # Compute the boundary of the newly created face as the concatenation of:
    #  - corner_1.face_key's boundary circulated to end with vertex_1
    #  - old_face_2's boundary circulated to end with vertex_2's predecessor.
    #  - vertex_2 if old face 2 was not a point-sphere.
    #  - vertex_2 if corner_1.face_key was not a point-sphere.
    new_face_vertex_keys = (
        circular_list.circulated_to_item(old_face_1_vertices, corner_1.vertex_key)
        + circular_list.circulated_to_item(
            old_face_2_vertices,
            circular_list.previous_item(old_face_2_vertices, corner_2.vertex_key),
        )
        + ([corner_2.vertex_key] if len(old_face_2_vertices) > 1 else [])
        + ([corner_1.vertex_key] if len(old_face_1_vertices) > 1 else [])
    )
    mesh.face_vertices[new_face_key] = new_face_vertex_keys

    # Update the vertices face rotations:
    for vertex_key in new_face_vertex_keys:
        # Replace corner_1.face_key and old_face_2 with the new_face for each vertex.
        mesh.vertex_faces[vertex_key].discard(corner_1.face_key)
        mesh.vertex_faces[vertex_key].discard(corner_2.face_key)
        mesh.vertex_faces[vertex_key].add(new_face_key)

    # Delete the old faces.
    mesh.delete_face(corner_1.face_key)
    mesh.delete_face(corner_2.face_key)

    # Create the edge.
    mesh.create_edge(corner_1.vertex_key, corner_2.vertex_key)

    return (new_face_key, new_face_key)


def delete_edge(
    mesh: dlfl_mesh.Mesh, corner_1: corner.Corner, corner_2: corner.Corner
) -> Tuple[FaceKey, FaceKey]:
    """Deletes an edge between two corners.

    Returns the faces created as a result of this operation:
     - A tuple of (new_face_1_key, new_face_2_key) for a cofacial deletion.
     - A tuple of (new_face_key, new_face_key) for a non-cofacial deletion.
    """
    return (
        _delete_edge_cofacial
        if corner_1.face_key == corner_2.face_key
        else _delete_edge_non_cofacial
    )(mesh, corner_1, corner_2)


def _delete_edge_cofacial(
    mesh: dlfl_mesh.Mesh, corner_1: corner.Corner, corner_2: corner.Corner
) -> Tuple[FaceKey, FaceKey]:
    """Deletes an edge between two corners of the same face.

    This will split the old face into two new ones.
    """
    old_face_key = corner_1.face_key  # == corner_2.face_key.

    # Create two new faces.
    new_face_1_key = mesh.create_face()
    new_face_2_key = mesh.create_face()

    # Compute the boundaries of the new faces as the boundary of the old face
    # circulated to (vertex_1, vertex_2) and split at (vertex_2, vertex_1).
    new_face_1_vertices, new_face_2_vertices = circular_list.split_at_pair(
        circular_list.circulated_to_pair(
            mesh.face_vertices[old_face_key], (corner_1.vertex_key, corner_2.vertex_key)
        ),
        (corner_2.vertex_key, corner_1.vertex_key),
    )

    # Remove the last vertices from the created faces (i.e vertex_1 and
    # vertex_2) if the faces are not point-spheres.
    if len(new_face_1_vertices) > 1:
        new_face_1_vertices.pop()
    if len(new_face_2_vertices) > 1:
        new_face_2_vertices.pop()

    mesh.face_vertices[new_face_1_key] = new_face_1_vertices
    mesh.face_vertices[new_face_2_key] = new_face_2_vertices

    # Update the vertices face rotations:
    for vertex_key in mesh.face_vertices[new_face_1_key]:
        # Replace old_face with new_face_1 for each vertex in new_face_1.
        mesh.vertex_faces[vertex_key].discard(old_face_key)
        mesh.vertex_faces[vertex_key].add(new_face_1_key)

    for vertex_key in mesh.face_vertices[new_face_2_key]:
        # Replace old_face with new_face_2 for each vertex in new_face_2.
        mesh.vertex_faces[vertex_key].discard(old_face_key)
        mesh.vertex_faces[vertex_key].add(new_face_2_key)

    # Delete the old face.
    mesh.delete_face(old_face_key)

    # Delete the edge.
    mesh.delete_edge(EdgeKey(frozenset((corner_1.vertex_key, corner_2.vertex_key))))

    return (new_face_1_key, new_face_2_key)


def _delete_edge_non_cofacial(
    mesh: dlfl_mesh.Mesh, corner_1: corner.Corner, corner_2: corner.Corner
) -> Tuple[FaceKey, FaceKey]:
    """Deletes an edge between two corners of two different faces.

    This will merge the two old faces into a new one.
    """
    # Create a new face.
    new_face_key = mesh.create_face()

    old_face_1_vertices = mesh.face_vertices[corner_1.face_key]
    old_face_2_vertices = mesh.face_vertices[corner_2.face_key]

    # Compute the new face's boundary as the concatenation of:
    #  - corner_1.face_key's boundary circulated to vertex_1, without vertex_1.
    #  - old_face_2's boundary circulated to vertex_2, without vertex_2.
    new_face_vertex_keys = (
        circular_list.circulated_to_item(old_face_1_vertices, corner_1.vertex_key)[:-1]
        + circular_list.circulated_to_item(old_face_2_vertices, corner_2.vertex_key)[
            :-1
        ]
    )

    mesh.face_vertices[new_face_key] = new_face_vertex_keys

    # Update the vertices face rotations:
    for vertex_key in new_face_vertex_keys:
        # Replace corner_1.face_key and old_face_2 with new_face for each vertex of the
        # new face.
        mesh.vertex_faces[vertex_key].discard(corner_1.face_key)
        mesh.vertex_faces[vertex_key].discard(corner_2.face_key)
        mesh.vertex_faces[vertex_key].add(new_face_key)

    # Delete the old faces.
    mesh.delete_face(corner_1.face_key)
    mesh.delete_face(corner_2.face_key)

    # Delete the edge.
    mesh.delete_edge(EdgeKey(frozenset((corner_1.vertex_key, corner_2.vertex_key))))

    return (new_face_key, new_face_key)
