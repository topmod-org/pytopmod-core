import dataclasses
from typing import Tuple

from pytopmod.core.face import FaceKey
from pytopmod.core.vertex import VertexKey


@dataclasses.dataclass(slots=True)
class HalfEdge:
    """Convenience data class for representing a half-edge."""

    vertex_keys: Tuple[VertexKey, VertexKey]
    face_key: FaceKey
