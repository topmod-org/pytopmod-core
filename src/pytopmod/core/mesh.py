import dataclasses

from pytopmod.core.face import FaceKey
from pytopmod.core.geometry import Point3D
from pytopmod.core.keystore import KeyStore
from pytopmod.core.vertex import VertexKey


@dataclasses.dataclass(slots=True)
class Mesh:
    """Base Mesh class, to be subclassed (e.g DLFLMesh, DCELMesh, ect.)

    Stores and provides create/delete methods for vertice and face keys.
    Also exposes a vertex coordinates map.
    """

    vertices: KeyStore[VertexKey] = dataclasses.field(init=False)
    faces: KeyStore[FaceKey] = dataclasses.field(init=False)
    vertex_coordinates: dict[VertexKey, Point3D] = dataclasses.field(init=False)

    def __post_init__(self):
        self.vertices = KeyStore[VertexKey]("v")
        self.faces = KeyStore[VertexKey]("f")
        self.vertex_coordinates = {}

    def create_vertex(self, position: Point3D) -> VertexKey:
        vertex = self.vertices.new()
        self.vertex_coordinates[vertex] = position
        return vertex

    def delete_vertex(self, vertex: VertexKey):
        self.vertices.delete(vertex)
        del self.vertex_coordinates[vertex]

    def create_face(self) -> FaceKey:
        return self.faces.new()

    def delete_face(self, face: FaceKey):
        return self.faces.delete(face)
