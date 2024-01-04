import dataclasses

from pytopmod.core.edge import EdgeKey
from pytopmod.core.face import FaceKey
from pytopmod.core.vertex import VertexKey


@dataclasses.dataclass(slots=True)
class Corner:
    """Convenience data class for representing a corner."""

    vertex_key: VertexKey
    face_key: FaceKey
    edge_1_key: EdgeKey
    edge_2_key: EdgeKey
