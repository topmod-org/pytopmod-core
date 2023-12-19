from typing import Iterable, Tuple, TypeAlias, cast

Point: TypeAlias = Tuple[float, ...]

# Type alias for a 3D point.
Point3D: TypeAlias = Tuple[float, float, float]


def midpoint(point_1: Point, point_2: Point) -> Point:
    """Returns the midpoint between two points."""
    return tuple(sum(pair) / 2.0 for pair in zip(point_1, point_2))


def centroid(points: Iterable[Point]) -> Point:
    """Returns the centroid of a set of points."""
    sum_coords: Tuple[float, ...] = (0.0, 0.0, 0.0)
    num = 0.0
    for point in points:
        sum_coords = tuple(cast(float, sum(pair)) for pair in zip(sum_coords, point))
        num += 1.0
    return tuple(coord / num for coord in sum_coords)
