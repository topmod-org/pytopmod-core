from typing import TypeAlias

from pytopmod.core.vertex import VertexKey

# Type alias for an edge key.
EdgeKey: TypeAlias = frozenset[VertexKey]
