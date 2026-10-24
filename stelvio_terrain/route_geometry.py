from pyproj import Transformer
from math import radians, cos


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

