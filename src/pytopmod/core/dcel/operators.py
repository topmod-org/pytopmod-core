"""Manifold-preserving operators on DCEL Meshes."""
import itertools
from typing import Generator, Optional

from pytopmod.core import circular_list
from pytopmod.core.dcel import mesh as dcel_mesh
from pytopmod.core.edge import EdgeKey
from pytopmod.core.face import FaceKey
from pytopmod.core.vertex import VertexKey


def vertex_trace(
    mesh: dcel_mesh.Mesh,
    vertex_key: VertexKey,
    start_edge_key: Optional[EdgeKey] = None,
) -> Generator[EdgeKey, None, None]:
    """Returns a generator over the edges that form a vertex rotation.

    The starting edge can optionally be specified, otherwise one will be picked.
    """
    start_edge_key = start_edge_key or next(mesh.vertex_edges(vertex_key))
    yield start_edge_key

    edge_node = mesh.edge_nodes[start_edge_key]
    edge_key = (
        edge_node.vertex_1_next_key
        if edge_node.vertex_1_key == vertex_key
        else edge_node.vertex_2_next_key
    )

    while edge_key != start_edge_key:
        yield edge_key
        edge_node = mesh.edge_nodes[edge_key]
        edge_key = (
            edge_node.vertex_1_next_key
            if edge_node.vertex_1_key == vertex_key
            else edge_node.vertex_2_next_key
        )


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
        edge_node.vertex_1_next_key
        if edge_node.face_1_key == face_key
        else edge_node.vertex_2_next_key
    )

    while edge_key != start_edge_key:
        yield edge_key
        edge_node = mesh.edge_nodes[edge_key]
        edge_key = (
            edge_node.vertex_1_next_key
            if edge_node.face_1_key == face_key
            else edge_node.vertex_2_next_key
        )


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
    edge_1_node = mesh.edge_nodes[edge_1_key]
    edge_2_node = mesh.edge_nodes[edge_2_key]

    # 1.1 - Find the 2nd edges for each corner.
    edge_1_2_key = (
        edge_1_node.vertex_1_next_key
        if edge_1_node.vertex_1_key == vertex_1_key
        else edge_1_node.vertex_2_next_key
    )
    edge_2_2_key = (
        edge_2_node.vertex_1_next_key
        if edge_2_node.vertex_1_key == vertex_2_key
        else edge_2_node.vertex_2_next_key
    )

    # 1.2 - Find the faces that contain each corner.
    face_1_key = (
        edge_1_node.face_1_key
        if edge_1_node.vertex_1_key == vertex_1_key
        else edge_1_node.face_2_key
    )
    face_2_key = (
        edge_2_node.face_1_key
        if edge_2_node.vertex_1_key == vertex_2_key
        else edge_1_node.face_2_key
    )

    # Set the vertex and edge information for the new edge.
    # 2 - Create a new edge node.
    new_edge_key = mesh.create_edge(
        vertex_1_key, vertex_2_key, face_1_key, face_2_key, edge_1_2_key, edge_2_2_key
    )
    new_edge_node = mesh.edge_nodes[new_edge_key]

    # Non-cofacial insertion.
    if face_1_key != face_2_key:
        # 3.1 - Update the face information.
        # Create a new face.
        new_face_key = mesh.create_face()
        # Traverse the corners' faces and replace face_1 and face_2 by the new face.
        for edge_key in list(
            itertools.chain(face_trace(mesh, face_1_key), face_trace(mesh, face_2_key))
        ):
            edge_node = mesh.edge_nodes[edge_key]
            if edge_node.face_1_key in (face_1_key, face_2_key):
                edge_node.face_1_key = new_face_key
            if edge_node.face_2_key in (face_1_key, face_2_key):
                edge_node.face_2_key = new_face_key
        # Set the face information for the new edge.
        new_edge_node.face_1_key = new_face_key
        new_edge_node.face_2_key = new_face_key
        # Delete the old faces.
        mesh.delete_face(face_1_key)
        mesh.delete_face(face_2_key)

        # 3.2 - Update the edge information.
        if edge_1_node.vertex_1_key == vertex_1_key:
            edge_1_node.vertex_1_next_key = new_edge_key
        else:
            edge_1_node.vertex_2_next_key = new_edge_key
        if edge_2_node.vertex_1_key == vertex_2_key:
            edge_2_node.vertex_1_next_key = new_edge_key
        else:
            edge_2_node.vertex_2_next_key = new_edge_key

    # Cofacial insertion.
    else:
        # 4.1 - Update the edge information.
        if edge_1_node.vertex_1_key == vertex_1_key:
            edge_1_node.vertex_1_next_key = new_edge_key
        else:
            edge_1_node.vertex_2_next_key = new_edge_key
        if edge_2_node.vertex_1_key == vertex_2_key:
            edge_2_node.vertex_1_next_key = new_edge_key
        else:
            edge_2_node.vertex_2_next_key = new_edge_key

        # 4.2 - Update the face information.
        # Create two new faces.
        new_face_1_key = mesh.create_face()
        new_face_2_key = mesh.create_face()

        # Starting from one direction of the new edge, replace face_1 by new_face_1.
        for edge_key in list(face_trace(mesh, face_1_key, start_edge_key=edge_1_2_key)):
            edge_node = mesh.edge_nodes[edge_key]
            if edge_node.face_1_key == face_1_key:
                edge_node.face_1_key = new_face_1_key
            else:
                edge_node.face_2_key = new_face_1_key

        # Starting from the opposite direction, replace face_1 by new_face_2.
        for edge_key in list(face_trace(mesh, face_1_key, start_edge_key=edge_2_2_key)):
            edge_node = mesh.edge_nodes[edge_key]
            if edge_node.face_1_key == face_1_key:
                edge_node.face_1_key = new_face_2_key
            else:
                edge_node.face_2_key = new_face_2_key

        # Delete face_1 == face_2.
        mesh.delete_face(face_1_key)


