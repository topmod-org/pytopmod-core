import dataclasses
from typing import Generator

from pytopmod.core import keystore
from pytopmod.core import mesh as base_mesh
from pytopmod.core.edge import EdgeKey
from pytopmod.core.face import FaceKey
from pytopmod.core.vertex import VertexKey


@dataclasses.dataclass(slots=True)
class EdgeNode:
    """An Edge Node in the DCEL structure."""

    vertex_1_key: VertexKey
    vertex_2_key: VertexKey
    face_1_key: FaceKey
    face_2_key: FaceKey
    edge_1_key: EdgeKey
    edge_2_key: EdgeKey

    def __repr__(self) -> str:
        return dataclasses.astuple(self).__repr__()


@dataclasses.dataclass(slots=True)
class Mesh(base_mesh.Mesh):
    """DCEL-backed Mesh class.

    This structure uses a map of EdgeNodes.

    Manifold-preserving operators are implemented in 'operators.py'.
    """

    edge_keys: keystore.KeyStore[EdgeKey] = dataclasses.field(init=False)
    edge_nodes: dict[EdgeKey, EdgeNode] = dataclasses.field(init=False)

    def __post_init__(self):
        super(Mesh, self).__post_init__()
        self.edge_keys = keystore.KeyStore[EdgeKey]("e")
        self.edge_nodes = {}

    def create_edge(
        self,
        vertex_1_key: VertexKey,
        vertex_2_key: VertexKey,
        face_1_key: FaceKey,
        face_2_key: FaceKey,
        edge_1_key: EdgeKey,
        edge_2_key: EdgeKey,
    ) -> EdgeKey:
        edge_key = self.edge_keys.new()
        self.edge_nodes[edge_key] = EdgeNode(
            vertex_1_key,
            vertex_2_key,
            face_1_key,
            face_2_key,
            edge_1_key,
            edge_2_key,
        )
        return edge_key

    def delete_edge(self, edge_key: EdgeKey):
        del self.edge_nodes[edge_key]
        return self.edge_keys.delete(edge_key)

    def vertex_edges(self, vertex_key: VertexKey) -> Generator[EdgeKey, None, None]:
        """Returns a generator over the edges incident to a vertex."""
        for edge_key, node in self.edge_nodes.items():
            if vertex_key in (node.vertex_1_key, node.vertex_2_key):
                yield edge_key

    def face_edges(self, face: FaceKey) -> Generator[EdgeKey, None, None]:
        """Returns a generator over the edges on the boundary of a face."""
        for edge_key, node in self.edge_nodes.items():
            if face in (node.face_1_key, node.face_2_key):
                yield edge_key
