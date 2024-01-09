"""Convenience functions to create primitive DLFL Meshes."""
from pytopmod.core.dlfl import mesh as dlfl_mesh
from pytopmod.core.dlfl import operators


def triangle() -> dlfl_mesh.Mesh:
    """Creates and returns a triangle with two faces."""
    mesh = dlfl_mesh.Mesh()

    corner_1 = operators.create_point_sphere(mesh, (1.0, 1.0, 1.0))
    corner_2 = operators.create_point_sphere(mesh, (1.0, -1.0, -1.0))
    corner_3 = operators.create_point_sphere(mesh, (-1.0, 1.0, -1.0))

    new_face_1, _ = operators.insert_edge(mesh, corner_1, corner_2)
    new_face_2, _ = operators.insert_edge(
        mesh,
        operators.corner_from_face_vertex(mesh, new_face_1, corner_2.vertex_key),
        corner_3,
    )
    operators.insert_edge(
        mesh,
        operators.corner_from_face_vertex(mesh, new_face_2, corner_3.vertex_key),
        operators.corner_from_face_vertex(mesh, new_face_2, corner_1.vertex_key),
    )

    return mesh


def tetrahedron():
    """Creates and returns a tetrahedron."""
    mesh = dlfl_mesh.Mesh()

    corner_1 = operators.create_point_sphere(mesh, (1.0, 1.0, 1.0))
    corner_2 = operators.create_point_sphere(mesh, (1.0, -1.0, -1.0))
    corner_3 = operators.create_point_sphere(mesh, (-1.0, 1.0, -1.0))
    corner_4 = operators.create_point_sphere(mesh, (-1.0, -1.0, 1.0))

    new_face_1, _ = operators.insert_edge(mesh, corner_1, corner_2)
    new_face_2, _ = operators.insert_edge(
        mesh,
        operators.corner_from_face_vertex(mesh, new_face_1, corner_2.vertex_key),
        corner_3,
    )
    new_face_3, _ = operators.insert_edge(
        mesh,
        operators.corner_from_face_vertex(mesh, new_face_2, corner_3.vertex_key),
        operators.corner_from_face_vertex(mesh, new_face_2, corner_1.vertex_key),
    )
    new_face_4, _ = operators.insert_edge(
        mesh,
        operators.corner_from_face_vertex(mesh, new_face_3, corner_1.vertex_key),
        corner_4,
    )
    new_face_5, _ = operators.insert_edge(
        mesh,
        operators.corner_from_face_vertex(mesh, new_face_4, corner_4.vertex_key),
        operators.corner_from_face_vertex(mesh, new_face_4, corner_2.vertex_key),
    )
    operators.insert_edge(
        mesh,
        operators.corner_from_face_vertex(mesh, new_face_5, corner_4.vertex_key),
        operators.corner_from_face_vertex(mesh, new_face_5, corner_3.vertex_key),
    )

    return mesh
