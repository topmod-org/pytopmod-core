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

    mesh.create_edge(v_2, v_1, f_4, f_1, "e6", "e3")
    mesh.create_edge(v_1, v_3, f_4, f_2, "e1", "e5")
    mesh.create_edge(v_1, v_4, f_2, f_1, "e2", "e4")
    mesh.create_edge(v_4, v_2, f_3, f_1, "e5", "e1")
    mesh.create_edge(v_3, v_4, f_3, f_2, "e6", "e3")
    mesh.create_edge(v_2, v_3, f_3, f_4, "e4", "e2")

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

    mesh.create_edge(v_1, v_2, f_1, f_2, "e4", "e2")
    mesh.create_edge(v_2, v_3, f_1, f_2, "e1", "e3")
    mesh.create_edge(v_3, v_4, f_1, f_2, "e2", "e4")
    mesh.create_edge(v_4, v_1, f_1, f_2, "e3", "e1")

    return mesh
