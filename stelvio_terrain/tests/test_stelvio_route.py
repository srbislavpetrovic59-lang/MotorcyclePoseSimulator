import math
import pytest
import json
from pathlib import Path
from stelvio_terrain.route_geometry import lonlat_to_local_m
from pyproj import Transformer
from stelvio_terrain.route_geometry import lonlat_to_local_utm_m
from pyproj import Geod
from stelvio_terrain.route_geometry import (
        cumulative_route_distances,
    )
from stelvio_terrain.route_geometry import (
        build_elevation_profile,
    )
from stelvio_terrain.route_geometry import (
        interpolate_elevation,
    )
from stelvio_terrain.road_elevation import (
        detect_elevation_spikes,
    )
from stelvio_terrain.road_elevation import calculate_road_grade

def test_stelvio_route_geojson_exists():
    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    assert route_file.is_file()


def test_stelvio_route_has_coordinates():
    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    assert data["type"] in ("FeatureCollection", "Feature")




def test_stelvio_route_has_line_geometry():
    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    if data["type"] == "FeatureCollection":
        features = data["features"]
    else:
        features = [data]

    geometries = [feature["geometry"] for feature in features]

    assert any(
        geometry["type"] in ("LineString", "MultiLineString")
        and len(geometry["coordinates"]) >= 2
        for geometry in geometries
    )




from math import radians, sin, cos, asin, sqrt


def haversine_distance(a, b):
    lon1, lat1 = map(radians, a[:2])
    lon2, lat2 = map(radians, b[:2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    h = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    return 2 * 6371000 * asin(sqrt(min(1.0, h)))


def test_stelvio_route_length():
    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    features = (
        data["features"]
        if data["type"] == "FeatureCollection"
        else [data]
    )

    lines = []

    for feature in features:
        geometry = feature["geometry"]

        if geometry["type"] == "LineString":
            lines.append(geometry["coordinates"])
        elif geometry["type"] == "MultiLineString":
            lines.extend(geometry["coordinates"])

    assert lines, "Nema linijske geometrije"

    length_m = sum(
        haversine_distance(a, b)
        for line in lines
        for a, b in zip(line, line[1:])
    )

    print(f"\nStelvio route length: {length_m / 1000:.3f} km")

    assert 20_000 < length_m < 35_000



def test_stelvio_route_point_count():
    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    features = (
        data["features"]
        if data["type"] == "FeatureCollection"
        else [data]
    )

    point_count = 0

    for feature in features:
        geometry = feature["geometry"]

        if geometry["type"] == "LineString":
            point_count += len(geometry["coordinates"])

        elif geometry["type"] == "MultiLineString":
            point_count += sum(
                len(line)
                for line in geometry["coordinates"]
            )

    print(f"\nStelvio route points: {point_count}")

    assert point_count >= 2

def test_stelvio_route_segment_lengths():
    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    features = (
        data["features"]
        if data["type"] == "FeatureCollection"
        else [data]
    )

    lengths = []

    for feature in features:
        geometry = feature["geometry"]

        if geometry["type"] == "LineString":
            lines = [geometry["coordinates"]]
        elif geometry["type"] == "MultiLineString":
            lines = geometry["coordinates"]
        else:
            continue

        for line in lines:
            cleaned = remove_consecutive_duplicates(line)

            lengths.extend(
                haversine_distance(a, b)
                for a, b in zip(cleaned, cleaned[1:])
            )

    assert lengths, "Nema segmenata puta"

    print(f"\nShortest segment: {min(lengths):.2f} m")
    print(f"Longest segment:  {max(lengths):.2f} m")
    print(f"Average segment:  {sum(lengths) / len(lengths):.2f} m")
    
    zero_segments = sum(length == 0 for length in lengths)

    print(f"Zero-length segments: {zero_segments}")
    
    #assert all(length > 0 for length in lengths)
    assert zero_segments == 0, (
        f"Found {zero_segments} zero-length segments"
    )


from stelvio_terrain.route_geometry import (
    remove_consecutive_duplicates,
)


def test_remove_consecutive_duplicates():
    coordinates = [
        [10.0, 46.0],
        [10.0, 46.0],
        [10.1, 46.1],
        [10.1, 46.1],
        [10.2, 46.2],
    ]

    cleaned = remove_consecutive_duplicates(coordinates)

    assert cleaned == [
        [10.0, 46.0],
        [10.1, 46.1],
        [10.2, 46.2],
    ]




def test_stelvio_route_cleaning_preserves_length():
    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    features = (
        data["features"]
        if data["type"] == "FeatureCollection"
        else [data]
    )

    original_length = 0.0
    cleaned_length = 0.0
    original_points = 0
    cleaned_points = 0

    for feature in features:
        geometry = feature["geometry"]

        if geometry["type"] == "LineString":
            lines = [geometry["coordinates"]]
        elif geometry["type"] == "MultiLineString":
            lines = geometry["coordinates"]
        else:
            continue

        for line in lines:
            cleaned = remove_consecutive_duplicates(line)

            original_points += len(line)
            cleaned_points += len(cleaned)

            original_length += sum(
                haversine_distance(a, b)
                for a, b in zip(line, line[1:])
            )

            cleaned_length += sum(
                haversine_distance(a, b)
                for a, b in zip(cleaned, cleaned[1:])
            )

            assert all(
                haversine_distance(a, b) > 0
                for a, b in zip(cleaned, cleaned[1:])
            )

    print(f"\nOriginal points: {original_points}")
    print(f"Cleaned points:  {cleaned_points}")
    print(f"Removed points:  {original_points - cleaned_points}")
    print(f"Original length: {original_length / 1000:.3f} km")
    print(f"Cleaned length:  {cleaned_length / 1000:.3f} km")

    assert cleaned_points < original_points
    assert abs(original_length - cleaned_length) < 0.001



def test_stelvio_longest_segment_location():
    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    features = (
        data["features"]
        if data["type"] == "FeatureCollection"
        else [data]
    )

    longest = (0.0, None, None)

    for feature in features:
        geometry = feature["geometry"]

        if geometry["type"] == "LineString":
            lines = [geometry["coordinates"]]
        elif geometry["type"] == "MultiLineString":
            lines = geometry["coordinates"]
        else:
            continue

        for line in lines:
            cleaned = remove_consecutive_duplicates(line)

            for a, b in zip(cleaned, cleaned[1:]):
                distance = haversine_distance(a, b)

                if distance > longest[0]:
                    longest = (distance, a, b)

    distance, start, end = longest

    assert start is not None
    assert end is not None

    print(f"\nLongest segment: {distance:.2f} m")
    print(f"Start (lon, lat): {start[:2]}")
    print(f"End   (lon, lat): {end[:2]}")

    assert distance < 200



def test_stelvio_route_bounds():
    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    features = (
        data["features"]
        if data["type"] == "FeatureCollection"
        else [data]
    )

    coordinates = []

    for feature in features:
        geometry = feature["geometry"]

        if geometry["type"] == "LineString":
            lines = [geometry["coordinates"]]
        elif geometry["type"] == "MultiLineString":
            lines = geometry["coordinates"]
        else:
            continue

        for line in lines:
            coordinates.extend(remove_consecutive_duplicates(line))

    assert coordinates

    longitudes = [point[0] for point in coordinates]
    latitudes = [point[1] for point in coordinates]

    print(f"\nWest:  {min(longitudes):.6f}")
    print(f"East:  {max(longitudes):.6f}")
    print(f"South: {min(latitudes):.6f}")
    print(f"North: {max(latitudes):.6f}")

    assert min(longitudes) < max(longitudes)
    assert min(latitudes) < max(latitudes)


def test_stelvio_terrain_dimensions():
    west = 10.452940
    east = 10.595260
    south = 46.528620
    north = 46.616820

    center_lat = (south + north) / 2
    center_lon = (west + east) / 2

    width_m = haversine_distance(
        (west, center_lat),
        (east, center_lat),
    )

    height_m = haversine_distance(
        (center_lon, south),
        (center_lon, north),
    )

    print(f"\nTerrain width:  {width_m / 1000:.3f} km")
    print(f"Terrain height: {height_m / 1000:.3f} km")

    assert 10_000 < width_m < 12_000
    assert 9_000 < height_m < 11_000



def test_lonlat_to_local_origin():
    origin_lon = 10.5241
    origin_lat = 46.5727

    x, y = lonlat_to_local_m(
        origin_lon,
        origin_lat,
        origin_lon,
        origin_lat,
    )

    assert x == 0.0
    assert y == 0.0



def test_lonlat_to_local_directions():
    origin_lon = 10.5241
    origin_lat = 46.5727

    # Tačka približno 100 m istočno
    east_lon = origin_lon + 0.001307

    east_x, east_y = lonlat_to_local_m(
        east_lon,
        origin_lat,
        origin_lon,
        origin_lat,
    )

    # Tačka približno 100 m severno
    north_lat = origin_lat + 0.000899

    north_x, north_y = lonlat_to_local_m(
        origin_lon,
        north_lat,
        origin_lon,
        origin_lat,
    )

    print(f"\nEast:  x={east_x:.2f}, y={east_y:.2f}")
    print(f"North: x={north_x:.2f}, y={north_y:.2f}")

    assert 99 < east_x < 101
    assert abs(east_y) < 0.001

    assert abs(north_x) < 0.001
    assert 99 < north_y < 101



def test_stelvio_route_local_coordinates():
    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    features = (
        data["features"]
        if data["type"] == "FeatureCollection"
        else [data]
    )

    origin_lon = 10.5241
    origin_lat = 46.5727

    local_points = []

    for feature in features:
        geometry = feature["geometry"]

        if geometry["type"] == "LineString":
            lines = [geometry["coordinates"]]
        elif geometry["type"] == "MultiLineString":
            lines = geometry["coordinates"]
        else:
            continue

        for line in lines:
            cleaned = remove_consecutive_duplicates(line)

            for lon, lat, *_ in cleaned:
                x, y = lonlat_to_local_m(
                    lon,
                    lat,
                    origin_lon,
                    origin_lat,
                )
                local_points.append((x, y))

    print(f"\nLocal points: {len(local_points)}")
    print(f"X range: {min(p[0] for p in local_points):.1f}"
          f" to {max(p[0] for p in local_points):.1f} m")
    print(f"Y range: {min(p[1] for p in local_points):.1f}"
          f" to {max(p[1] for p in local_points):.1f} m")

    assert len(local_points) == 2923
    assert all(
        abs(x) < 6000 and abs(y) < 6000
        for x, y in local_points
    )



def test_local_projection_distance():
    origin_lon = 10.5241
    origin_lat = 46.5727

    # Dve stvarne tačke sa trase Stelvija
    a = (10.58164, 46.61261)
    b = (10.57998, 46.61158)

    geographic_distance = haversine_distance(a, b)

    ax, ay = lonlat_to_local_m(
        *a, origin_lon, origin_lat
    )
    bx, by = lonlat_to_local_m(
        *b, origin_lon, origin_lat
    )

    local_distance = (
        (bx - ax) ** 2 + (by - ay) ** 2
    ) ** 0.5

    error = abs(local_distance - geographic_distance)

    print(f"\nGeographic distance: {geographic_distance:.3f} m")
    print(f"Local distance:      {local_distance:.3f} m")
    print(f"Difference:          {error:.3f} m")

    assert error < 1.0



def test_stelvio_total_local_distance():
    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    features = (
        data["features"]
        if data["type"] == "FeatureCollection"
        else [data]
    )

    origin_lon = 10.5241
    origin_lat = 46.5727

    geographic_total = 0.0
    local_total = 0.0

    for feature in features:
        geometry = feature["geometry"]

        if geometry["type"] == "LineString":
            lines = [geometry["coordinates"]]
        elif geometry["type"] == "MultiLineString":
            lines = geometry["coordinates"]
        else:
            continue

        for line in lines:
            cleaned = remove_consecutive_duplicates(line)

            for a, b in zip(cleaned, cleaned[1:]):
                geographic_total += haversine_distance(a, b)

                ax, ay = lonlat_to_local_m(
                    a[0], a[1], origin_lon, origin_lat
                )
                bx, by = lonlat_to_local_m(
                    b[0], b[1], origin_lon, origin_lat
                )

                local_total += (
                    (bx - ax) ** 2 + (by - ay) ** 2
                ) ** 0.5

    difference = local_total - geographic_total

    print(f"\nGeographic total: {geographic_total:.3f} m")
    print(f"Local total:      {local_total:.3f} m")
    print(f"Difference:       {difference:.3f} m")
    print(
        f"Relative error:   "
        f"{abs(difference) / geographic_total * 100:.4f}%"
    )

    assert geographic_total > 0
    assert abs(difference) / geographic_total < 0.01


def test_stelvio_utm_projection():
    transformer = Transformer.from_crs(
        "EPSG:4326",
        "EPSG:32632",
        always_xy=True,
    )

    lon = 10.5241
    lat = 46.5727

    x, y = transformer.transform(lon, lat)

    print(f"\nUTM Easting:  {x:.3f} m")
    print(f"UTM Northing: {y:.3f} m")

    assert 500_000 < x < 700_000
    assert 5_000_000 < y < 5_300_000


def test_local_utm_origin_and_directions():
    origin_lon = 10.5241
    origin_lat = 46.5727

    x0, y0 = lonlat_to_local_utm_m(
        origin_lon, origin_lat,
        origin_lon, origin_lat,
    )

    east_x, east_y = lonlat_to_local_utm_m(
        origin_lon + 0.001,
        origin_lat,
        origin_lon, origin_lat,
    )

    north_x, north_y = lonlat_to_local_utm_m(
        origin_lon,
        origin_lat + 0.001,
        origin_lon, origin_lat,
    )

    print(f"\nOrigin: ({x0:.3f}, {y0:.3f})")
    print(f"East:   ({east_x:.3f}, {east_y:.3f})")
    print(f"North:  ({north_x:.3f}, {north_y:.3f})")

    assert abs(x0) < 0.001
    assert abs(y0) < 0.001

    assert east_x > 0
    assert north_y > 0



def test_local_projection_vs_utm():
    origin_lon = 10.5241
    origin_lat = 46.5727

    points = {
        "West":  (10.452940, origin_lat),
        "East":  (10.595260, origin_lat),
        "South": (origin_lon, 46.528620),
        "North": (origin_lon, 46.616820),
    }

    for name, (lon, lat) in points.items():
        old_x, old_y = lonlat_to_local_m(
            lon, lat, origin_lon, origin_lat
        )

        utm_x, utm_y = lonlat_to_local_utm_m(
            lon, lat, origin_lon, origin_lat
        )

        difference = (
            (utm_x - old_x) ** 2
            + (utm_y - old_y) ** 2
        ) ** 0.5

        print(
            f"\n{name}: "
            f"old=({old_x:.2f}, {old_y:.2f}), "
            f"UTM=({utm_x:.2f}, {utm_y:.2f}), "
            f"difference={difference:.2f} m"
        )

        assert difference < 200


def test_stelvio_total_utm_distance():
    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    features = (
        data["features"]
        if data["type"] == "FeatureCollection"
        else [data]
    )

    origin_lon = 10.5241
    origin_lat = 46.5727

    geographic_total = 0.0
    utm_total = 0.0

    for feature in features:
        geometry = feature["geometry"]

        if geometry["type"] == "LineString":
            lines = [geometry["coordinates"]]
        elif geometry["type"] == "MultiLineString":
            lines = geometry["coordinates"]
        else:
            continue

        for line in lines:
            cleaned = remove_consecutive_duplicates(line)

            for a, b in zip(cleaned, cleaned[1:]):
                geographic_total += haversine_distance(a, b)

                ax, ay = lonlat_to_local_utm_m(
                    a[0], a[1], origin_lon, origin_lat
                )
                bx, by = lonlat_to_local_utm_m(
                    b[0], b[1], origin_lon, origin_lat
                )

                utm_total += (
                    (bx - ax) ** 2 + (by - ay) ** 2
                ) ** 0.5

    difference = utm_total - geographic_total

    print(f"\nGeographic length: {geographic_total:.3f} m")
    print(f"UTM length:        {utm_total:.3f} m")
    print(f"Difference:        {difference:.3f} m")
    print(
        f"Relative difference: "
        f"{abs(difference) / geographic_total * 100:.4f}%"
    )

    assert geographic_total > 0
    assert abs(difference) / geographic_total < 0.01


def test_stelvio_utm_vs_geodesic():
    geod = Geod(ellps="WGS84")

    route_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "stelvio_east_route.geojson"
    )

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    features = (
        data["features"]
        if data["type"] == "FeatureCollection"
        else [data]
    )

    geodesic_total = 0.0
    utm_total = 0.0

    for feature in features:
        geometry = feature["geometry"]

        if geometry["type"] == "LineString":
            lines = [geometry["coordinates"]]
        elif geometry["type"] == "MultiLineString":
            lines = geometry["coordinates"]
        else:
            continue

        for line in lines:
            cleaned = remove_consecutive_duplicates(line)

            for a, b in zip(cleaned, cleaned[1:]):
                _, _, distance = geod.inv(
                    a[0], a[1], b[0], b[1]
                )
                geodesic_total += distance

                ax, ay = lonlat_to_local_utm_m(
                    a[0], a[1], 10.5241, 46.5727
                )
                bx, by = lonlat_to_local_utm_m(
                    b[0], b[1], 10.5241, 46.5727
                )

                utm_total += (
                    (bx - ax) ** 2
                    + (by - ay) ** 2
                ) ** 0.5

    difference = utm_total - geodesic_total

    print(f"\nGeodesic length: {geodesic_total:.3f} m")
    print(f"UTM length:      {utm_total:.3f} m")
    print(f"Difference:      {difference:.3f} m")
    print(
        f"Relative error:  "
        f"{abs(difference) / geodesic_total * 100:.4f}%"
    )

    assert abs(difference) / geodesic_total < 0.001


def test_rasterio_available():
    import rasterio

    assert rasterio.__version__



def test_stelvio_dem_sample():
    import rasterio
    import math

    dem_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "dem"
        / "output_hh.tif"
    )

    lon = 10.5241
    lat = 46.5727

    with rasterio.open(dem_file) as dem:
        assert dem.crs.to_epsg() == 4326

        assert (
            dem.bounds.left <= lon <= dem.bounds.right
            and dem.bounds.bottom <= lat <= dem.bounds.top
        )

        elevation = next(dem.sample([(lon, lat)]))[0]

    print(f"\nDEM elevation: {elevation:.2f} m")

    assert math.isfinite(float(elevation))
    assert 500 < elevation < 4000


