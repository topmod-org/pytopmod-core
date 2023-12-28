"""Manifold-preserving operators on DCEL Meshes."""
from typing import Generator, Optional

from pytopmod.core import circular_list, corner
from pytopmod.core.dcel import mesh as dcel_mesh
from pytopmod.core.edge import EdgeKey
from pytopmod.core.face import FaceKey
from pytopmod.core.vertex import VertexKey


def corner_from_edge_vertex(
    mesh: dcel_mesh.Mesh, edge_key: EdgeKey, vertex_key: VertexKey
) -> corner.Corner:
    """Returns the corner defined by an edge and a vertex."""
    edge_node = mesh.edge_nodes[edge_key]

    if vertex_key not in (edge_node.vertex_1_key, edge_node.vertex_2_key):
        raise ValueError(f"Vertex {vertex_key} is not an endpoint of edge {edge_key}.")

    return corner.Corner(
        vertex_key=vertex_key,
        face_key=(
            edge_node.face_1_key
            if vertex_key == edge_node.vertex_1_key
            else edge_node.face_2_key
        ),
        edge_1_key=edge_key,
        edge_2_key=(
            edge_node.next_edge_1_key
            if vertex_key == edge_node.vertex_1_key
            else edge_node.next_edge_2_key
        ),
    )


def corner_from_face_vertex(
    mesh: dcel_mesh.Mesh, face_key: FaceKey, vertex_key: VertexKey
) -> corner.Corner:
    """Returns the corner defined by a face and a vertex."""
    for edge_key in vertex_trace(mesh, vertex_key):
        edge_node = mesh.edge_nodes[edge_key]
        if edge_node.face_1_key == face_key:
            return corner_from_edge_vertex(mesh, edge_key, edge_node.vertex_1_key)
        if edge_node.face_2_key == face_key:
            return corner_from_edge_vertex(mesh, edge_key, edge_node.vertex_2_key)

    raise ValueError(f"Vertex {vertex_key} is not in face {face_key}.")


def vertex_trace(
    mesh: dcel_mesh.Mesh,
    vertex_key: VertexKey,
    start_edge_key: Optional[EdgeKey] = None,
) -> Generator[EdgeKey, None, None]:
    """Returns a generator over the edges that form a vertex rotation.

    The starting edge can optionally be specified, otherwise one will be picked.
    """
    start_corner = corner_from_edge_vertex(
        mesh, start_edge_key or next(mesh.vertex_edges(vertex_key)), vertex_key
    )
    yield start_corner.edge_1_key

    corner = corner_from_edge_vertex(mesh, start_corner.edge_2_key, vertex_key)

    while corner != start_corner:
        yield corner.edge_1_key
        corner = corner_from_edge_vertex(mesh, corner.edge_2_key, vertex_key)


def face_trace(
    mesh: dcel_mesh.Mesh, face_key: FaceKey, start_edge_key: Optional[EdgeKey] = None
) -> Generator[EdgeKey, None, None]:
    """Returns a generator over the edges that form a face boundary.

    The starting edge can optionally be specified, otherwise one will be picked.
    """
    start_edge_key = start_edge_key or next(mesh.face_edges(face_key))
    yield start_edge_key

    edge_node = mesh.edge_nodes[start_edge_key]
    edge_key = (
        edge_node.next_edge_1_key
        if edge_node.face_1_key == face_key
        else edge_node.next_edge_2_key
    )

    while edge_key != start_edge_key:
        yield edge_key
        edge_node = mesh.edge_nodes[edge_key]
        edge_key = (
            edge_node.next_edge_1_key
            if edge_node.face_1_key == face_key
            else edge_node.next_edge_2_key
        )


def _update_next_edge(
    mesh: dcel_mesh.Mesh,
    edge_key: EdgeKey,
    at_vertex_key: VertexKey,
    new_edge_key: EdgeKey,
):
    """Updates the next edge information of an edge node at the passed vertex."""
    edge_node = mesh.edge_nodes[edge_key]

    if at_vertex_key not in (edge_node.vertex_1_key, edge_node.vertex_2_key):
        raise ValueError(
            f"Vertex {at_vertex_key} is not an endpoint of edge {edge_key}."
        )

    if at_vertex_key == edge_node.vertex_1_key:
        edge_node.next_edge_1_key = new_edge_key
    if at_vertex_key == edge_node.vertex_2_key:
        edge_node.next_edge_2_key = new_edge_key


def _replace_face(
    mesh: dcel_mesh.Mesh,
    old_face_key: FaceKey,
    new_face_key: FaceKey,
    start_edge_key: Optional[EdgeKey] = None,
):
    """Replaces a face by another one in a mesh."""
    for edge_key in list(face_trace(mesh, old_face_key, start_edge_key)):
        edge_node = mesh.edge_nodes[edge_key]
        if edge_node.face_1_key == old_face_key:
            edge_node.face_1_key = new_face_key
        if edge_node.face_2_key == old_face_key:
            edge_node.face_2_key = new_face_key


