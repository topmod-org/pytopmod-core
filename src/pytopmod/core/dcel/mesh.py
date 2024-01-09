import dataclasses
from typing import Generator

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
    next_edge_1_key: EdgeKey
    next_edge_2_key: EdgeKey

    def __repr__(self) -> str:
        return dataclasses.astuple(self).__repr__()


@dataclasses.dataclass(slots=True)
class Mesh(base_mesh.Mesh):
    """DCEL-backed Mesh class.

    This structure uses a map of EdgeNodes.

    Manifold-preserving operators are implemented in 'operators.py'.
    """

    edge_nodes: dict[EdgeKey, EdgeNode] = dataclasses.field(default_factory=dict)

    def create_edge_node(
        self,
        vertex_1_key: VertexKey,
        vertex_2_key: VertexKey,
        face_1_key: FaceKey,
        face_2_key: FaceKey,
        next_edge_1_key: EdgeKey,
        next_edge_2_key: EdgeKey,
    ) -> EdgeNode:
        edge_key = EdgeKey(frozenset([vertex_1_key, vertex_2_key]))
        edge_node = EdgeNode(
            vertex_1_key,
            vertex_2_key,
            face_1_key,
            face_2_key,
            next_edge_1_key,
            next_edge_2_key,
        )
        self.edge_nodes[edge_key] = edge_node
        return edge_node

    def delete_edge(self, edge_key: EdgeKey):
        self.edge_nodes.pop(edge_key)
        return self.edge_keys.remove(edge_key)

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