def test_stelvio_route_elevation_profile():
    import rasterio
    import math

    base = Path(__file__).resolve().parents[1]

    route_file = base / "data" / "stelvio_east_route.geojson"
    dem_file = base / "data" / "dem" / "output_hh.tif"

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    features = (
        data["features"]
        if data["type"] == "FeatureCollection"
        else [data]
    )

    coordinates = []

    for feature in features:
        geometry = feature["geometry"]

        if geometry["type"] == "LineString":
            lines = [geometry["coordinates"]]
        elif geometry["type"] == "MultiLineString":
            lines = geometry["coordinates"]
        else:
            continue

        for line in lines:
            coordinates.extend(
                remove_consecutive_duplicates(line)
            )

    with rasterio.open(dem_file) as dem:
        assert dem.crs.to_epsg() == 4326

        samples = list(dem.sample(
            [(p[0], p[1]) for p in coordinates],
            masked=True,
        ))

    elevations = [float(s[0]) for s in samples]

    assert len(elevations) == 2923
    assert all(math.isfinite(z) for z in elevations)
    assert all(not bool(s.mask.any()) for s in samples)

    print(f"\nRoute points: {len(elevations)}")
    print(f"Start elevation: {elevations[0]:.2f} m")
    print(f"End elevation:   {elevations[-1]:.2f} m")
    print(f"Minimum:         {min(elevations):.2f} m")
    print(f"Maximum:         {max(elevations):.2f} m")
    min_index = elevations.index(min(elevations))

    print(f"Minimum index: {min_index}")
    print(f"Minimum coordinates: {coordinates[min_index]}")
    print(f"Minimum route position: {min_index / (len(elevations) - 1) * 100:.1f}% of points")
    height_differences = [
        abs(elevations[i + 1] - elevations[i])
        for i in range(len(elevations) - 1)
    ]

    max_jump = max(height_differences)
    max_jump_index = height_differences.index(max_jump)

    print(f"Maximum height jump: {max_jump:.2f} m")
    print(f"Jump between points: {max_jump_index} and {max_jump_index + 1}")
    print(f"Elevation before: {elevations[max_jump_index]:.2f} m")
    print(f"Elevation after:  {elevations[max_jump_index + 1]:.2f} m")
    

    geod = Geod(ellps="WGS84")

    p1 = coordinates[max_jump_index]
    p2 = coordinates[max_jump_index + 1]

    _, _, distance = geod.inv(
        p1[0], p1[1],
        p2[0], p2[1],
    )

    height_change = (
        elevations[max_jump_index + 1]
        - elevations[max_jump_index]
    )

    grade_percent = (
        100.0 * height_change / distance
        if distance > 0
        else float("nan")
    )

    print(f"Horizontal distance: {distance:.2f} m")
    print(f"Height change:       {height_change:+.2f} m")
    print(f"Calculated grade:    {grade_percent:+.1f}%")
    print(f"Point 1: {p1}")
    print(f"Point 2: {p2}")
    print("\nElevation around maximum jump:")

    for i in range(max_jump_index - 5, max_jump_index + 7):
        print(
            f"{i:4d} | "
            f"{elevations[i]:8.2f} m | "
            f"{coordinates[i]}"
        )

    grades = []

    for i in range(len(coordinates) - 1):
        p1 = coordinates[i]
        p2 = coordinates[i + 1]

        _, _, distance = geod.inv(
            p1[0], p1[1],
            p2[0], p2[1],
        )

        if distance > 0:
            grade = (
                100.0
                * (elevations[i + 1] - elevations[i])
                / distance
            )
            grades.append(abs(grade))

    print("\nDEM grade statistics:")
    print(f"Segments:      {len(grades)}")
    print(f"Above 15%:     {sum(g > 15 for g in grades)}")
    print(f"Above 30%:     {sum(g > 30 for g in grades)}")
    print(f"Above 100%:    {sum(g > 100 for g in grades)}")
    print(f"Maximum grade: {max(grades):.1f}%")

    print("\nRoute endpoints:")
    print(f"Start: {coordinates[0]}")
    print(f"Minimum: {coordinates[min_index]}")
    print(f"End: {coordinates[-1]}")

    segment_distances = []

    for i in range(len(coordinates) - 1):
        p1 = coordinates[i]
        p2 = coordinates[i + 1]

        _, _, distance = geod.inv(
            p1[0], p1[1],
            p2[0], p2[1],
        )

        segment_distances.append(distance)

    distance_to_minimum = sum(segment_distances[:min_index])
    distance_after_minimum = sum(segment_distances[min_index:])

    print("\nRoute distances:")
    print(f"Before minimum: {distance_to_minimum / 1000:.3f} km")
    print(f"After minimum:  {distance_after_minimum / 1000:.3f} km")
    print(f"Total:          {sum(segment_distances) / 1000:.3f} km")
    from stelvio_terrain.route_geometry import (
        cumulative_route_distances,
        build_elevation_profile,
    )
    from stelvio_terrain.road_elevation import (
        detect_elevation_spikes,
    )

    distances = cumulative_route_distances(coordinates)

    profile = build_elevation_profile(
        distances,
        elevations,
    )

    spikes = detect_elevation_spikes(
        profile,
        threshold_m=10.0,
    )

    print("\nStelvio elevation anomalies:")
    print(f"Route points:       {len(profile)}")
    print(f"Suspected points:   {len(spikes)}")
    print(f"Percentage:         {100 * len(spikes) / len(profile):.2f}%")

    print("\nFirst 10 suspected points:")

    for i in spikes[:10]:
        print(
            f"Index {i:4d} | "
            f"km {distances[i] / 1000:6.3f} | "
            f"Z = {elevations[i]:8.2f} m"
        )
    print("\nMaximum jump detection:")
    print(f"Point 1694 detected: {1694 in spikes}")
    print(f"Point 1695 detected: {1695 in spikes}")
    print("\nSuspected points around maximum jump:")
    from stelvio_terrain.road_elevation import (
        group_consecutive_spikes,
    )

    groups = group_consecutive_spikes(spikes)
    from stelvio_terrain.road_elevation import (
        expand_spike_interval,
    )

    zones = []

    for start, end in groups:
        zone_start, zone_end = expand_spike_interval(
            start,
            end,
            len(profile),
        )

        length_m = (
            distances[zone_end] - distances[zone_start]
        )

        zones.append(
            (zone_start, zone_end, length_m)
        )

    zones.sort(key=lambda zone: zone[2], reverse=True)
    from stelvio_terrain.road_elevation import (
    merge_spike_zones,
    )

    zone_intervals = [
        (start, end)
        for start, end, length_m in zones
    ]

    merged_zones = merge_spike_zones(zone_intervals)

    print("\nStelvio merged anomaly zones:")
    print(f"Before merging: {len(zones)}")
    print(f"After merging:  {len(merged_zones)}")

    total_length_m = sum(
        distances[end] - distances[start]
        for start, end in merged_zones
    )

    print(f"Total zone length: {total_length_m:.1f} m")
    print(
        f"Route coverage: "
        f"{100 * total_length_m / distances[-1]:.2f}%"
    )
    print("\nStelvio expanded anomaly zones:")
    print(f"Number of zones: {len(zones)}")

    print("\n10 longest zones:")

    for start, end, length_m in zones[:10]:
        print(
            f"{start:4d} - {end:4d} | "
            f"km {distances[start] / 1000:6.3f} | "
            f"length {length_m:6.1f} m"
        )
    print("\nStelvio suspected intervals:")
    print(f"Number of intervals: {len(groups)}")

    print("\nFirst 10 intervals:")

    for start, end in groups[:10]:
        length_m = distances[end] - distances[start]

        print(
            f"{start:4d} - {end:4d} | "
            f"km {distances[start] / 1000:6.3f} | "
            f"length {length_m:6.1f} m | "
            f"points {end - start + 1}"
        )
    for i in range(1689, 1701):
        print(
            f"{i:4d} | "
            f"Z = {elevations[i]:8.2f} m | "
            f"Suspected = {i in spikes}"
        )

