from pyproj import Transformer
from math import radians, cos
from pyproj import Geod


def remove_consecutive_duplicates(coordinates):
    if not coordinates:
        return []

    cleaned = [coordinates[0]]

    for point in coordinates[1:]:
        if point[:2] != cleaned[-1][:2]:
            cleaned.append(point)

    return cleaned


def lonlat_to_local_m(lon, lat, origin_lon, origin_lat):
    earth_radius = 6371000.0

    x = (
        earth_radius
        * radians(lon - origin_lon)
        * cos(radians(origin_lat))
    )

    y = earth_radius * radians(lat - origin_lat)

    return x, y



_utm_transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32632",
    always_xy=True,
)


def lonlat_to_local_utm_m(
    lon,
    lat,
    origin_lon,
    origin_lat,
):
    x, y = _utm_transformer.transform(lon, lat)

    origin_x, origin_y = _utm_transformer.transform(
        origin_lon,
        origin_lat,
    )

    return x - origin_x, y - origin_y


def cumulative_route_distances(coordinates):
    """Return cumulative WGS84 distances in metres."""
    

    if not coordinates:
        return []

    geod = Geod(ellps="WGS84")
    distances = [0.0]

    for p1, p2 in zip(coordinates, coordinates[1:]):
        _, _, segment_length = geod.inv(
            p1[0], p1[1],
            p2[0], p2[1],
        )
        distances.append(distances[-1] + segment_length)

    return distances


def build_elevation_profile(distances, elevations):
    """Pair cumulative distances with valid elevations."""
    import math

    if len(distances) != len(elevations):
        raise ValueError(
            "Distances and elevations must have equal length"
        )

    if not all(math.isfinite(z) for z in elevations):
        raise ValueError(
            "Elevations must contain only finite values"
        )
    if not all(math.isfinite(d) for d in distances):
        raise ValueError(
            "Distances must contain only finite values"
        )

    if any(b <= a for a, b in zip(distances, distances[1:])):
        raise ValueError(
            "Distances must be strictly increasing"
        )

    return list(zip(distances, elevations))


def interpolate_elevation(profile, distance):
    """Linearly interpolate elevation at a route distance."""
    if not profile:
        raise ValueError("Elevation profile is empty")

    if distance < profile[0][0] or distance > profile[-1][0]:
        raise ValueError("Distance outside elevation profile")

    for i in range(len(profile) - 1):
        s1, z1 = profile[i]
        s2, z2 = profile[i + 1]

        if s1 <= distance <= s2:
            t = (distance - s1) / (s2 - s1)
            return z1 + t * (z2 - z1)

    return profile[-1][1]





