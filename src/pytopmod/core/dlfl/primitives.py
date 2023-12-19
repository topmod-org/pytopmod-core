"""Convenience functions to create primitive DLFL Meshes."""
from pytopmod.core.dlfl import mesh as dlfl_mesh
from pytopmod.core.dlfl import operators


def triangle() -> dlfl_mesh.Mesh:
    """Creates and returns a triangle with two faces."""
    mesh = dlfl_mesh.Mesh()

    v_1, f_1 = operators.create_point_sphere(mesh, (1.0, 1.0, 1.0))
    v_2, f_2 = operators.create_point_sphere(mesh, (1.0, -1.0, -1.0))
    v_3, f_3 = operators.create_point_sphere(mesh, (-1.0, 1.0, -1.0))

    f_4, _ = operators.insert_edge(mesh, v_1, f_1, v_2, f_2)
    f_5, _ = operators.insert_edge(mesh, v_2, f_4, v_3, f_3)
    _, _ = operators.insert_edge(mesh, v_3, f_5, v_1, f_5)

    return mesh


def tetrahedron():
    """Creates and returns a tetrahedron."""
    mesh = dlfl_mesh.Mesh()

    v_1, f_1 = operators.create_point_sphere(mesh, (1.0, 1.0, 1.0))
    v_2, f_2 = operators.create_point_sphere(mesh, (1.0, -1.0, -1.0))
    v_3, f_3 = operators.create_point_sphere(mesh, (-1.0, 1.0, -1.0))
    v_4, f_4 = operators.create_point_sphere(mesh, (-1.0, -1.0, 1.0))

    f_5, _ = operators.insert_edge(mesh, v_1, f_1, v_2, f_2)
    f_6, _ = operators.insert_edge(mesh, v_2, f_5, v_3, f_3)
    f_7, _ = operators.insert_edge(mesh, v_3, f_6, v_1, f_6)
    f_9, _ = operators.insert_edge(mesh, v_1, f_7, v_4, f_4)
    f_10, _ = operators.insert_edge(mesh, v_4, f_9, v_2, f_9)
    _, _ = operators.insert_edge(mesh, v_4, f_10, v_3, f_10)

    return mesh