def test_cumulative_route_distances():
    

    coordinates = [
        [10.0, 46.0],
        [10.001, 46.0],
        [10.002, 46.0],
    ]

    distances = cumulative_route_distances(coordinates)

    assert len(distances) == 3
    assert distances[0] == 0.0
    assert distances[1] > 0.0
    assert distances[2] > distances[1]
    assert 150.0 < distances[-1] < 160.0

def test_stelvio_cumulative_distances():
    

    base = Path(__file__).resolve().parents[1]
    route_file = base / "data" / "stelvio_east_route.geojson"

    with route_file.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    geometry = (
        data["geometry"]
        if data["type"] == "Feature"
        else data
    )

    coordinates = geometry["coordinates"]
    coordinates = remove_consecutive_duplicates(coordinates)

    distances = cumulative_route_distances(coordinates)

    assert len(distances) == 2923
    assert distances[0] == 0.0
    assert all(
        b > a
        for a, b in zip(distances, distances[1:])
    )
    assert abs(distances[-1] - 29283.648) < 1.0

    print(f"\nTotal route: {distances[-1]:.3f} m")
    print(f"Minimum point: {distances[367]:.3f} m")


def test_build_elevation_profile():
   

    distances = [0.0, 10.0, 25.0]
    elevations = [1000.0, 1001.0, 1003.0]

    profile = build_elevation_profile(
        distances,
        elevations,
    )

    assert profile == [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (25.0, 1003.0),
    ]


def test_build_elevation_profile_rejects_invalid_heights():
    import pytest
    

    with pytest.raises(ValueError):
        build_elevation_profile(
            [0.0, 10.0],
            [1000.0, float("nan")],
        )

    with pytest.raises(ValueError):
        build_elevation_profile(
            [0.0, 10.0],
            [1000.0, float("inf")],
        )

def test_build_elevation_profile_rejects_non_increasing_distances():
    import pytest
    from stelvio_terrain.route_geometry import (
        build_elevation_profile,
    )

    with pytest.raises(ValueError):
        build_elevation_profile(
            [0.0, 10.0, 10.0],
            [1000.0, 1001.0, 1002.0],
        )

    with pytest.raises(ValueError):
        build_elevation_profile(
            [0.0, 20.0, 15.0],
            [1000.0, 1002.0, 1001.0],
        )


def test_interpolate_elevation():
    from stelvio_terrain.route_geometry import (
        interpolate_elevation,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1002.0),
        (30.0, 1006.0),
    ]

    assert interpolate_elevation(profile, 0.0) == 1000.0
    assert interpolate_elevation(profile, 5.0) == 1001.0
    assert interpolate_elevation(profile, 10.0) == 1002.0
    assert interpolate_elevation(profile, 20.0) == 1004.0
    assert interpolate_elevation(profile, 30.0) == 1006.0

def test_interpolate_elevation_preserves_known_points():
    

    profile = [
        (0.0, 1000.0),
        (7.5, 1002.5),
        (23.0, 1005.0),
        (40.0, 1004.0),
    ]

    for distance, elevation in profile:
        assert interpolate_elevation(profile, distance) == elevation


def test_detect_elevation_spike():
    from stelvio_terrain.road_elevation import (
        detect_elevation_spikes,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1035.0),
        (30.0, 1003.0),
        (40.0, 1004.0),
    ]

    spikes = detect_elevation_spikes(
        profile,
        threshold_m=10.0,
    )

    assert spikes == [2]

    # Originalni podaci ostaju nepromenjeni.
    assert profile[2] == (20.0, 1035.0)


def test_detect_elevation_spikes_preserves_normal_climb():
    

    # Ravnomeran uspon od 10%.
    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1002.0),
        (30.0, 1003.0),
        (40.0, 1004.0),
    ]

    spikes = detect_elevation_spikes(
        profile,
        threshold_m=10.0,
    )

    assert spikes == []

def test_detect_elevation_spikes_preserves_grade_transition():
    from stelvio_terrain.road_elevation import (
        detect_elevation_spikes,
    )

    # Prvih 20 m: uspon 5%.
    # Sledećih 20 m: uspon 15%.
    profile = [
        (0.0, 1000.0),
        (10.0, 1000.5),
        (20.0, 1001.0),
        (30.0, 1002.5),
        (40.0, 1004.0),
    ]

    spikes = detect_elevation_spikes(
        profile,
        threshold_m=10.0,
    )

    assert spikes == []


def test_detect_elevation_spikes_two_consecutive_anomalies():
    from stelvio_terrain.road_elevation import (
        detect_elevation_spikes,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1035.0),
        (30.0, 1036.0),
        (40.0, 1004.0),
        (50.0, 1005.0),
    ]

    spikes = detect_elevation_spikes(
        profile,
        threshold_m=10.0,
    )

    assert spikes == [2, 3]
    height_changes = [
        profile[i + 1][1] - profile[i][1]
        for i in range(len(profile) - 1)
    ]

    print(f"\nHeight changes: {height_changes}")
    print(f"Detected spikes: {spikes}")


def test_detect_elevation_spikes_preserves_long_climb():
    from stelvio_terrain.road_elevation import (
        detect_elevation_spikes,
    )

    # Visinski uspon i silazak na velikoj udaljenosti.
    # Nagibi su samo 5%, iako je promena visine 20 m.
    profile = [
        (0.0, 1000.0),
        (400.0, 1020.0),
        (800.0, 1000.0),
    ]

    spikes = detect_elevation_spikes(
        profile,
        threshold_m=10.0,
    )

    assert spikes == []
   

def test_group_consecutive_spikes():
    from stelvio_terrain.road_elevation import (
        group_consecutive_spikes,
    )

    spikes = [
        59, 110, 183, 184, 185, 186, 1695, 1696
    ]

    groups = group_consecutive_spikes(spikes)

    assert groups == [
        (59, 59),
        (110, 110),
        (183, 186),
        (1695, 1696),
    ]


def test_expand_spike_interval_to_neighbors():
    from stelvio_terrain.road_elevation import (
        expand_spike_interval,
    )

    assert expand_spike_interval(
        start=1695,
        end=1696,
        point_count=2923,
    ) == (1694, 1697)

    # Interval na početku trase.
    assert expand_spike_interval(
        start=0,
        end=1,
        point_count=100,
    ) == (0, 2)

    # Interval na kraju trase.
    assert expand_spike_interval(
        start=98,
        end=99,
        point_count=100,
    ) == (97, 99)


def test_merge_overlapping_spike_zones():
    from stelvio_terrain.road_elevation import (
        merge_spike_zones,
    )

    zones = [
        (10, 15),
        (14, 20),
        (30, 35),
        (36, 40),
        (50, 55),
    ]

    merged = merge_spike_zones(zones)

    assert merged == [
        (10, 20),
        (30, 40),
        (50, 55),
    ]


def test_merge_spike_zones_preserves_coverage():
    from stelvio_terrain.road_elevation import (
        merge_spike_zones,
    )

    distances = [
        0.0, 10.0, 20.0, 30.0,
        40.0, 50.0, 60.0,
    ]

    zones = [
        (1, 3),
        (2, 4),
        (5, 6),
    ]

    merged = merge_spike_zones(zones)

    assert merged == [(1, 6)]

    total_length = sum(
        distances[end] - distances[start]
        for start, end in merged
    )

    assert total_length == 50.0


def test_interpolate_road_elevation_zone():
    from stelvio_terrain.road_elevation import (
        interpolate_road_elevation_zone,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1035.0),
        (20.0, 1036.0),
        (30.0, 1003.0),
    ]

    corrected = interpolate_road_elevation_zone(
        profile,
        start=1,
        end=2,
    )

    assert corrected == [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1002.0),
        (30.0, 1003.0),
    ]

    # Originalni profil mora ostati netaknut.
    assert profile[1][1] == 1035.0
    assert profile[2][1] == 1036.0



def test_calculate_road_grade():
    from stelvio_terrain.road_elevation import (
        calculate_road_grade,
    )

    # Uspon od 10%.
    assert calculate_road_grade(
        (0.0, 1000.0),
        (100.0, 1010.0),
    ) == pytest.approx(0.10)

    # Spust od 5%.
    assert calculate_road_grade(
        (0.0, 1000.0),
        (100.0, 995.0),
    ) == pytest.approx(-0.05)

    # Horizontalni put.
    assert calculate_road_grade(
        (0.0, 1000.0),
        (100.0, 1000.0),
    ) == pytest.approx(0.0)

    # Nulta dužina segmenta nije dozvoljena.
    with pytest.raises(ValueError):
        calculate_road_grade(
            (0.0, 1000.0),
            (0.0, 1010.0),
        )



def test_max_road_grade_in_zone():
    from stelvio_terrain.road_elevation import (
        max_road_grade_in_zone,
    )

    profile = [
        (0.0, 1000.0),
        (100.0, 1005.0),
        (200.0, 1015.0),
        (300.0, 1007.0),
    ]

    max_grade = max_road_grade_in_zone(
        profile,
        start=0,
        end=3,
    )

    assert max_grade == pytest.approx(0.10)