def delete_edge(mesh: dcel_mesh.Mesh, old_edge: EdgeKey):
    old_edge_node = mesh.edge_nodes[old_edge]

    # 1.1 - Find the edges before and after the edge in the rotation of vertex_1.
    vertex_1_rotation = list(vertex_trace(mesh, old_edge_node.vertex_1_key))
    vertex_1_previous = circular_list.previous_item(vertex_1_rotation, old_edge)
    vertex_1_previous_node = mesh.edge_nodes[vertex_1_previous]
    vertex_1_next_key = circular_list.next_item(vertex_1_rotation, old_edge)

    # 1.2 - Find the edges before and after the edge in the rotation of vertex_2.
    vertex_2_rotation = list(vertex_trace(mesh, old_edge_node.vertex_2_key))
    vertex_2_previous = circular_list.previous_item(vertex_2_rotation, old_edge)
    vertex_2_previous_node = mesh.edge_nodes[vertex_2_previous]
    vertex_2_next_key = circular_list.next_item(vertex_2_rotation, old_edge)

    face_1_key = old_edge_node.face_1_key
    face_2_key = old_edge_node.face_2_key

    # 2 - Non-cofacial deletion.
    if face_1_key != face_2_key:
        # 2.1 - Update the face information.
        # Create a new face.
        new_face_key = mesh.create_face()

        # Traverse face_1 and face_2, replace face_1 and face_2 with new_face.
        for edge_key in list(
            itertools.chain(face_trace(mesh, face_1_key), face_trace(mesh, face_2_key))
        ):
            edge_node = mesh.edge_nodes[edge_key]
            if edge_node.face_1_key in (face_1_key, face_2_key):
                edge_node.face_1_key = new_face_key
            if edge_node.face_2_key in (face_1_key, face_2_key):
                edge_node.face_2_key = new_face_key

        # Delete face_1 and face_2.
        mesh.delete_face(face_1_key)
        mesh.delete_face(face_2_key)

        # 2.2 - Update the edge information to delete the edge.
        if vertex_1_previous_node.vertex_1_key == old_edge_node.vertex_1_key:
            vertex_1_previous_node.vertex_1_next_key = vertex_1_next_key
        else:
            vertex_1_previous_node.vertex_2_next_key = vertex_1_next_key
        if vertex_2_previous_node.vertex_1_key == old_edge_node.vertex_2_key:
            vertex_2_previous_node.vertex_1_next_key = vertex_2_next_key
        else:
            vertex_2_previous_node.vertex_2_next_key = vertex_2_next_key

        # Delete the edge.
        mesh.delete_edge(old_edge)

    # 3 - Cofacial deletion.
    else:
        # 3.1 - Update the edge information to delete the edge.
        if vertex_1_previous_node.vertex_1_key == old_edge_node.vertex_1_key:
            vertex_1_previous_node.vertex_1_next_key = vertex_1_next_key
        else:
            vertex_1_previous_node.vertex_2_next_key = vertex_1_next_key
        if vertex_2_previous_node.vertex_1_key == old_edge_node.vertex_2_key:
            vertex_2_previous_node.vertex_1_next_key = vertex_2_next_key
        else:
            vertex_2_previous_node.vertex_2_next_key = vertex_2_next_key

        # Delete the edge.
        mesh.delete_edge(old_edge)

        # 3.2 - Update the face information.
        # Create two new faces.
        new_face_1_key = mesh.create_face()
        new_face_2_key = mesh.create_face()

        # Starting from vertex_1_previous, traverse the face and replace face_1 by
        # new_face_1.
        for edge_key in list(
            face_trace(mesh, face_1_key, start_edge_key=vertex_1_previous)
        ):
            edge_node = mesh.edge_nodes[edge_key]
            if edge_node.face_1_key == face_1_key:
                edge_node.face_1_key = new_face_1_key
            if edge_node.face_2_key == face_1_key:
                edge_node.face_2_key = face_1_key

        # Starting from vertex_2_previous, traverse the face and replace face_1 by
        # new_face_2.
        for edge_key in list(
            face_trace(mesh, face_1_key, start_edge_key=vertex_2_previous)
        ):
            edge_node = mesh.edge_nodes[edge_key]
            if edge_node.face_1_key == face_1_key:
                edge_node.face_1_key = new_face_2_key
            if edge_node.face_2_key == face_1_key:
                edge_node.face_2_key = new_face_2_key

        # Delete face_1 == face_2.
        mesh.delete_face(face_1_key)
