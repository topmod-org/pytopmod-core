"""Convenience functions to create primitive DCEL Meshes."""
from pytopmod.core.dcel import mesh as dcel_mesh


def tetrahedron() -> dcel_mesh.Mesh:
    mesh = dcel_mesh.Mesh()

    v_1, v_2, v_3, v_4 = (
        mesh.create_vertex((1.0, 1.0, 1.0)),
        mesh.create_vertex((1.0, -1.0, -1.0)),
        mesh.create_vertex((-1.0, 1.0, -1.0)),
        mesh.create_vertex((-1.0, -1.0, 1.0)),
    )

    f_1, f_2, f_3, f_4 = (
        mesh.create_face(),
        mesh.create_face(),
        mesh.create_face(),
        mesh.create_face(),
    )

    e_1_2 = mesh.create_edge(v_1, v_2)
    e_1_3 = mesh.create_edge(v_1, v_3)
    e_1_4 = mesh.create_edge(v_1, v_4)
    e_4_2 = mesh.create_edge(v_4, v_2)
    e_3_4 = mesh.create_edge(v_3, v_4)
    e_2_3 = mesh.create_edge(v_2, v_3)

    mesh.create_edge_node(v_2, v_1, f_4, f_1, e_2_3, e_1_4)
    mesh.create_edge_node(v_1, v_3, f_4, f_2, e_1_2, e_3_4)
    mesh.create_edge_node(v_1, v_4, f_2, f_1, e_1_3, e_4_2)
    mesh.create_edge_node(v_4, v_2, f_3, f_1, e_3_4, e_1_2)
    mesh.create_edge_node(v_3, v_4, f_3, f_2, e_2_3, e_1_4)
    mesh.create_edge_node(v_2, v_3, f_3, f_4, e_4_2, e_1_3)

    return mesh


def square() -> dcel_mesh.Mesh:
    mesh = dcel_mesh.Mesh()

    v_1, v_2, v_3, v_4 = (
        mesh.create_vertex((-1.0, 1.0, 0.0)),
        mesh.create_vertex((1.0, 1.0, 0.0)),
        mesh.create_vertex((1.0, -1.0, 0.0)),
        mesh.create_vertex((-1.0, -1.0, 0)),
    )

    f_1, f_2 = (mesh.create_face(), mesh.create_face())

    e_1_2 = mesh.create_edge(v_1, v_2)
    e_2_3 = mesh.create_edge(v_2, v_3)
    e_3_4 = mesh.create_edge(v_3, v_4)
    e_4_1 = mesh.create_edge(v_4, v_1)

    mesh.create_edge_node(v_1, v_2, f_1, f_2, e_4_1, e_2_3)
    mesh.create_edge_node(v_2, v_3, f_1, f_2, e_1_2, e_3_4)
    mesh.create_edge_node(v_3, v_4, f_1, f_2, e_2_3, e_4_1)
    mesh.create_edge_node(v_4, v_1, f_1, f_2, e_3_4, e_1_2)

    return mesh


def triangle() -> dcel_mesh.Mesh:
    mesh = dcel_mesh.Mesh()

    v_1, v_2, v_3 = (
        mesh.create_vertex((1.0, 1.0, 1.0)),
        mesh.create_vertex((1.0, -1.0, -1.0)),
        mesh.create_vertex((-1.0, 1.0, -1.0)),
    )

    f_1, f_2 = (mesh.create_face(), mesh.create_face())

    e_1_2 = mesh.create_edge(v_1, v_2)
    e_2_3 = mesh.create_edge(v_2, v_3)
    e_3_1 = mesh.create_edge(v_3, v_1)

    mesh.create_edge_node(v_1, v_2, f_1, f_2, e_3_1, e_2_3)
    mesh.create_edge_node(v_2, v_3, f_1, f_2, e_1_2, e_3_1)
    mesh.create_edge_node(v_3, v_1, f_1, f_2, e_2_3, e_1_2)

    return mesh