def test_is_road_grade_acceptable():
    from stelvio_terrain.road_elevation import (
        is_road_grade_acceptable,
    )

    profile = [
        (0.0, 1000.0),
        (100.0, 1005.0),
        (200.0, 1015.0),
        (300.0, 1007.0),
    ]

    assert is_road_grade_acceptable(
        profile, start=0, end=3, max_allowed_grade=0.12
    ) is True

    assert is_road_grade_acceptable(
        profile, start=0, end=3, max_allowed_grade=0.08
    ) is False

    # Tačno na dozvoljenoj granici.
    assert is_road_grade_acceptable(
        profile, start=0, end=3, max_allowed_grade=0.10
    ) is True



def test_reconstruct_road_zone_with_grade_limit():
    from stelvio_terrain.road_elevation import (
        reconstruct_road_zone,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1035.0),
        (20.0, 1036.0),
        (30.0, 1003.0),
    ]

    corrected = reconstruct_road_zone(
        profile,
        start=1,
        end=2,
        max_allowed_grade=0.12,
    )

    assert corrected == [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1002.0),
        (30.0, 1003.0),
    ]

    # Stroži prag mora odbiti rekonstrukciju.
    with pytest.raises(ValueError):
        reconstruct_road_zone(
            profile,
            start=1,
            end=2,
            max_allowed_grade=0.08,
        )

    # Izvorni podaci ostaju nepromenjeni.
    assert profile[1][1] == 1035.0
    assert profile[2][1] == 1036.0



def test_reconstruct_road_zone_rejects_suspect_boundaries():
    from stelvio_terrain.road_elevation import (
        reconstruct_road_zone,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1035.0),
        (20.0, 1036.0),
        (30.0, 1003.0),
    ]

    with pytest.raises(ValueError):
        reconstruct_road_zone(
            profile,
            start=1,
            end=2,
            max_allowed_grade=0.12,
            suspect_indices={0},
        )

    with pytest.raises(ValueError):
        reconstruct_road_zone(
            profile,
            start=1,
            end=2,
            max_allowed_grade=0.12,
            suspect_indices={3},
        )


def test_reconstruct_road_zone_requires_verified_boundaries():
    from stelvio_terrain.road_elevation import (
        reconstruct_road_zone,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1035.0),
        (20.0, 1036.0),
        (30.0, 1003.0),
    ]

    # Obe granične tačke su potvrđene.
    corrected = reconstruct_road_zone(
        profile,
        start=1,
        end=2,
        max_allowed_grade=0.12,
        verified_indices={0, 3},
    )

    assert corrected[1][1] == pytest.approx(1001.0)
    assert corrected[2][1] == pytest.approx(1002.0)

    # Desna granična tačka nije potvrđena.
    with pytest.raises(ValueError):
        reconstruct_road_zone(
            profile,
            start=1,
            end=2,
            max_allowed_grade=0.12,
            verified_indices={0},
        )

    # Nijedna granična tačka nije potvrđena.
    with pytest.raises(ValueError):
        reconstruct_road_zone(
            profile,
            start=1,
            end=2,
            max_allowed_grade=0.12,
            verified_indices=set(),
        )



def test_road_elevation_reference():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
    )

    reference = RoadElevationReference(
        point_index=1694,
        elevation_m=1905.0,
        source="survey",
        verified=True,
    )

    assert reference.point_index == 1694
    assert reference.elevation_m == 1905.0
    assert reference.source == "survey"
    assert reference.verified is True



def test_get_verified_reference_indices():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        get_verified_reference_indices,
    )

    references = [
        RoadElevationReference(
            point_index=100,
            elevation_m=1200.0,
            source="survey",
            verified=True,
        ),
        RoadElevationReference(
            point_index=200,
            elevation_m=1300.0,
            source="DEM",
            verified=False,
        ),
        RoadElevationReference(
            point_index=300,
            elevation_m=1400.0,
            source="survey",
            verified=True,
        ),
    ]

    result = get_verified_reference_indices(references)

    assert result == {100, 300}



def test_reference_elevation_matches_profile():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        reference_matches_profile,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1002.0),
    ]

    reference = RoadElevationReference(
        point_index=1,
        elevation_m=1001.4,
        source="survey",
        verified=True,
    )

    assert reference_matches_profile(
        profile,
        reference,
        tolerance_m=0.5,
    ) is True

    assert reference_matches_profile(
        profile,
        reference,
        tolerance_m=0.2,
    ) is False



def test_reference_matches_profile_rejects_negative_tolerance():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        reference_matches_profile,
    )

    reference = RoadElevationReference(
        point_index=0,
        elevation_m=1000.0,
        source="survey",
        verified=True,
    )

    with pytest.raises(ValueError):
        reference_matches_profile(
            [(0.0, 1000.0)],
            reference,
            tolerance_m=-0.1,
        )


def test_reference_matches_profile_rejects_invalid_index():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        reference_matches_profile,
    )

    profile = [(0.0, 1000.0)]

    for index in (-1, 1):
        reference = RoadElevationReference(
            point_index=index,
            elevation_m=1000.0,
            source="survey",
            verified=True,
        )

        with pytest.raises(ValueError):
            reference_matches_profile(
                profile,
                reference,
                tolerance_m=0.5,
            )


def test_reference_matches_profile_accepts_exact_elevation():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        reference_matches_profile,
    )

    reference = RoadElevationReference(
        point_index=0,
        elevation_m=1000.0,
        source="survey",
        verified=True,
    )

    assert reference_matches_profile(
        [(0.0, 1000.0)],
        reference,
        tolerance_m=0.0,
    ) is True



@pytest.mark.parametrize(
    "profile_elevation, reference_elevation, tolerance",
    [
        (float("nan"), 1000.0, 0.5),
        (float("inf"), 1000.0, 0.5),
        (1000.0, float("nan"), 0.5),
        (1000.0, float("-inf"), 0.5),
        (1000.0, 1000.0, float("nan")),
        (1000.0, 1000.0, float("inf")),
    ],
)
def test_reference_matches_profile_rejects_nonfinite_values(
    profile_elevation,
    reference_elevation,
    tolerance,
):
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        reference_matches_profile,
    )

    reference = RoadElevationReference(
        point_index=0,
        elevation_m=reference_elevation,
        source="survey",
        verified=True,
    )

    with pytest.raises(ValueError):
        reference_matches_profile(
            [(0.0, profile_elevation)],
            reference,
            tolerance_m=tolerance,
        )



def test_find_conflicting_references():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        find_conflicting_references,
    )

    references = [
        RoadElevationReference(
            point_index=100,
            elevation_m=1905.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=100,
            elevation_m=1912.0,
            source="survey_B",
            verified=True,
        ),
        RoadElevationReference(
            point_index=200,
            elevation_m=2100.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=200,
            elevation_m=2100.3,
            source="survey_B",
            verified=True,
        ),
    ]

    conflicts = find_conflicting_references(
        references,
        tolerance_m=0.5,
    )

    assert conflicts == {100}

    
@pytest.mark.parametrize(
    "invalid_elevation",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_find_conflicting_references_rejects_nonfinite_elevations(
    invalid_elevation,
):
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        find_conflicting_references,
    )

    references = [
        RoadElevationReference(
            point_index=100,
            elevation_m=1905.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=100,
            elevation_m=invalid_elevation,
            source="survey_B",
            verified=True,
        ),
    ]

    with pytest.raises(ValueError):
        find_conflicting_references(
            references,
            tolerance_m=0.5,
        )



@pytest.mark.parametrize(
    "invalid_tolerance",
    [
        -0.1,
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_find_conflicting_references_rejects_invalid_tolerance(
    invalid_tolerance,
):
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        find_conflicting_references,
    )

    references = [
        RoadElevationReference(
            point_index=100,
            elevation_m=1905.0,
            source="survey",
            verified=True,
        ),
    ]

    with pytest.raises(ValueError):
        find_conflicting_references(
            references,
            tolerance_m=invalid_tolerance,
        )


def test_verified_indices_exclude_conflicting_references():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        find_conflicting_references,
        get_verified_reference_indices,
    )

    references = [
        RoadElevationReference(
            point_index=100,
            elevation_m=1905.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=100,
            elevation_m=1912.0,
            source="survey_B",
            verified=True,
        ),
        RoadElevationReference(
            point_index=200,
            elevation_m=2100.0,
            source="survey_A",
            verified=True,
        ),
    ]

    conflicts = find_conflicting_references(
        references,
        tolerance_m=0.5,
    )

    verified_indices = get_verified_reference_indices(
        references,
        excluded_indices=conflicts,
    )

    assert conflicts == {100}
    assert verified_indices == {200}


def test_get_safe_verified_indices():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        get_safe_verified_indices,
    )

    references = [
        RoadElevationReference(
            point_index=100,
            elevation_m=1905.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=100,
            elevation_m=1912.0,
            source="survey_B",
            verified=True,
        ),
        RoadElevationReference(
            point_index=200,
            elevation_m=2100.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=300,
            elevation_m=2200.0,
            source="DEM",
            verified=False,
        ),
    ]

    result = get_safe_verified_indices(
        references,
        tolerance_m=0.5,
    )

    assert result == {200}



@pytest.mark.parametrize(
    "invalid_index",
    [-1, 1.5, "100", True],
)
def test_get_safe_verified_indices_rejects_invalid_index(
    invalid_index,
):
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        get_safe_verified_indices,
    )

    references = [
        RoadElevationReference(
            point_index=invalid_index,
            elevation_m=1905.0,
            source="survey",
            verified=True,
        ),
    ]

    with pytest.raises(ValueError):
        get_safe_verified_indices(
            references,
            tolerance_m=0.5,
        )


def test_get_safe_verified_indices_rejects_out_of_range_index():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        get_safe_verified_indices,
    )

    references = [
        RoadElevationReference(
            point_index=3,
            elevation_m=1003.0,
            source="survey",
            verified=True,
        ),
    ]

    with pytest.raises(ValueError):
        get_safe_verified_indices(
            references,
            tolerance_m=0.5,
            point_count=3,
        )


@pytest.mark.parametrize(
    "invalid_point_count",
    [
        -1,
        2.5,
        "2923",
        True,
    ],
)
def test_get_safe_verified_indices_rejects_invalid_point_count(
    invalid_point_count,
):
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        get_safe_verified_indices,
    )

    references = [
        RoadElevationReference(
            point_index=0,
            elevation_m=1000.0,
            source="survey",
            verified=True,
        ),
    ]

    with pytest.raises(ValueError):
        get_safe_verified_indices(
            references,
            tolerance_m=0.5,
            point_count=invalid_point_count,
        )



def test_road_zone_has_safe_boundary_references():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        road_zone_has_safe_boundaries,
    )

    references = [
        RoadElevationReference(
            point_index=0,
            elevation_m=1000.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=3,
            elevation_m=1003.0,
            source="survey_B",
            verified=True,
        ),
    ]

    assert road_zone_has_safe_boundaries(
        references,
        start=1,
        end=2,
        point_count=4,
        tolerance_m=0.5,
    ) is True

    assert road_zone_has_safe_boundaries(
        references[:1],
        start=1,
        end=2,
        point_count=4,
        tolerance_m=0.5,
    ) is False


def test_get_verified_reference_elevation():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        get_verified_reference_elevation,
    )

    references = [
        RoadElevationReference(
            point_index=100,
            elevation_m=1905.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=200,
            elevation_m=2100.0,
            source="DEM",
            verified=False,
        ),
    ]

    assert get_verified_reference_elevation(
        references,
        point_index=100,
        tolerance_m=0.5,
    ) == pytest.approx(1905.0)

    with pytest.raises(ValueError):
        get_verified_reference_elevation(
            references,
            point_index=200,
            tolerance_m=0.5,
        )



