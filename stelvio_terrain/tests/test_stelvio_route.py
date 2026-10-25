
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







