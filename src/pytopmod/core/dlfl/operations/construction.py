import collections
from typing import Deque, Generator, Tuple, TypeAlias, cast

from pytopmod.core import circular_list
from pytopmod.core.dlfl import operators
from pytopmod.core.dlfl.mesh import DLFLMesh
from pytopmod.core.face import FaceKey
from pytopmod.core.geometry import Point3D
from pytopmod.core.half_edge import HalfEdge
from pytopmod.core.vertex import VertexKey

VertexQuadruplet: TypeAlias = Tuple[VertexKey, VertexKey, VertexKey, VertexKey]


def construct_mesh(points: list[Point3D], faces: list[list[int]]):
    """Constructs a manifold DLFL mesh from a set of points and faces."""
    mesh = DLFLMesh()

    # "Read all vertex positions and create a point-sphere for each vertex".
    vertices: list[VertexKey] = [
        operators.create_point_sphere(mesh, point)[0] for point in points
    ]

    # "Read all faces. Parse each face and create a list of edges present in each face
    # using the index into the array V to denote the edge ends."
    #
    # Instead of building this list, we build a queue of (a, v1, v2, b) edge quadruplets
    # representing the two corners of an edge: (a, v1, v2) and (v1, v2, b).
    # E.g: f1 = [v1, v2, v3], f2 = [v2, v3, v4], ...
    # => [(v1, v2, v3, v1), (v2, v3, v1, v2), (v3, v1, v2, v2),
    #     (v2, v3, v4, v2), (v3, v4, v2, v3), (v4, v2, v3, v4), ...]
    quadruplets: Deque[VertexQuadruplet] = collections.deque()
    for face in faces:
        for quadruplet in circular_list.tuples(face, 4):
            quadruplets.append(
                cast(VertexQuadruplet, tuple([vertices[index] for index in quadruplet]))
            )

    # Set of already inserted edges.
    inserted_edges: set[frozenset[VertexKey]] = set()

    # Counterpart to the quadruplets queue, will contain postponed edge quadruplets.
    postponed_quadruplets: Deque[VertexQuadruplet] = collections.deque()

    num_null_passes = 0
    while quadruplets:
        pass_inserted_edges: set[frozenset[VertexKey]] = set()

        while quadruplets:
            (
                vertex_1_prev,
                vertex_1,
                vertex_2,
                vertex_2_next,
            ) = quadruplets.popleft()

            # "If an edge already exists between two vertices it need not be inserted
            # again. If an edge would cause a self-loop it is not inserted."
            if vertex_1 == vertex_2 or (
                frozenset((vertex_1, vertex_2))
                in inserted_edges.union(pass_inserted_edges)
            ):
                continue

            vertex_1_face: FaceKey | None = None
            vertex_2_face: FaceKey | None = None

            # "Get the list of corners referring to vertex v1 and v2. We will refer to
            # these lists as Cv1 and Cv2 corresponding to v1 and v2 respectively."

            # We list the half-edges that form the rotations of v1 and v2 as they
            # contain the face/vertex pair that forms a corner.
            vertex_1_rotation = list(operators.vertex_trace(mesh, vertex_1))
            vertex_2_rotation = list(operators.vertex_trace(mesh, vertex_2))

            # "If Cv1 contains only 1 corner select that corner. The corner
            # corresponding to c2 is found similarly using Cv2."
            if len(vertex_1_rotation) == 1:
                vertex_1_face = vertex_1_rotation[0].face
            if len(vertex_2_rotation) == 1:
                vertex_2_face = vertex_2_rotation[0].face

            # "To find the corner corresponding to c1, go through Cv1 and find the
            # corner which is preceded by vertex a or followed by vertex b.""
            if vertex_1_face is None:
                for corner_triplet, corner_face in _vertex_rotation_triplets(
                    mesh, vertex_1_rotation
                ):
                    if (
                        corner_triplet[0] == vertex_1_prev
                        or corner_triplet[-1] == vertex_2
                    ):
                        vertex_1_face = corner_face
                        break
            # "The corner corresponding to c2 is found similarly using Cv2."
            if vertex_2_face is None:
                for corner_triplet, corner_face in _vertex_rotation_triplets(
                    mesh, vertex_2_rotation
                ):
                    if (
                        corner_triplet[0] == vertex_1
                        or corner_triplet[-1] == vertex_2_next
                    ):
                        vertex_2_face = corner_face
                        break

            if vertex_1_face is None or vertex_2_face is None and num_null_passes > 2:
                # "If in two successive passes no postponed edges could be
                # resolved, it indicates that the object has multiple 2-manifold
                # interpretations. We choose one of the interpretations arbitrarily
                # by picking the originally tagged corner during the next pass.
                raise NotImplementedError()

            if vertex_1_face is not None and vertex_2_face is not None:
                # "If we can find matching corners for both c1 and c2 in the above step,
                # do the actual edge insertion using the INSERTEDGE operator".
                operators.insert_edge(
                    mesh, vertex_1, vertex_1_face, vertex_2, vertex_2_face
                )
                pass_inserted_edges.add(frozenset((vertex_1, vertex_2)))
            else:
                # "If either of Cv1 or Cv2 contains more than one corner and a matching
                # corner for c1 or c2 cannot be found, postpone insertion of this edge."
                postponed_quadruplets.append(
                    (vertex_1_prev, vertex_1, vertex_2, vertex_2_next)
                )

        inserted_edges.update(pass_inserted_edges)
        num_null_passes = 0 if pass_inserted_edges else num_null_passes + 1

        quadruplets = postponed_quadruplets

    return mesh


def _vertex_rotation_triplets(
    mesh: DLFLMesh, vertex_rotation: list[HalfEdge]
) -> Generator[Tuple[Tuple[VertexKey, VertexKey, VertexKey], FaceKey], None, None]:
    """Returns a generator over corners as vertex triplets in a vertex rotation.

    E.g: rotation(v1) = [
        ((v1, v2), f1), ((v2, v1), f2), ((v1, v3), f3), ..., ((vn, vm), fn)]
         => (vn, v1, v2), (v2, v1, v3), ...
    """
    # The first half-edge in a vertex rotation starts with the passed vertex.
    # We circulate the rotation so it starts with a vertex preceding the passed one.
    # I.e: rotation(v1) = [((v1, v2), f1), ((v2, v1), f2), ((v1, v3), f3), ...]
    #       circulated  = [((v2*, v1*), f2), ((v1, v3*, f3)), ..., ((v1, v2), f1)]
    #          triplets = [(v2, v1, v3), ...]
    for half_edge_1, half_edge_2 in circular_list.pairs(
        circular_list.circulated_to(vertex_rotation, 0)
    ):
        yield (
            half_edge_1.vertices[0],
            half_edge_1.vertices[1],
            half_edge_2.vertices[1],
        ), half_edge_1.face
