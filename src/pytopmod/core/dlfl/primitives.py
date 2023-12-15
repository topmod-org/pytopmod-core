"""Convenience functions to create primitive DLFL Meshes."""
from pytopmod.core.dlfl import operators
from pytopmod.core.dlfl.mesh import DLFLMesh


def triangle() -> DLFLMesh:
    """Creates and returns a triangle with two faces."""
    mesh = DLFLMesh()

    operators.create_point_sphere(mesh, (1.0, 1.0, 1.0))
    operators.create_point_sphere(mesh, (1.0, -1.0, -1.0))
    operators.create_point_sphere(mesh, (-1.0, 1.0, -1.0))

    operators.insert_edge(mesh, "v1", "f1", "v2", "f2")
    operators.insert_edge(mesh, "v2", "f4", "v3", "f3")
    operators.insert_edge(mesh, "v3", "f5", "v1", "f5")

    return mesh


def tetrahedron():
    """Creates and returns a tetrahedron."""
    mesh = DLFLMesh()

    operators.create_point_sphere(mesh, (1.0, 1.0, 1.0))
    operators.create_point_sphere(mesh, (1.0, -1.0, -1.0))
    operators.create_point_sphere(mesh, (-1.0, 1.0, -1.0))
    operators.create_point_sphere(mesh, (-1.0, -1.0, 1.0))

    operators.insert_edge(mesh, "v1", "f1", "v2", "f2")
    operators.insert_edge(mesh, "v2", "f5", "v3", "f3")
    operators.insert_edge(mesh, "v3", "f6", "v1", "f6")
    operators.insert_edge(mesh, "v1", "f7", "v4", "f4")
    operators.insert_edge(mesh, "v4", "f9", "v2", "f9")
    operators.insert_edge(mesh, "v4", "f10", "v3", "f10")

    return mesh
