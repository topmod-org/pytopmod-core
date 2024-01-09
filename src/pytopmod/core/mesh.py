import dataclasses

from pytopmod.core.edge import EdgeKey
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

    vertex_keys: KeyStore[VertexKey] = dataclasses.field(init=False)
    face_keys: KeyStore[FaceKey] = dataclasses.field(init=False)
    edge_keys: set[EdgeKey] = dataclasses.field(init=False)
    vertex_coordinates: dict[VertexKey, Point3D] = dataclasses.field(init=False)

    def __post_init__(self):
        self.vertex_keys = KeyStore[VertexKey]("v")
        self.face_keys = KeyStore[VertexKey]("f")
        self.edge_keys = set()
        self.vertex_coordinates = dict()

    def create_vertex(self, position: Point3D) -> VertexKey:
        vertex_key = self.vertex_keys.new()
        self.vertex_coordinates[vertex_key] = position
        return vertex_key

    def delete_vertex(self, vertex_key: VertexKey):
        self.vertex_keys.delete(vertex_key)
        self.vertex_coordinates.pop(vertex_key)

    def create_face(self) -> FaceKey:
        return self.face_keys.new()

    def delete_face(self, face_key: FaceKey):
        return self.face_keys.delete(face_key)

    def create_edge(self, vertex_1_key: VertexKey, vertex_2_key: VertexKey) -> EdgeKey:
        edge_key = EdgeKey(frozenset((vertex_1_key, vertex_2_key)))
        self.edge_keys.add(edge_key)
        return edge_key

    def delete_edge(self, edge_key: EdgeKey):
        self.edge_keys.remove(edge_key)