def test_verified_reference_elevation_averages_agreeing_measurements():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        get_verified_reference_elevation,
    )

    references = [
        RoadElevationReference(
            point_index=100,
            elevation_m=1905.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=100,
            elevation_m=1905.4,
            source="survey_B",
            verified=True,
        ),
    ]

    result = get_verified_reference_elevation(
        references,
        point_index=100,
        tolerance_m=0.5,
    )

    assert result == pytest.approx(1905.2)

    reversed_result = get_verified_reference_elevation(
        list(reversed(references)),
        point_index=100,
        tolerance_m=0.5,
    )

    assert reversed_result == pytest.approx(1905.2)



def test_verified_reference_elevation_rejects_conflicting_measurements():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        get_verified_reference_elevation,
    )

    references = [
        RoadElevationReference(
            point_index=100,
            elevation_m=1900.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=100,
            elevation_m=1910.0,
            source="survey_B",
            verified=True,
        ),
    ]

    with pytest.raises(ValueError):
        get_verified_reference_elevation(
            references,
            point_index=100,
            tolerance_m=0.5,
        )


def test_apply_boundary_reference_elevations():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        apply_boundary_reference_elevations,
    )

    profile = [
        (0.0, 995.0),
        (10.0, 1035.0),
        (20.0, 1036.0),
        (30.0, 998.0),
    ]

    references = [
        RoadElevationReference(
            point_index=0,
            elevation_m=1000.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=3,
            elevation_m=1003.0,
            source="survey_B",
            verified=True,
        ),
    ]

    corrected = apply_boundary_reference_elevations(
        profile,
        references,
        start=1,
        end=2,
        tolerance_m=0.5,
    )

    assert corrected == [
        (0.0, 1000.0),
        (10.0, 1035.0),
        (20.0, 1036.0),
        (30.0, 1003.0),
    ]

    # Originalni profil mora ostati netaknut.
    assert profile[0] == (0.0, 995.0)
    assert profile[3] == (30.0, 998.0)



def test_reconstruct_road_zone_from_references():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        reconstruct_road_zone_from_references,
    )

    profile = [
        (0.0, 995.0),
        (10.0, 1035.0),
        (20.0, 1036.0),
        (30.0, 998.0),
    ]

    references = [
        RoadElevationReference(
            point_index=0,
            elevation_m=1000.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=3,
            elevation_m=1003.0,
            source="survey_B",
            verified=True,
        ),
    ]

    corrected = reconstruct_road_zone_from_references(
        profile,
        references,
        start=1,
        end=2,
        tolerance_m=0.5,
        max_allowed_grade=0.12,
    )

    assert corrected == [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1002.0),
        (30.0, 1003.0),
    ]

    # Originalni DEM profil nije promenjen.
    assert profile == [
        (0.0, 995.0),
        (10.0, 1035.0),
        (20.0, 1036.0),
        (30.0, 998.0),
    ]


def test_reconstruct_road_zone_from_references_rejects_steep_left_transition():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        reconstruct_road_zone_from_references,
    )

    profile = [
        (-10.0, 990.0),
        (0.0, 995.0),
        (10.0, 1035.0),
        (20.0, 1036.0),
        (30.0, 998.0),
        (40.0, 1004.0),
    ]

    references = [
        RoadElevationReference(
            point_index=1,
            elevation_m=1000.0,
            source="survey_A",
            verified=True,
        ),
        RoadElevationReference(
            point_index=4,
            elevation_m=1003.0,
            source="survey_B",
            verified=True,
        ),
    ]

    with pytest.raises(ValueError):
        reconstruct_road_zone_from_references(
            profile,
            references,
            start=2,
            end=3,
            tolerance_m=0.5,
            max_allowed_grade=0.12,
        )



def test_calculate_road_grade_change():
    from stelvio_terrain.road_elevation import (
        calculate_road_grade_change,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1000.0),
    ]

    change = calculate_road_grade_change(
        profile,
        index=1,
    )

    assert change == pytest.approx(0.20)



@pytest.mark.parametrize(
    "invalid_index",
    [-1, 0, 2, 3],
)
def test_calculate_road_grade_change_rejects_boundary_indices(
    invalid_index,
):
    from stelvio_terrain.road_elevation import (
        calculate_road_grade_change,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1000.0),
    ]

    with pytest.raises(ValueError):
        calculate_road_grade_change(
            profile,
            index=invalid_index,
        )



def test_calculate_vertical_curvature():
    from stelvio_terrain.road_elevation import (
        calculate_vertical_curvature,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1000.0),
    ]

    curvature = calculate_vertical_curvature(
        profile,
        index=1,
    )

    assert curvature == pytest.approx(-0.02)



def test_calculate_vertical_curvature_unequal_segments():
    from stelvio_terrain.road_elevation import (
        calculate_vertical_curvature,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (40.0, 1004.0),
    ]

    curvature = calculate_vertical_curvature(
        profile,
        index=1,
    )

    assert curvature == pytest.approx(0.0)



def test_calculate_vertical_curvature_unequal_segments_with_grade_change():
    from stelvio_terrain.road_elevation import (
        calculate_vertical_curvature,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (40.0, 1000.0),
    ]

    curvature = calculate_vertical_curvature(
        profile,
        index=1,
    )

    assert curvature == pytest.approx(-1.0 / 150.0)



@pytest.mark.parametrize(
    "invalid_index",
    [-1, 0, 2, 3],
)
def test_calculate_vertical_curvature_rejects_invalid_index(
    invalid_index,
):
    from stelvio_terrain.road_elevation import (
        calculate_vertical_curvature,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1000.0),
    ]

    with pytest.raises(ValueError):
        calculate_vertical_curvature(
            profile,
            index=invalid_index,
        )


def test_calculate_vertical_curvature_rejects_duplicate_distances():
    from stelvio_terrain.road_elevation import (
        calculate_vertical_curvature,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (10.0, 1002.0),
    ]

    with pytest.raises(ValueError):
        calculate_vertical_curvature(
            profile,
            index=1,
        )



def test_calculate_vertical_curvature_rejects_decreasing_distances():
    from stelvio_terrain.road_elevation import (
        calculate_vertical_curvature,
    )

    profile = [
        (0.0, 1000.0),
        (20.0, 1001.0),
        (10.0, 1002.0),
    ]

    with pytest.raises(ValueError):
        calculate_vertical_curvature(
            profile,
            index=1,
        )



def test_calculate_vertical_curvature_profile():
    from stelvio_terrain.road_elevation import (
        calculate_vertical_curvature_profile,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1000.0),
        (30.0, 1000.0),
    ]

    result = calculate_vertical_curvature_profile(profile)

    assert len(result) == 2

    assert result[0] == pytest.approx(
        (10.0, -0.02)
    )

    assert result[1] == pytest.approx(
        (20.0, 0.01)
    )



def test_find_max_vertical_curvature():
    from stelvio_terrain.road_elevation import (
        find_max_vertical_curvature,
    )

    curvature_profile = [
        (10.0, -0.02),
        (20.0, 0.01),
        (30.0, -0.05),
        (40.0, 0.03),
    ]

    result = find_max_vertical_curvature(
        curvature_profile
    )

    assert result == (30.0, -0.05)