def insert_edge(
    mesh: dcel_mesh.Mesh,
    vertex_1_key: VertexKey,
    edge_1_key: EdgeKey,
    vertex_2_key: VertexKey,
    edge_2_key: EdgeKey,
):
    """Inserts an edge between two corners.

    If the two corners:
      - belong to the same face, the face will be split into two new ones.
      - belong to two different faces, the faces will be merged into a new one.
    """
    corner_1 = corner_from_edge_vertex(mesh, edge_1_key, vertex_1_key)
    corner_2 = corner_from_edge_vertex(mesh, edge_2_key, vertex_2_key)

    # Set the vertex and edge information for the new edge.
    # 2 - Create a new edge node.
    new_edge_key = mesh.create_edge(
        vertex_1_key,
        vertex_2_key,
        corner_1.face_key,
        corner_2.face_key,
        corner_1.edge_2_key,
        corner_2.edge_2_key,
    )
    new_edge_node = mesh.edge_nodes[new_edge_key]

    # Non-cofacial insertion.
    if corner_1.face_key != corner_2.face_key:
        # 3.1 - Update the face information.

        # Create a new face.
        new_face_key = mesh.create_face()

        # Traverse the corners' faces and replace face_1 and face_2 by the new face.
        _replace_face(mesh, corner_1.face_key, new_face_key)
        _replace_face(mesh, corner_2.face_key, new_face_key)

        # Set the face information for the new edge.
        new_edge_node.face_1_key = new_face_key
        new_edge_node.face_2_key = new_face_key

        # Delete the old faces.
        mesh.delete_face(corner_1.face_key)
        mesh.delete_face(corner_2.face_key)

        # 3.2 - Update the edge information.
        _update_next_edge(mesh, corner_1.edge_1_key, corner_1.vertex_key, new_edge_key)
        _update_next_edge(mesh, corner_2.edge_1_key, corner_2.vertex_key, new_edge_key)

    # Cofacial insertion.
    else:
        face_key = corner_1.face_key

        # 4.1 - Update the edge information.
        _update_next_edge(mesh, corner_1.edge_1_key, corner_1.vertex_key, new_edge_key)
        _update_next_edge(mesh, corner_2.edge_1_key, corner_2.vertex_key, new_edge_key)

        # 4.2 - Update the face information.
        # Create two new faces.
        new_face_1_key = mesh.create_face()
        new_face_2_key = mesh.create_face()

        # Starting from one direction of the new edge, replace face_1 by new_face_1.
        _replace_face(mesh, face_key, new_face_1_key, corner_1.edge_2_key)
        # Starting from the opposite direction, replace face_1 by new_face_2.
        _replace_face(mesh, face_key, new_face_2_key, corner_2.edge_2_key)

        # Delete face_1 == face_2.
        mesh.delete_face(face_key)


def delete_edge(mesh: dcel_mesh.Mesh, old_edge: EdgeKey):
    old_edge_node = mesh.edge_nodes[old_edge]

    corner_1 = corner_from_edge_vertex(mesh, old_edge, old_edge_node.vertex_1_key)
    corner_2 = corner_from_edge_vertex(mesh, old_edge, old_edge_node.vertex_2_key)

    # 1.1 - Find the edge before the old edge in the rotation of vertex_1.
    vertex_1_previous_edge_key = circular_list.previous_item(
        list(vertex_trace(mesh, corner_1.vertex_key)), old_edge
    )

    # 1.2 - Find the edge before the old edge in the rotation of vertex_2.
    vertex_2_previous_edge_key = circular_list.previous_item(
        list(vertex_trace(mesh, corner_2.vertex_key)), old_edge
    )

    # 2 - Non-cofacial deletion.
    if corner_1.face_key != corner_2.face_key:
        # 2.1 - Update the face information.
        # Create a new face.
        new_face_key = mesh.create_face()

        # Traverse face_1 and face_2, replace face_1 and face_2 with new_face.
        _replace_face(mesh, corner_1.face_key, new_face_key)
        _replace_face(mesh, corner_2.face_key, new_face_key)

        # Delete face_1 and face_2.
        mesh.delete_face(corner_1.face_key)
        mesh.delete_face(corner_2.face_key)

        # 2.2 - Update the edge information to delete the edge.
        _update_next_edge(
            mesh, vertex_1_previous_edge_key, corner_1.vertex_key, corner_1.edge_2_key
        )
        _update_next_edge(
            mesh, vertex_2_previous_edge_key, corner_2.vertex_key, corner_2.edge_2_key
        )

        # Delete the edge.
        mesh.delete_edge(old_edge)

    # 3 - Cofacial deletion.
    else:
        face_key = corner_1.face_key

        # 3.1 - Update the edge information to delete the edge.
        _update_next_edge(
            mesh, vertex_1_previous_edge_key, corner_1.vertex_key, corner_1.edge_2_key
        )
        _update_next_edge(
            mesh, vertex_2_previous_edge_key, corner_2.vertex_key, corner_2.edge_2_key
        )

        # Delete the edge.
        mesh.delete_edge(old_edge)

        # 3.2 - Update the face information.
        # Create two new faces.
        new_face_1_key = mesh.create_face()
        new_face_2_key = mesh.create_face()

        # Starting from vertex_1_previous, traverse the face and replace face_1 by
        # new_face_1.
        _replace_face(mesh, face_key, new_face_1_key, vertex_1_previous_edge_key)

        # Starting from vertex_2_previous, traverse the face and replace face_1 by
        # new_face_2.
        _replace_face(mesh, face_key, new_face_2_key, vertex_2_previous_edge_key)

        # Delete face_1 == face_2.
        mesh.delete_face(face_key)
