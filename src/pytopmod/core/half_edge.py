import dataclasses
from typing import Tuple

from pytopmod.core.face import FaceKey
from pytopmod.core.vertex import VertexKey


@dataclasses.dataclass(slots=True)
class HalfEdge:
    """Convenience data class for representing a half-edge."""

    vertices: Tuple[VertexKey, VertexKey]
    face: FaceKey