def test_stelvio_max_vertical_curvature_diagnostic():
    from stelvio_terrain.road_elevation import (
        calculate_vertical_curvature_profile,
        find_max_vertical_curvature,
    )
    from stelvio_terrain.route_geometry import (
        remove_consecutive_duplicates,
        cumulative_route_distances,
    )

    import json
    import rasterio

    route_path = (
        "stelvio_terrain/data/stelvio_east_route.geojson"
    )
    dem_path = (
        "stelvio_terrain/data/dem/output_hh.tif"
    )

    with open(route_path, encoding="utf-8") as f:
        route = json.load(f)
        
    geometry = route["geometry"]
    coordinates = remove_consecutive_duplicates(
        geometry["coordinates"]
    )

    distances = cumulative_route_distances(coordinates)

    with rasterio.open(dem_path) as dem:
        elevations = [
            float(sample[0])
            for sample in dem.sample(coordinates)
        ]

    profile = list(zip(distances, elevations))

    curvature_profile = (
        calculate_vertical_curvature_profile(profile)
    )

    distance, curvature = find_max_vertical_curvature(
        curvature_profile
    )
    
    index = min(
        range(1, len(profile) - 1),
        key=lambda i: abs(profile[i][0] - distance),
    )

    print("\nAnomaly index:", index)

    for i in range(index - 1, index + 2):
        s, z = profile[i]
        print(
            f"Point {i}: "
            f"distance={s:.3f} m, "
            f"elevation={z:.3f} m"
        )

    grade_before = (
        (profile[index][1] - profile[index - 1][1])
        / (profile[index][0] - profile[index - 1][0])
    )

    grade_after = (
        (profile[index + 1][1] - profile[index][1])
        / (profile[index + 1][0] - profile[index][0])
    )

    print(f"Grade before: {grade_before * 100:.2f}%")
    print(f"Grade after:  {grade_after * 100:.2f}%")
    
    with rasterio.open(dem_path) as dem:
        print("\nDEM cell diagnostics:")

        for i in range(index - 1, index + 2):
            lon, lat = coordinates[i]
            row, col = dem.index(lon, lat)

            print(
                f"Point {i}: "
                f"row={row}, col={col}, "
                f"elevation={profile[i][1]:.3f} m"
            )

    print()
    print(f"Stelvio points: {len(profile)}")
    print(f"Curvature samples: {len(curvature_profile)}")
    print(f"Maximum at: {distance:.1f} m")
    print(f"Curvature: {curvature:.6f} 1/m")

    assert len(profile) == 2923
    assert len(curvature_profile) == 2921
    assert distance > 0
    
    from rasterio.windows import Window
    from scipy.ndimage import map_coordinates
    import numpy as np

    with rasterio.open(dem_path) as dem:
        raster = dem.read(1)

        print("\nBilinear DEM diagnostics:")

        for i in range(index - 1, index + 2):
            lon, lat = coordinates[i]

            col_f, row_f = (
                ~dem.transform
            ) @ (lon, lat)

            # Raster coordinates refer to pixel corners.
            # Shift to pixel centers.
            row_center = row_f - 0.5
            col_center = col_f - 0.5

            elevation = map_coordinates(
                raster,
                np.array([
                    [row_center],
                    [col_center],
                ]),
                order=1,
                mode="nearest",
            )[0]

            print(
                f"Point {i}: "
                f"nearest={profile[i][1]:.3f} m, "
                f"bilinear={elevation:.3f} m"
            )
        
    # Bilinearno uzorkovanje cele Stelvio trase.
    with rasterio.open(dem_path) as dem:
        raster = dem.read(1)

        bilinear_elevations = []

        for lon, lat in coordinates:
            col_f, row_f = (~dem.transform) @ (lon, lat)

            elevation = map_coordinates(
                raster,
                np.array([
                    [row_f - 0.5],
                    [col_f - 0.5],
                ]),
                order=1,
                mode="nearest",
            )[0]

            bilinear_elevations.append(float(elevation))

    bilinear_profile = list(
        zip(distances, bilinear_elevations)
    )

    bilinear_curvatures = (
        calculate_vertical_curvature_profile(
            bilinear_profile
        )
    )

    bilinear_distance, bilinear_curvature = (
        find_max_vertical_curvature(
            bilinear_curvatures
        )
    )

    print("\nFull Stelvio DEM comparison:")
    print(
        f"Nearest maximum: "
        f"{curvature:.6f} 1/m "
        f"at {distance:.1f} m"
    )
    print(
        f"Bilinear maximum: "
        f"{bilinear_curvature:.6f} 1/m "
        f"at {bilinear_distance:.1f} m"
    )

    assert len(bilinear_profile) == 2923
    assert len(bilinear_curvatures) == 2921
    
    bilinear_index = min(
        range(1, len(bilinear_profile) - 1),
        key=lambda i: abs(
            bilinear_profile[i][0] - bilinear_distance
        ),
    )

    print("\nBilinear anomaly diagnostics:")
    print(f"Index: {bilinear_index}")

    for i in range(bilinear_index - 1, bilinear_index + 2):
        s, z = bilinear_profile[i]
        print(
            f"Point {i}: "
            f"distance={s:.3f} m, "
            f"elevation={z:.3f} m"
        )

    grade_before = calculate_road_grade(
        bilinear_profile[bilinear_index - 1],
        bilinear_profile[bilinear_index],
    )

    grade_after = calculate_road_grade(
        bilinear_profile[bilinear_index],
        bilinear_profile[bilinear_index + 1],
    )

    print(f"Grade before: {grade_before * 100:.2f}%")
    print(f"Grade after:  {grade_after * 100:.2f}%")
    
    from stelvio_terrain.road_elevation import (
        resample_elevation_profile,
    )

    uniform_profile = resample_elevation_profile(
        bilinear_profile,
        step_m=10.0,
    )

    uniform_curvatures = (
        calculate_vertical_curvature_profile(
            uniform_profile
        )
    )

    uniform_distance, uniform_curvature = (
        find_max_vertical_curvature(
            uniform_curvatures
        )
    )

    print("\nUniform 10 m profile:")
    print(f"Points: {len(uniform_profile)}")
    print(
        f"Maximum curvature: "
        f"{uniform_curvature:.6f} 1/m"
    )
    print(
        f"Maximum at: "
        f"{uniform_distance:.1f} m"
    )

    assert len(uniform_profile) > 2900
    assert len(uniform_curvatures) == len(uniform_profile) - 2
    
    uniform_index = min(
        range(1, len(uniform_profile) - 1),
        key=lambda i: abs(
            uniform_profile[i][0] - uniform_distance
        ),
    )

    print("\nUniform profile anomaly:")
    print(f"Index: {uniform_index}")

    for i in range(uniform_index - 2, uniform_index + 3):
        s, z = uniform_profile[i]
        print(
            f"Point {i}: "
            f"distance={s:.1f} m, "
            f"elevation={z:.3f} m"
        )

    print("\nAdjacent grades:")

    for i in range(uniform_index - 2, uniform_index + 2):
        grade = calculate_road_grade(
            uniform_profile[i],
            uniform_profile[i + 1],
        )

        print(
            f"Segment {i}-{i + 1}: "
            f"{grade * 100:.2f}%"
        )
    
    print("\nOriginal bilinear points near 27000 m:")

    nearby_points = [
        (i, s, z)
        for i, (s, z) in enumerate(bilinear_profile)
        if 26990.0 <= s <= 27010.0
    ]

    for i, s, z in nearby_points:
        print(
            f"Point {i}: "
            f"distance={s:.3f} m, "
            f"elevation={z:.3f} m"
        )

    assert nearby_points
    
    from stelvio_terrain.road_elevation import (
        find_steep_road_segments,
    )

    steep_indices = find_steep_road_segments(
        uniform_profile,
        max_grade=0.20,
    )

    steep_length = sum(
        uniform_profile[i + 1][0] - uniform_profile[i][0]
        for i in steep_indices
    )

    grades = [
        calculate_road_grade(
            uniform_profile[i],
            uniform_profile[i + 1],
        )
        for i in range(len(uniform_profile) - 1)
    ]

    max_grade_index = max(
        range(len(grades)),
        key=lambda i: abs(grades[i]),
    )

    print("\nStelvio steep segment diagnostics:")
    print(f"Total segments: {len(grades)}")
    print(f"Steep segments (>20%): {len(steep_indices)}")
    print(f"Steep length: {steep_length:.1f} m")
    print(
        f"Steep share: "
        f"{100 * steep_length / uniform_profile[-1][0]:.2f}%"
    )
    print(
        f"Maximum grade: "
        f"{grades[max_grade_index] * 100:.2f}%"
    )
    print(
        f"Maximum grade at: "
        f"{uniform_profile[max_grade_index][0]:.1f} m"
    )

    assert len(grades) == len(uniform_profile) - 1
    
    from stelvio_terrain.road_elevation import (
        group_consecutive_segments,
    )

    steep_zones = group_consecutive_segments(
        steep_indices
    )

    print("\nStelvio steep zones:")
    print(f"Number of zones: {len(steep_zones)}")

    zone_lengths = []

    for start, end in steep_zones:
        start_distance = uniform_profile[start][0]
        end_distance = uniform_profile[end + 1][0]

        zone_lengths.append(
            end_distance - start_distance
        )

    print(
        f"Longest zone: {max(zone_lengths):.1f} m"
    )

    longest_zone_index = max(
        range(len(zone_lengths)),
        key=lambda i: zone_lengths[i],
    )

    start, end = steep_zones[longest_zone_index]

    print(
        f"Longest zone starts at: "
        f"{uniform_profile[start][0]:.1f} m"
    )
    print(
        f"Longest zone ends at: "
        f"{uniform_profile[end + 1][0]:.1f} m"
    )

    assert sum(zone_lengths) == pytest.approx(
        steep_length
    )
    
    ranked_zones = sorted(
        zip(steep_zones, zone_lengths),
        key=lambda item: item[1],
        reverse=True,
    )

    print("\nFive longest steep zones:")

    for rank, ((start, end), length) in enumerate(
        ranked_zones[:5],
        start=1,
    ):
        start_distance = uniform_profile[start][0]
        end_distance = uniform_profile[end + 1][0]

        zone_max_grade = max(
            abs(grades[i])
            for i in range(start, end + 1)
        )

        print(
            f"{rank}. "
            f"{start_distance:.0f} - "
            f"{end_distance:.0f} m | "
            f"length={length:.0f} m | "
            f"max grade={zone_max_grade * 100:.2f}%"
        )

    assert len(ranked_zones) == len(steep_zones)
    
    print("\nLongest steep zone elevation profile:")

    start, end = steep_zones[longest_zone_index]

    first_point = max(0, start - 2)
    last_point = min(
        len(uniform_profile) - 1,
        end + 3,
    )

    for i in range(first_point, last_point + 1):
        distance, elevation = uniform_profile[i]

        if i < len(grades):
            grade_text = f"{grades[i] * 100:+.2f}%"
        else:
            grade_text = "-"

        print(
            f"{i:4d} | "
            f"{distance:8.1f} m | "
            f"{elevation:9.3f} m | "
            f"{grade_text:>9}"
        )
        
    print("\nLongest zone boundary diagnostics:")

    start, end = steep_zones[longest_zone_index]

    for margin in (0, 2, 5, 10, 20):
        left = max(0, start - margin)
        right = min(
            len(uniform_profile) - 1,
            end + 1 + margin,
        )

        s0, z0 = uniform_profile[left]
        s1, z1 = uniform_profile[right]

        average_grade = (z1 - z0) / (s1 - s0)

        print(
            f"Margin {margin:2d}: "
            f"{s0:.0f}-{s1:.0f} m | "
            f"grade={average_grade * 100:+.2f}%"
        )
        
    print("\nStelvio reconstruction reference candidates:")

    start, end = steep_zones[longest_zone_index]

    for margin in (2, 5, 10, 20):
        left = start - margin
        right = end + 1 + margin

        if left < 0 or right >= len(uniform_profile):
            continue

        s_left, z_left = uniform_profile[left]
        s_right, z_right = uniform_profile[right]

        print(
            f"Margin {margin:2d}: "
            f"left=({s_left:.0f} m, {z_left:.3f} m), "
            f"right=({s_right:.0f} m, {z_right:.3f} m)"
        )

    
def test_generate_uniform_distances():
    from stelvio_terrain.road_elevation import (
        generate_uniform_distances,
    )

    result = generate_uniform_distances(
        total_distance=25.0,
        step_m=10.0,
    )

    assert result == pytest.approx([
        0.0,
        10.0,
        20.0,
        25.0,
    ])


def test_resample_elevation_profile():
    from stelvio_terrain.road_elevation import (
        resample_elevation_profile,
    )

    profile = [
        (0.0, 1000.0),
        (15.0, 1003.0),
        (25.0, 1005.0),
    ]

    result = resample_elevation_profile(
        profile,
        step_m=10.0,
    )

    assert result == pytest.approx([
        (0.0, 1000.0),
        (10.0, 1002.0),
        (20.0, 1004.0),
        (25.0, 1005.0),
    ])



def test_find_steep_road_segments():
    from stelvio_terrain.road_elevation import (
        find_steep_road_segments,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1005.0),
        (30.0, 1004.0),
        (40.0, 1000.0),
    ]

    result = find_steep_road_segments(
        profile,
        max_grade=0.20,
    )

    assert result == [1, 3]


def test_group_consecutive_segments():
    from stelvio_terrain.road_elevation import (
        group_consecutive_segments,
    )

    indices = [1, 2, 3, 7, 8, 12]

    result = group_consecutive_segments(indices)

    assert result == [
        (1, 3),
        (7, 8),
        (12, 12),
    ]


def test_road_zone_without_references_is_not_safe():
    from stelvio_terrain.road_elevation import (
        road_zone_has_safe_boundaries,
    )

    profile = [
        (0.0, 1000.0),
        (10.0, 1001.0),
        (20.0, 1005.0),
        (30.0, 1008.0),
        (40.0, 1009.0),
    ]

    references = []
       
    assert road_zone_has_safe_boundaries(
        references=references,
        start=1,
        end=3,
        point_count=len(profile),
        tolerance_m=1.0,
    ) is False


def test_road_zone_with_only_one_reference_is_not_safe():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        road_zone_has_safe_boundaries,
    )

    references = [
        RoadElevationReference(
            point_index=0,
            elevation_m=1000.0,
            source="survey",
            verified=True,
        ),
       
    ]

    result = road_zone_has_safe_boundaries(
        references=references,
        start=1,
        end=3,
        point_count=5,
        tolerance_m=1.0,
    )

    assert result is False



def test_road_zone_with_two_verified_boundaries_is_safe():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        road_zone_has_safe_boundaries,
    )

    references = [
        RoadElevationReference(
            point_index=0,
            elevation_m=1000.0,
            source="survey",
            verified=True,
        ),
        RoadElevationReference(
            point_index=4,
            elevation_m=1009.0,
            source="survey",
            verified=True,
        ),
    ]

    result = road_zone_has_safe_boundaries(
        references=references,
        start=1,
        end=3,
        point_count=5,
        tolerance_m=1.0,
    )

    assert result is True


def test_road_zone_with_unverified_boundary_is_not_safe():
    from stelvio_terrain.road_elevation import (
        RoadElevationReference,
        road_zone_has_safe_boundaries,
    )
        
    references = [
        RoadElevationReference(
            point_index=0,
            elevation_m=1000.0,
            source="survey",
            verified=True,
        ),
    ]

    result = road_zone_has_safe_boundaries(
        references=references,
        start=1,
        end=3,
        point_count=5,
        tolerance_m=1.0,
    )

    assert result is False


def test_find_constant_elevation_runs():
    from stelvio_terrain.road_elevation import (
        find_constant_elevation_runs,
    )

    profile = [
        (0.0, 100.0),
        (10.0, 101.0),
        (20.0, 101.0),
        (30.0, 101.0),
        (40.0, 102.0),
        (50.0, 103.0),
        (60.0, 103.0),
    ]

    result = find_constant_elevation_runs(
        profile,
        min_length_m=20.0,
    )

    assert result == [(1, 3)]


def test_find_constant_elevation_runs_at_profile_end():
    from stelvio_terrain.road_elevation import (
        find_constant_elevation_runs,
    )

    profile = [
        (0.0, 100.0),
        (10.0, 101.0),
        (20.0, 102.0),
        (30.0, 102.0),
        (40.0, 102.0),
    ]

    result = find_constant_elevation_runs(
        profile,
        min_length_m=20.0,
    )

    assert result == [(2, 4)]


