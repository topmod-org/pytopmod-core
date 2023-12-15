import dataclasses

from pytopmod.core.face import FaceKey
from pytopmod.core.geometry import Point3D
from pytopmod.core.mesh import Mesh
from pytopmod.core.vertex import VertexKey


@dataclasses.dataclass(slots=True)
class DLFLMesh(Mesh):
    """A DLFL-backed Mesh.

    This structure uses two maps:
     - face_vertices: A map that associates each face with an ordered list of the
        vertices forming its boundary.
     - vertex_faces: A map that associates each vertex with an (unordered) set of
        faces in its rotation.

    Manifold-preserving operators are implemented in 'operators.py'.
    """

    face_vertices: dict[FaceKey, list[VertexKey]] = dataclasses.field(
        default_factory=dict
    )
    vertex_faces: dict[VertexKey, set[FaceKey]] = dataclasses.field(
        default_factory=dict
    )

    def create_vertex(self, position: Point3D) -> VertexKey:
        vertex = super(DLFLMesh, self).create_vertex(position)
        self.vertex_faces[vertex] = set()
        return vertex

    def delete_vertex(self, vertex: VertexKey):
        super(DLFLMesh, self).delete_vertex(vertex)
        del self.vertex_faces[vertex]

    def create_face(self) -> FaceKey:
        face = super(DLFLMesh, self).create_face()
        self.face_vertices[face] = []
        return face

    def delete_face(self, face: FaceKey):
        super(DLFLMesh, self).delete_face(face)
        del self.face_vertices[face]