def test_find_constant_elevation_runs_entire_profile():
    from stelvio_terrain.road_elevation import (
        find_constant_elevation_runs,
    )

    profile = [
        (0.0, 1450.0),
        (10.0, 1450.0),
        (20.0, 1450.0),
        (30.0, 1450.0),
        (40.0, 1450.0),
    ]

    result = find_constant_elevation_runs(
        profile,
        min_length_m=30.0,
    )

    assert result == [(0, 4)]



def test_find_constant_elevation_runs_multiple_runs():
    from stelvio_terrain.road_elevation import (
        find_constant_elevation_runs,
    )

    profile = [
        (0.0, 100.0),
        (10.0, 100.0),
        (20.0, 100.0),
        (30.0, 101.0),
        (40.0, 102.0),
        (50.0, 102.0),
        (60.0, 102.0),
        (70.0, 103.0),
    ]

    result = find_constant_elevation_runs(
        profile,
        min_length_m=20.0,
    )

    assert result == [
        (0, 2),
        (4, 6),
    ]



def test_get_constant_elevation_run_indices():
    from stelvio_terrain.road_elevation import (
        get_constant_elevation_run_indices,
    )

    runs = [
        (1, 3),
        (6, 8),
    ]

    result = get_constant_elevation_run_indices(runs)

    assert result == {1, 2, 3, 6, 7, 8}

def test_is_point_in_constant_elevation_run():
    from stelvio_terrain.road_elevation import (
        is_point_in_constant_elevation_run,
    )

    plateau_indices = {1, 2, 3, 6, 7, 8}

    assert is_point_in_constant_elevation_run(
        2, plateau_indices
    ) is True

    assert is_point_in_constant_elevation_run(
        5, plateau_indices
    ) is False

def test_get_non_plateau_indices():
    from stelvio_terrain.road_elevation import (
        get_non_plateau_indices,
    )

    point_count = 10
    plateau_indices = {1, 2, 3, 6, 7, 8}

    result = get_non_plateau_indices(
        point_count,
        plateau_indices,
    )

    assert result == {0, 4, 5, 9}


def test_get_non_plateau_indices_without_plateaus():
    from stelvio_terrain.road_elevation import (
        get_non_plateau_indices,
    )

    result = get_non_plateau_indices(
        point_count=5,
        plateau_indices=set(),
    )

    assert result == {0, 1, 2, 3, 4}

def test_is_gpx_segment_length_acceptable():
    from stelvio_terrain.road_elevation import (
        is_gpx_segment_length_acceptable,
    )

    assert is_gpx_segment_length_acceptable(
        20.0, 10.0, 100.0
    ) is True

    assert is_gpx_segment_length_acceptable(
        5.0, 10.0, 100.0
    ) is False

    assert is_gpx_segment_length_acceptable(
        150.0, 10.0, 100.0
    ) is False


def test_is_gpx_segment_length_acceptable_boundaries():
    from stelvio_terrain.road_elevation import (
        is_gpx_segment_length_acceptable,
    )

    assert is_gpx_segment_length_acceptable(
        10.0, 10.0, 100.0
    ) is True

    assert is_gpx_segment_length_acceptable(
        100.0, 10.0, 100.0
    ) is True

    assert is_gpx_segment_length_acceptable(
        9.99, 10.0, 100.0
    ) is False

    assert is_gpx_segment_length_acceptable(
        100.01, 10.0, 100.0
    ) is False


def test_elevation_difference():
    from stelvio_terrain.road_elevation import elevation_difference

    assert elevation_difference(1172.0, 1167.3) == pytest.approx(4.7)
    assert elevation_difference(1173.0, 1182.7) == pytest.approx(-9.7)
    assert elevation_difference(1205.0, 1199.4) == pytest.approx(5.6)

def test_elevation_difference_within_tolerance():
    from stelvio_terrain.road_elevation import (
        is_elevation_difference_acceptable,
    )

    assert is_elevation_difference_acceptable(4.7, 5.0) is True
    assert is_elevation_difference_acceptable(-4.7, 5.0) is True
    assert is_elevation_difference_acceptable(5.0, 5.0) is True

    assert is_elevation_difference_acceptable(-9.7, 5.0) is False
    assert is_elevation_difference_acceptable(5.6, 5.0) is False


def test_elevation_difference_change():
    from stelvio_terrain.road_elevation import (
        elevation_difference_change,
    )

    assert elevation_difference_change(4.7, -9.7) == pytest.approx(-14.4)
    assert elevation_difference_change(-2.4, 5.6) == pytest.approx(8.0)
    assert elevation_difference_change(3.0, 3.0) == pytest.approx(0.0)


def test_elevation_difference_change_rate():
    from stelvio_terrain.road_elevation import (
        elevation_difference_change_rate,
    )

    assert elevation_difference_change_rate(
        -14.4, 170.83
    ) == pytest.approx(-14.4 / 170.83)

    assert elevation_difference_change_rate(
        8.0, 100.0
    ) == pytest.approx(0.08)

    assert elevation_difference_change_rate(
        0.0, 50.0
    ) == pytest.approx(0.0)


def test_elevation_difference_change_rate_rejects_zero_length():
    from stelvio_terrain.road_elevation import (
        elevation_difference_change_rate,
    )

    with pytest.raises(ValueError):
        elevation_difference_change_rate(-14.4, 0.0)


def test_elevation_grade_disagreement_percent():
    from stelvio_terrain.road_elevation import (
        elevation_grade_disagreement_percent,
    )

    assert elevation_grade_disagreement_percent(
        -14.4, 170.83
    ) == pytest.approx(-8.43, abs=0.01)

    assert elevation_grade_disagreement_percent(
        8.0, 100.0
    ) == pytest.approx(8.0)

    assert elevation_grade_disagreement_percent(
        0.0, 50.0
    ) == pytest.approx(0.0)


def test_is_grade_disagreement_significant():
    from stelvio_terrain.road_elevation import (
        is_grade_disagreement_significant,
    )

    assert is_grade_disagreement_significant(-8.43, 5.0) is True
    assert is_grade_disagreement_significant(6.0, 5.0) is True

    assert is_grade_disagreement_significant(3.0, 5.0) is False
    assert is_grade_disagreement_significant(-5.0, 5.0) is False
    assert is_grade_disagreement_significant(0.0, 5.0) is False


def test_grade_disagreement_threshold_boundary():
    from stelvio_terrain.road_elevation import (
        is_grade_disagreement_significant,
    )

    assert is_grade_disagreement_significant(5.001, 5.0) is True
    assert is_grade_disagreement_significant(-5.001, 5.0) is True

    assert is_grade_disagreement_significant(4.999, 5.0) is False
    assert is_grade_disagreement_significant(-4.999, 5.0) is False


def test_reconstruct_road_profile_preserves_valid_points():
    from stelvio_terrain.road_elevation import (
        reconstruct_road_profile,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1004.0),
        (100.0, 1008.0),
    ]

    result = reconstruct_road_profile(profile)

    assert result == profile

def test_reconstruct_road_profile_returns_independent_copy():
    from stelvio_terrain.road_elevation import (
        reconstruct_road_profile,
    )

    original = [
        (0.0, 1000.0),
        (50.0, 1004.0),
        (100.0, 1008.0),
    ]

    result = reconstruct_road_profile(original)

    assert result is not original

    result[1] = (50.0, 1010.0)

    assert original[1] == (50.0, 1004.0)


def test_reconstruct_road_profile_rejects_duplicate_distance():
    from stelvio_terrain.road_elevation import (
        reconstruct_road_profile,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1004.0),
        (50.0, 1008.0),
    ]

    with pytest.raises(ValueError):
        reconstruct_road_profile(profile)


def test_is_road_grade_suspicious_when_above_limit():
    from stelvio_terrain.road_elevation import (
        is_road_grade_suspicious,
    )

    assert is_road_grade_suspicious(
        distance=100.0,
        elevation_change=20.0,
        max_grade_percent=15.0,
    ) is True

    assert is_road_grade_suspicious(
        distance=100.0,
        elevation_change=10.0,
        max_grade_percent=15.0,
    ) is False

def test_is_road_grade_suspicious_for_descent():
    from stelvio_terrain.road_elevation import (
        is_road_grade_suspicious,
    )

    assert is_road_grade_suspicious(
        distance=100.0,
        elevation_change=-20.0,
        max_grade_percent=15.0,
    ) is True

    assert is_road_grade_suspicious(
        distance=100.0,
        elevation_change=-10.0,
        max_grade_percent=15.0,
    ) is False

    assert is_road_grade_suspicious(
        distance=100.0,
        elevation_change=-15.0,
        max_grade_percent=15.0,
    ) is False

def test_find_suspicious_grade_segments():
    from stelvio_terrain.road_elevation import (
        find_suspicious_grade_segments,
    )

    profile = [
        (0.0, 1000.0),
        (100.0, 1010.0),  # +10% — prihvatljivo
        (200.0, 1030.0),  # +20% — sumnjivo
        (300.0, 1025.0),  # -5%  — prihvatljivo
        (400.0, 1005.0),  # -20% — sumnjivo
    ]

    result = find_suspicious_grade_segments(
        profile,
        max_grade_percent=15.0,
    )

    assert result == [1, 3]


def test_find_suspicious_grade_segments_skips_zero_length():
    from stelvio_terrain.road_elevation import (
        find_suspicious_grade_segments,
    )

    profile = [
        (0.0, 1000.0),
        (100.0, 1010.0),
        (100.0, 1010.0),  # Duplirana tačka
        (200.0, 1030.0),  # Nagib +20%
    ]

    result = find_suspicious_grade_segments(
        profile,
        max_grade_percent=15.0,
    )

    assert result == [2]

def test_correct_isolated_elevation_spike():
    from stelvio_terrain.road_elevation import (
        correct_isolated_elevation_spike,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1020.0),
        (100.0, 1010.0),
    ]

    result = correct_isolated_elevation_spike(
        profile,
        index=1,
    )

    assert result == [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    assert profile[1] == (50.0, 1020.0)


def test_correct_isolated_elevation_spike_rejects_endpoints():
    import pytest

    from stelvio_terrain.road_elevation import (
        correct_isolated_elevation_spike,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1020.0),
        (100.0, 1010.0),
    ]

    with pytest.raises(ValueError):
        correct_isolated_elevation_spike(profile, index=0)

    with pytest.raises(ValueError):
        correct_isolated_elevation_spike(profile, index=2)


def test_correct_isolated_elevation_spike_rejects_zero_distance():
    import pytest

    from stelvio_terrain.road_elevation import (
        correct_isolated_elevation_spike,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1020.0),
        (0.0, 1010.0),
    ]

    with pytest.raises(ValueError):
        correct_isolated_elevation_spike(
            profile,
            index=1,
        )


def test_correct_isolated_elevation_spike_rejects_middle_point_outside_neighbors():
    import pytest

    from stelvio_terrain.road_elevation import (
        correct_isolated_elevation_spike,
    )

    profile = [
        (0.0, 1000.0),
        (150.0, 1020.0),
        (100.0, 1010.0),
    ]

    with pytest.raises(ValueError):
        correct_isolated_elevation_spike(
            profile,
            index=1,
        )


def test_is_isolated_elevation_spike():
    from stelvio_terrain.road_elevation import (
        is_isolated_elevation_spike,
    )

    # Nagli uspon +40%, zatim spust -20%.
    assert is_isolated_elevation_spike(
        grade_before=40.0,
        grade_after=-20.0,
        threshold=15.0,
    ) is True

    # Stalan uspon nije šiljak.
    assert is_isolated_elevation_spike(
        grade_before=20.0,
        grade_after=18.0,
        threshold=15.0,
    ) is False

    # Blag prevoj nije sumnjiv šiljak.
    assert is_isolated_elevation_spike(
        grade_before=8.0,
        grade_after=-6.0,
        threshold=15.0,
    ) is False

    # Nagli pad pa uspon: moguća visinska rupa.
    assert is_isolated_elevation_spike(
        grade_before=-25.0,
        grade_after=30.0,
        threshold=15.0,
    ) is True


def test_is_profile_elevation_spike():
    from stelvio_terrain.road_elevation import (
        is_profile_elevation_spike,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1020.0),
        (100.0, 1010.0),
    ]

    assert is_profile_elevation_spike(
        profile,
        index=1,
        threshold=15.0,
    ) is True


def test_is_profile_elevation_spike_preserves_climb():
    from stelvio_terrain.road_elevation import (
        is_profile_elevation_spike,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1010.0),
        (100.0, 1020.0),
    ]

    result = is_profile_elevation_spike(
        profile,
        index=1,
        threshold=15.0,
    )

    assert result is False


def test_is_profile_elevation_spike_preserves_gentle_summit():
    from stelvio_terrain.road_elevation import (
        is_profile_elevation_spike,
    )

    profile = [
        (0.0, 1000.0),
        (100.0, 1008.0),
        (200.0, 1002.0),
    ]

    result = is_profile_elevation_spike(
        profile,
        index=1,
        threshold=15.0,
    )

    assert result is False


def test_interpolate_profile_elevation():
    from stelvio_terrain.road_elevation import (
        interpolate_profile_elevation,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1010.0),
        (150.0, 1030.0),
    ]

    result = interpolate_profile_elevation(
        profile,
        distance=100.0,
    )

    assert result == 1020.0

def test_sample_elevation_profile_at_fixed_distances():
    from stelvio_terrain.road_elevation import (
        sample_elevation_profile,
    )

    profile = [
        (0.0, 1000.0),
        (60.0, 1006.0),
        (150.0, 1015.0),
        (200.0, 1020.0),
    ]

    result = sample_elevation_profile(
        profile,
        step=50.0,
    )

    assert result == [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
        (150.0, 1015.0),
        (200.0, 1020.0),
    ]


def test_sample_elevation_profile_includes_endpoint():
    from stelvio_terrain.road_elevation import (
        sample_elevation_profile,
    )

    profile = [
        (0.0, 1000.0),
        (120.0, 1012.0),
    ]

    result = sample_elevation_profile(
        profile,
        step=50.0,
    )

    assert result == [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
        (120.0, 1012.0),
    ]


def test_sample_elevation_profile_with_nonzero_start():
    from stelvio_terrain.road_elevation import (
        sample_elevation_profile,
    )

    profile = [
        (3500.0, 1092.0),
        (3620.0, 1104.0),
    ]

    result = sample_elevation_profile(
        profile,
        step=50.0,
    )

    assert result == [
        (3500.0, 1092.0),
        (3550.0, 1097.0),
        (3600.0, 1102.0),
        (3620.0, 1104.0),
    ]


@pytest.mark.parametrize("step", [0.0, -50.0])
def test_sample_elevation_profile_rejects_invalid_step(step):
    from stelvio_terrain.road_elevation import (
        sample_elevation_profile,
    )

    profile = [
        (0.0, 1000.0),
        (100.0, 1010.0),
    ]

    with pytest.raises(ValueError):
        sample_elevation_profile(
            profile,
            step=step,
        )


def test_calculate_profile_grades():
    from stelvio_terrain.road_elevation import (
        calculate_profile_grades,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1007.0),
        (150.0, 1004.0),
    ]

    result = calculate_profile_grades(profile)

    assert result == [
        (0.0, 50.0, 10.0),
        (50.0, 100.0, 4.0),
        (100.0, 150.0, -6.0),
    ]


def test_reconstruct_road_profile_does_not_modify_input():
    from stelvio_terrain.road_elevation import (
        reconstruct_road_profile,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    original = list(profile)

    result = reconstruct_road_profile(profile)

    assert profile == original
    assert result == original
    assert result is not profile


def test_road_elevation_correction_requires_confirmation():
    from stelvio_terrain.road_elevation import (
        should_correct_road_elevation,
    )

    assert should_correct_road_elevation(
        grade_disagreement=13.09,
        confirmed_error=False,
    ) is False

    assert should_correct_road_elevation(
        grade_disagreement=13.09,
        confirmed_error=True,
    ) is True


def test_road_elevation_correction_requires_explicit_true():
    from stelvio_terrain.road_elevation import (
        should_correct_road_elevation,
    )

    assert should_correct_road_elevation(
        grade_disagreement=13.09,
        confirmed_error="False",
    ) is False


def test_apply_road_elevation_correction_without_confirmation():
    from stelvio_terrain.road_elevation import (
        apply_road_elevation_correction,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    result = apply_road_elevation_correction(
        profile,
        index=1,
        corrected_elevation=1008.0,
        confirmed_error=False,
    )

    assert result == profile
    assert result is not profile


def test_apply_road_elevation_correction_with_confirmation():
    from stelvio_terrain.road_elevation import (
        apply_road_elevation_correction,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    result = apply_road_elevation_correction(
        profile,
        index=1,
        corrected_elevation=1008.0,
        confirmed_error=True,
    )

    assert result == [
        (0.0, 1000.0),
        (50.0, 1008.0),
        (100.0, 1010.0),
    ]

    assert profile[1] == (50.0, 1005.0)
    assert result is not profile


@pytest.mark.parametrize("index", [-1, 3])
def test_apply_road_elevation_correction_rejects_invalid_index(index):
    from stelvio_terrain.road_elevation import (
        apply_road_elevation_correction,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    with pytest.raises(IndexError):
        apply_road_elevation_correction(
            profile,
            index=index,
            corrected_elevation=1008.0,
            confirmed_error=True,
        )


def test_corrected_profile_grades_can_be_checked():
    from stelvio_terrain.road_elevation import (
        apply_road_elevation_correction,
        calculate_profile_grades,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    corrected = apply_road_elevation_correction(
        profile,
        index=1,
        corrected_elevation=1020.0,
        confirmed_error=True,
    )

    grades = calculate_profile_grades(corrected)

    assert grades == [
        (0.0, 50.0, 40.0),
        (50.0, 100.0, -20.0),
    ]


def test_road_profile_respects_maximum_grade():
    from stelvio_terrain.road_elevation import (
        is_road_profile_grade_acceptable,
    )

    acceptable_profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    unacceptable_profile = [
        (0.0, 1000.0),
        (50.0, 1020.0),
        (100.0, 1010.0),
    ]

    assert is_road_profile_grade_acceptable(
        acceptable_profile,
        max_grade_percent=15.0,
    ) is True

    assert is_road_profile_grade_acceptable(
        unacceptable_profile,
        max_grade_percent=15.0,
    ) is False


def test_road_elevation_correction_rejects_excessive_grade():
    from stelvio_terrain.road_elevation import (
        apply_road_elevation_correction,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    with pytest.raises(ValueError):
        apply_road_elevation_correction(
            profile,
            index=1,
            corrected_elevation=1020.0,
            confirmed_error=True,
            max_grade_percent=15.0,
        )

    assert profile == [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]


def test_road_elevation_correction_accepts_valid_grade():
    from stelvio_terrain.road_elevation import (
        apply_road_elevation_correction,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    corrected = apply_road_elevation_correction(
        profile,
        index=1,
        corrected_elevation=1007.0,
        confirmed_error=True,
        max_grade_percent=15.0,
    )

    assert corrected == [
        (0.0, 1000.0),
        (50.0, 1007.0),
        (100.0, 1010.0),
    ]

    assert profile[1] == (50.0, 1005.0)


def test_road_elevation_correction_checks_only_adjacent_segments():
    from stelvio_terrain.road_elevation import (
        apply_road_elevation_correction,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1020.0),   # Postojeći nagib 40%
        (100.0, 1025.0),
        (150.0, 1030.0),
        (200.0, 1035.0),
    ]

    corrected = apply_road_elevation_correction(
        profile,
        index=3,
        corrected_elevation=1032.0,
        confirmed_error=True,
        max_grade_percent=15.0,
    )

    assert corrected[3] == (150.0, 1032.0)
    assert profile[3] == (150.0, 1030.0)


def test_road_elevation_correction_at_first_point():
    from stelvio_terrain.road_elevation import (
        apply_road_elevation_correction,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    corrected = apply_road_elevation_correction(
        profile,
        index=0,
        corrected_elevation=1002.0,
        confirmed_error=True,
        max_grade_percent=15.0,
    )

    assert corrected == [
        (0.0, 1002.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    assert profile[0] == (0.0, 1000.0)


def test_road_elevation_correction_at_last_point():
    from stelvio_terrain.road_elevation import (
        apply_road_elevation_correction,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    corrected = apply_road_elevation_correction(
        profile,
        index=2,
        corrected_elevation=1008.0,
        confirmed_error=True,
        max_grade_percent=15.0,
    )

    assert corrected == [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1008.0),
    ]

    assert profile == [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]


def test_road_elevation_anchor_candidate_is_unconfirmed():
    from stelvio_terrain.road_elevation import (
        create_road_elevation_anchor,
    )

    anchor = create_road_elevation_anchor(
        distance=24872.63,
        elevation=2758.0,
        source="OSM Stelvio Pass",
        confirmed=False,
    )

    assert anchor == {
        "distance": 24872.63,
        "elevation": 2758.0,
        "source": "OSM Stelvio Pass",
        "confirmed": False,
    }


def test_unconfirmed_anchor_does_not_change_road_profile():
    from stelvio_terrain.road_elevation import (
        create_road_elevation_anchor,
        apply_road_elevation_anchor,
    )

    profile = [
        (0.0, 2743.0),
        (50.0, 2748.0),
        (100.0, 2751.0),
    ]

    anchor = create_road_elevation_anchor(
        distance=100.0,
        elevation=2758.0,
        source="OSM Stelvio Pass",
        confirmed=False,
    )

    result = apply_road_elevation_anchor(
        profile,
        index=2,
        anchor=anchor,
    )

    assert result == profile
    assert result is not profile
    assert profile[-1] == (100.0, 2751.0)


def test_road_elevation_anchor_rejects_wrong_distance():
    import pytest

    from stelvio_terrain.road_elevation import (
        create_road_elevation_anchor,
        apply_road_elevation_anchor,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    anchor = create_road_elevation_anchor(
        distance=100.0,
        elevation=1012.0,
        source="Verified survey",
        confirmed=True,
    )

    with pytest.raises(ValueError):
        apply_road_elevation_anchor(
            profile,
            index=1,
            anchor=anchor,
        )

    assert profile[1] == (50.0, 1005.0)


def test_confirmed_anchor_corrects_matching_road_point():
    from stelvio_terrain.road_elevation import (
        create_road_elevation_anchor,
        apply_road_elevation_anchor,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    anchor = create_road_elevation_anchor(
        distance=100.0,
        elevation=1012.0,
        source="Verified survey",
        confirmed=True,
    )

    result = apply_road_elevation_anchor(
        profile,
        index=2,
        anchor=anchor,
    )

    assert result[-1] == (100.0, 1012.0)
    assert result[:2] == profile[:2]
    assert profile[-1] == (100.0, 1010.0)


def test_confirmed_anchor_rejects_excessive_road_grade():
    import pytest

    from stelvio_terrain.road_elevation import (
        create_road_elevation_anchor,
        apply_road_elevation_anchor,
    )

    profile = [
        (0.0, 1000.0),
        (50.0, 1005.0),
        (100.0, 1010.0),
    ]

    anchor = create_road_elevation_anchor(
        distance=100.0,
        elevation=1030.0,
        source="Verified survey",
        confirmed=True,
    )

    with pytest.raises(ValueError):
        apply_road_elevation_anchor(
            profile,
            index=2,
            anchor=anchor,
            max_grade_percent=15.0,
        )

    assert profile[-1] == (100.0, 1010.0)