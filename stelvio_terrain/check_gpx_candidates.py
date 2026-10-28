from pathlib import Path
import xml.etree.ElementTree as ET
from stelvio_terrain.road_elevation import (
    sample_elevation_profile, calculate_profile_grades,
)


from pyproj import Geod

from stelvio_terrain.road_elevation import (
    find_constant_elevation_runs,
    get_constant_elevation_run_indices,
    get_non_plateau_indices,
)

gpx_path = Path(
    "stelvio_terrain/data/"
    "salita-al-passo-dello-stelvio-da-prato.gpx"
)

root = ET.parse(gpx_path).getroot()
points = []

for element in root.iter():
    if element.tag.split("}")[-1] not in ("trkpt", "rtept"):
        continue

    elevation = next(
        (
            float(child.text)
            for child in element
            if child.tag.split("}")[-1] == "ele"
            and child.text is not None
        ),
        None,
    )

    if elevation is not None:
        points.append((
            float(element.attrib["lon"]),
            float(element.attrib["lat"]),
            elevation,
        ))

geod = Geod(ellps="WGS84")
profile = []
distance = 0.0

for i, (lon, lat, elevation) in enumerate(points):
    if i > 0:
        previous_lon, previous_lat, _ = points[i - 1]
        _, _, segment_length = geod.inv(
            previous_lon, previous_lat, lon, lat
        )
        distance += segment_length

    profile.append((distance, elevation))

runs = find_constant_elevation_runs(profile, 50.0)
plateau_indices = get_constant_elevation_run_indices(runs)
candidate_indices = get_non_plateau_indices(
    len(profile), plateau_indices
)

print("GPX points:", len(profile))
print("Long plateaus:", len(runs))
print("Points on plateaus:", len(plateau_indices))
print("Points outside plateaus:", len(candidate_indices))
print(
    "Candidate percentage:",
    round(100 * len(candidate_indices) / len(profile), 2),
)
from stelvio_terrain.road_elevation import (
    is_gpx_segment_length_acceptable,
)

acceptable = 0
too_short = 0
too_long = 0

for i in range(1, len(points)):
    lon1, lat1, _ = points[i - 1]
    lon2, lat2, _ = points[i]

    _, _, length = geod.inv(
        lon1, lat1,
        lon2, lat2,
    )

    if is_gpx_segment_length_acceptable(
        length, 10.0, 100.0
    ):
        acceptable += 1
    elif length < 10.0:
        too_short += 1
    else:
        too_long += 1

print()
print("GPX segments:", len(points) - 1)
print("Acceptable (10-100 m):", acceptable)
print("Too short (<10 m):", too_short)
print("Too long (>100 m):", too_long)
grades = []

for i in range(1, len(profile)):
    d1, z1 = profile[i - 1]
    d2, z2 = profile[i]

    length = d2 - d1

    if not is_gpx_segment_length_acceptable(
        length, 10.0, 100.0
    ):
        continue

    grade = 100.0 * (z2 - z1) / length
    grades.append((i - 1, i, grade))

steep = [
    item for item in grades
    if abs(item[2]) > 20.0
]

print()
print("Analyzed segments:", len(grades))
print("Segments above 20%:", len(steep))

if grades:
    worst = max(grades, key=lambda item: abs(item[2]))

    print(
        "Maximum absolute grade:",
        round(abs(worst[2]), 2),
        "%"
    )
    print("Segment indices:", worst[:2])
    print()
print("Steepest GPX segment:")

for i in range(93, 99):
    distance, elevation = profile[i]

    print(
        f"Point {i:3d}: "
        f"distance={distance:9.1f} m, "
        f"elevation={elevation:7.1f} m"
    )

d1, z1 = profile[95]
d2, z2 = profile[96]

print()
print(f"Segment length: {d2 - d1:.2f} m")
print(f"Elevation change: {z2 - z1:+.2f} m")
print(f"Grade: {100 * (z2 - z1) / (d2 - d1):+.2f}%")
import rasterio
from scipy.ndimage import map_coordinates

dem_path = (
    "stelvio_terrain/data/dem/output_hh.tif"
)

with rasterio.open(dem_path) as dem:
    data = dem.read(1)

    print()
    print("GPX vs DEM:")

    for i in range(93, 99):
        lon, lat, gpx_z = points[i]

        col, row = (~dem.transform) * (lon, lat)

        dem_z = float(
            map_coordinates(
                data,
                [[row - 0.5], [col - 0.5]],
                order=1,
                mode="nearest",
            )[0]
        )

        print(
            f"{i:3d}: "
            f"GPX={gpx_z:7.1f} m, "
            f"DEM={dem_z:7.1f} m, "
            f"diff={gpx_z - dem_z:+7.1f} m"
        )
        start = 93
end = 98

distance = profile[end][0] - profile[start][0]

gpx_rise = profile[end][1] - profile[start][1]

print()
print("GPX interval 93-98:")
print(f"Length: {distance:.2f} m")
print(f"Elevation gain: {gpx_rise:+.2f} m")
print(f"Average grade: {100 * gpx_rise / distance:+.2f}%")
with rasterio.open(dem_path) as dem:
    data = dem.read(1)

    dem_heights = []

    for i in (93, 98):
        lon, lat, _ = points[i]
        col, row = (~dem.transform) * (lon, lat)

        height = float(
            map_coordinates(
                data,
                [[row - 0.5], [col - 0.5]],
                order=1,
                mode="nearest",
            )[0]
        )

        dem_heights.append(height)

dem_rise = dem_heights[1] - dem_heights[0]
distance = profile[98][0] - profile[93][0]

print()
print("Interval 93-98:")
print(f"GPX average grade: {100 * 31.0 / distance:.2f}%")
print(f"DEM elevation gain: {dem_rise:+.2f} m")
print(f"DEM average grade: {100 * dem_rise / distance:+.2f}%")
start = 90
end = 105

with rasterio.open(dem_path) as dem:
    data = dem.read(1)
    dem_heights = []

    for i in (start, end):
        lon, lat, _ = points[i]
        col, row = (~dem.transform) * (lon, lat)

        dem_heights.append(
            float(
                map_coordinates(
                    data,
                    [[row - 0.5], [col - 0.5]],
                    order=1,
                    mode="nearest",
                )[0]
            )
        )

distance = profile[end][0] - profile[start][0]
gpx_rise = profile[end][1] - profile[start][1]
dem_rise = dem_heights[1] - dem_heights[0]

print()
print(f"Interval {start}-{end}:")
print(f"Length: {distance:.2f} m")
print(f"GPX rise: {gpx_rise:+.2f} m")
print(f"DEM rise: {dem_rise:+.2f} m")
print(f"GPX grade: {100 * gpx_rise / distance:+.2f}%")
print(f"DEM grade: {100 * dem_rise / distance:+.2f}%")
with rasterio.open(dem_path) as dem:
    data = dem.read(1)

    print()
    print("GPX - DEM differences (90-105):")

    for i in range(90, 106):
        lon, lat, gpx_z = points[i]
        col, row = (~dem.transform) * (lon, lat)

        dem_z = float(
            map_coordinates(
                data,
                [[row - 0.5], [col - 0.5]],
                order=1,
                mode="nearest",
            )[0]
        )

        print(
            f"{i:3d}: "
            f"GPX={gpx_z:7.1f} "
            f"DEM={dem_z:7.1f} "
            f"diff={gpx_z - dem_z:+7.1f}"
        )
    start = 91
    end = 92

    distance = profile[end][0] - profile[start][0]
    gpx_rise = profile[end][1] - profile[start][1]

    print()
    print("Segment 91-92:")
    print(f"Length: {distance:.2f} m")
    print(f"GPX rise: {gpx_rise:+.2f} m")
    print(f"GPX grade: {100 * gpx_rise / distance:+.2f}%")
start = 90
end = 91

distance = profile[end][0] - profile[start][0]
gpx_rise = profile[end][1] - profile[start][1]

print()
print("Segment 90-91:")
print(f"Length: {distance:.2f} m")
print(f"GPX rise: {gpx_rise:+.2f} m")
print(f"GPX grade: {100 * gpx_rise / distance:+.2f}%")    
with rasterio.open(dem_path) as dem:
    print()
    print("DEM coordinate system:")
    print(f"CRS: {dem.crs}")
    print(f"Resolution: {dem.res}")
    print(f"Bounds: {dem.bounds}")
with rasterio.open(dem_path) as dem:
    print()
    print("DEM data validity:")
    print(f"NoData value: {dem.nodata}")
    print(f"Minimum valid elevation: {dem.read(1, masked=True).min()}")
    print(f"Maximum valid elevation: {dem.read(1, masked=True).max()}")
with rasterio.open(dem_path) as dem:
    elevation = dem.read(1, masked=True)

    print()
    print("DEM mask:")
    print(f"Masked pixels: {int(elevation.mask.sum())}")
    print(f"Total pixels: {elevation.size}")

import numpy as np

with rasterio.open(dem_path) as dem:
    elevation = dem.read(1)

    print()
    print("DEM numeric validity:")
    print(f"NaN pixels: {np.isnan(elevation).sum()}")
    print(f"Infinite pixels: {np.isinf(elevation).sum()}")
    print(f"Finite pixels: {np.isfinite(elevation).sum()}")

from stelvio_terrain.road_elevation import (
    elevation_grade_disagreement_percent,
    is_grade_disagreement_significant,
)

significant_count = 0
checked_count = 0
dem_elevations = []

with rasterio.open(dem_path) as dem:
    elevation = dem.read(1)

    for lon, lat, _ in points:
        col, row = (~dem.transform) * (lon, lat)

        dem_z = map_coordinates(
            elevation,
            [[row - 0.5], [col - 0.5]],
            order=1,
            mode="nearest",
        )[0]

        dem_elevations.append(float(dem_z))
for i in range(1, len(profile)):
    distance = profile[i][0] - profile[i - 1][0]

    if distance <= 0:
        continue

    gpx_rise = profile[i][1] - profile[i - 1][1]
    dem_rise = dem_elevations[i] - dem_elevations[i - 1]

    disagreement = elevation_grade_disagreement_percent(
        gpx_rise - dem_rise,
        distance,
    )

    checked_count += 1

    if is_grade_disagreement_significant(disagreement, 5.0):
        significant_count += 1

print()
print("GPX vs DEM grade disagreement:")
print(f"Checked segments: {checked_count}")
print(f"Significant disagreements: {significant_count}")
print(f"Percentage: {100 * significant_count / checked_count:.2f}%")
filtered_count = 0
filtered_significant = 0

for i in range(1, len(profile)):
    distance = profile[i][0] - profile[i - 1][0]

    if not 10.0 <= distance <= 100.0:
        continue

    gpx_rise = profile[i][1] - profile[i - 1][1]
    dem_rise = dem_elevations[i] - dem_elevations[i - 1]

    disagreement = elevation_grade_disagreement_percent(
        gpx_rise - dem_rise,
        distance,
    )

    filtered_count += 1

    if is_grade_disagreement_significant(disagreement, 5.0):
        filtered_significant += 1

print()
print("GPX vs DEM (segments 10-100 m):")
print(f"Checked segments: {filtered_count}")
print(f"Significant disagreements: {filtered_significant}")
print(f"Percentage: {100 * filtered_significant / filtered_count:.2f}%")
total_length = 0.0
significant_length = 0.0

for i in range(1, len(profile)):
    distance = profile[i][0] - profile[i - 1][0]

    if not 10.0 <= distance <= 100.0:
        continue

    gpx_rise = profile[i][1] - profile[i - 1][1]
    dem_rise = dem_elevations[i] - dem_elevations[i - 1]

    disagreement = elevation_grade_disagreement_percent(
        gpx_rise - dem_rise,
        distance,
    )

    total_length += distance

    if is_grade_disagreement_significant(disagreement, 5.0):
        significant_length += distance

print()
print("Length-weighted disagreement (10-100 m):")
print(f"Total length: {total_length:.1f} m")
print(f"Significant length: {significant_length:.1f} m")
print(f"Percentage: {100 * significant_length / total_length:.2f}%")
gpx_total_rise = profile[-1][1] - profile[0][1]
dem_total_rise = dem_elevations[-1] - dem_elevations[0]

print()
print("Full GPX route elevation comparison:")
print(f"GPX net rise: {gpx_total_rise:+.2f} m")
print(f"DEM net rise: {dem_total_rise:+.2f} m")
print(f"Difference: {gpx_total_rise - dem_total_rise:+.2f} m")
print()
print("GPX route endpoints:")

for i in (0, len(profile) - 1):
    gpx_z = profile[i][1]
    dem_z = dem_elevations[i]

    print(
        f"Point {i}: "
        f"GPX={gpx_z:.2f} m, "
        f"DEM={dem_z:.2f} m, "
        f"Difference={gpx_z - dem_z:+.2f} m"
    )

middle_distance = profile[-1][0] / 2

middle_index = min(
    range(len(profile)),
    key=lambda i: abs(profile[i][0] - middle_distance),
)

gpx_z = profile[middle_index][1]
dem_z = dem_elevations[middle_index]

print()
print("GPX route midpoint:")
print(f"Point index: {middle_index}")
print(f"Distance: {profile[middle_index][0]:.2f} m")
print(f"GPX elevation: {gpx_z:.2f} m")
print(f"DEM elevation: {dem_z:.2f} m")
print(f"Difference: {gpx_z - dem_z:+.2f} m")
import numpy as np

absolute_differences = [
    abs(profile[i][1] - dem_elevations[i])
    for i in range(len(profile))
]

print()
print("GPX vs DEM absolute elevation differences:")
print(f"Median: {np.median(absolute_differences):.2f} m")
print(f"95th percentile: {np.percentile(absolute_differences, 95):.2f} m")
print(f"Maximum: {np.max(absolute_differences):.2f} m")
max_index = int(np.argmax(absolute_differences))

print()
print("Maximum GPX vs DEM difference:")
print(f"Point index: {max_index}")
print(f"Distance: {profile[max_index][0]:.2f} m")
print(f"GPX elevation: {profile[max_index][1]:.2f} m")
print(f"DEM elevation: {dem_elevations[max_index]:.2f} m")
print(
    f"Difference: "
    f"{profile[max_index][1] - dem_elevations[max_index]:+.2f} m"
)
print()
print("GPX vs DEM around point 55:")

for i in range(50, 61):
    gpx_z = profile[i][1]
    dem_z = dem_elevations[i]

    print(
        f"{i:3d}: "
        f"s={profile[i][0]:8.1f} m "
        f"GPX={gpx_z:7.1f} "
        f"DEM={dem_z:7.1f} "
        f"diff={gpx_z - dem_z:+7.1f}"
    )
print()
print("Grades around point 55:")

for i in range(53, 58):
    distance = profile[i + 1][0] - profile[i][0]

    gpx_rise = profile[i + 1][1] - profile[i][1]
    dem_rise = dem_elevations[i + 1] - dem_elevations[i]

    print(
        f"{i:3d}-{i+1}: "
        f"length={distance:6.1f} m "
        f"GPX={100 * gpx_rise / distance:+6.2f}% "
        f"DEM={100 * dem_rise / distance:+6.2f}%"
    )
from math import atan2, degrees, cos, radians

def segment_heading(a, b):
    lon1, lat1, _ = a
    lon2, lat2, _ = b

    dx = (lon2 - lon1) * cos(radians((lat1 + lat2) / 2))
    dy = lat2 - lat1

    return degrees(atan2(dx, dy))

heading_before = segment_heading(points[54], points[55])
heading_after = segment_heading(points[55], points[56])

turn_angle = (heading_after - heading_before + 180) % 360 - 180

print()
print("GPX geometry at point 55:")
print(f"Heading 54-55: {heading_before:.2f} degrees")
print(f"Heading 55-56: {heading_after:.2f} degrees")
print(f"Turn angle: {turn_angle:+.2f} degrees")
lon, lat, elevation = points[55]

print()
print("GPX point 55:")
print(f"Longitude: {lon:.8f}")
print(f"Latitude: {lat:.8f}")
print(f"Elevation: {elevation:.2f} m")
from pyproj import Geod

geod = Geod(ellps="WGS84")

lon, lat, _ = points[57]

# Smer puta između tačaka 54 i 56
heading, _, _ = geod.inv(
    points[56][0], points[56][1],
    points[58][0], points[58][1],
)

with rasterio.open(dem_path) as dem:
    elevation = dem.read(1)

    print()
    print("DEM cross-section at GPX point 55:")

    for offset in (-60.0, -45.0, -30.0, -15.0, 0.0, 15.0, 30.0, 45.0, 60.0):
        if offset < 0:
            azimuth = heading - 90.0
        else:
            azimuth = heading + 90.0

        sample_lon, sample_lat, _ = geod.fwd(
            lon, lat, azimuth, abs(offset)
        )

        col, row = (~dem.transform) * (sample_lon, sample_lat)

        dem_z = float(map_coordinates(
            elevation,
            [[row - 0.5], [col - 0.5]],
            order=1,
            mode="nearest",
        )[0])

        print(f"Offset {offset:+5.0f} m: DEM={dem_z:.2f} m")
'''z_left_45 = 1100.32
z_left_30 = 1090.68
target_z = points[56][2]

fraction = (target_z - z_left_45) / (z_left_30 - z_left_45)

estimated_offset = -45.0 + fraction * 15.0

print()
print("DEM elevation match at point 57:")

print(f"GPX elevation: {target_z:.2f} m")
print(f"Estimated lateral offset: {estimated_offset:.2f} m")'''
start = 55
end = 57

distance = profile[end][0] - profile[start][0]

gpx_rise = profile[end][1] - profile[start][1]
dem_rise = dem_elevations[end] - dem_elevations[start]

print()
print("Longitudinal comparison 55-57:")
print(f"Length: {distance:.2f} m")
print(f"GPX rise: {gpx_rise:+.2f} m")
print(f"DEM rise: {dem_rise:+.2f} m")
print(f"GPX grade: {100 * gpx_rise / distance:+.2f}%")
print(f"DEM grade: {100 * dem_rise / distance:+.2f}%")
from stelvio_terrain.road_elevation import (
    find_suspicious_grade_segments,
)
print()
print("Non-positive GPX segment lengths:")

for i in range(len(profile) - 1):
    distance = profile[i + 1][0] - profile[i][0]

    if distance <= 0:
        print(
            f"Segment {i}->{i + 1}: "
            f"distance={distance:.6f} m, "
            f"elevations={profile[i][1]:.2f} -> "
            f"{profile[i + 1][1]:.2f} m"
        )
suspicious = find_suspicious_grade_segments(
    profile,
    max_grade_percent=15.0,
)

print()
print("Stelvio GPX grade analysis:")
print(f"Total segments: {len(profile) - 1}")
print(f"Suspicious segments: {len(suspicious)}")
print(f"Percentage: {100 * len(suspicious) / (len(profile) - 1):.2f}%")
print(f"First 10 suspicious indices: {suspicious[:10]}")
suspicious_lengths = [
    profile[i + 1][0] - profile[i][0]
    for i in suspicious
]

print()
print("Suspicious segment lengths:")
print(f"Minimum: {min(suspicious_lengths):.2f} m")
print(f"Maximum: {max(suspicious_lengths):.2f} m")
print(
    f"Shorter than 20 m: "
    f"{sum(length < 20 for length in suspicious_lengths)}"
)
print(
    f"Shorter than 50 m: "
    f"{sum(length < 50 for length in suspicious_lengths)}"
)
total_suspicious_length = sum(suspicious_lengths)

total_route_length = profile[-1][0] - profile[0][0]

print()
print("Suspicious road length:")
print(f"Suspicious length: {total_suspicious_length:.2f} m")
print(f"Total route length: {total_route_length:.2f} m")
print(
    f"Suspicious road percentage: "
    f"{100 * total_suspicious_length / total_route_length:.2f}%"
)
from stelvio_terrain.road_elevation import (
    is_profile_elevation_spike,
)

spike_candidates = []

for i in range(1, len(profile) - 1):
    distance_before = profile[i][0] - profile[i - 1][0]
    distance_after = profile[i + 1][0] - profile[i][0]

    # Preskačemo segmente nulte dužine.
    if distance_before <= 0 or distance_after <= 0:
        continue

    if is_profile_elevation_spike(
        profile,
        index=i,
        threshold=15.0,
    ):
        spike_candidates.append(i)

print()
print("Stelvio elevation spike analysis:")
print(f"Spike candidates: {len(spike_candidates)}")
print(f"Candidate indices: {spike_candidates}")

reversals = []

for i in range(1, len(profile) - 1):
    d_before = profile[i][0] - profile[i - 1][0]
    d_after = profile[i + 1][0] - profile[i][0]

    if d_before <= 0 or d_after <= 0:
        continue

    grade_before = 100.0 * (
        profile[i][1] - profile[i - 1][1]
    ) / d_before

    grade_after = 100.0 * (
        profile[i + 1][1] - profile[i][1]
    ) / d_after

    if grade_before * grade_after < 0:
        reversals.append(
            (i, grade_before, grade_after)
        )

print()
print("GPX grade reversals:")
print(f"Total reversals: {len(reversals)}")
print("First 10 reversals:")

for i, before, after in reversals[:10]:
    print(
        f"Point {i}: "
        f"{before:+.2f}% -> {after:+.2f}%"
    )

start = 55
target_distance = profile[start][0] + 100.0

end = next(
    i
    for i in range(start + 1, len(profile))
    if profile[i][0] >= target_distance
)

distance = profile[end][0] - profile[start][0]
rise = profile[end][1] - profile[start][1]

print()
print("GPX 100 m grade:")
print(f"Start index: {start}")
print(f"End index: {end}")
print(f"Distance: {distance:.2f} m")
print(f"Elevation change: {rise:+.2f} m")
print(f"Average grade: {100.0 * rise / distance:+.2f}%")

from stelvio_terrain.road_elevation import (
    interpolate_profile_elevation,
)

start = 55

start_distance = profile[start][0]
start_elevation = profile[start][1]

target_distance = start_distance + 100.0

target_elevation = interpolate_profile_elevation(
    profile,
    distance=target_distance,
)

rise = target_elevation - start_elevation
grade = 100.0 * rise / 100.0

print()
print("GPX exact 100 m grade:")
print(f"Start elevation: {start_elevation:.2f} m")
print(f"End elevation: {target_elevation:.2f} m")
print(f"Elevation change: {rise:+.2f} m")
print(f"Average grade: {grade:+.2f}%")

dem_profile = [
    (profile[i][0], dem_elevations[i])
    for i in range(len(profile))
]

dem_start_elevation = dem_elevations[start]

dem_target_elevation = interpolate_profile_elevation(
    dem_profile,
    distance=target_distance,
)

dem_rise = dem_target_elevation - dem_start_elevation
dem_grade = 100.0 * dem_rise / 100.0

print()
print("DEM exact 100 m grade:")
print(f"Start elevation: {dem_start_elevation:.2f} m")
print(f"End elevation: {dem_target_elevation:.2f} m")
print(f"Elevation change: {dem_rise:+.2f} m")
print(f"Average grade: {dem_grade:+.2f}%")
print(f"Grade disagreement: {grade - dem_grade:+.2f} percentage points")
difference_start = (
    start_elevation - dem_start_elevation
)

difference_end = (
    target_elevation - dem_target_elevation
)

print()
print("GPX-DEM difference over 100 m:")
print(f"Difference at start: {difference_start:+.2f} m")
print(f"Difference at end: {difference_end:+.2f} m")
print(
    f"Difference change: "
    f"{difference_end - difference_start:+.2f} m"
)

differences = [
    profile[i][1] - dem_elevations[i]
    for i in range(len(profile))
]

changes = [
    differences[i + 1] - differences[i]
    for i in range(len(differences) - 1)
]

largest_index = max(
    range(len(changes)),
    key=lambda i: abs(changes[i]),
)

print()
print("Largest GPX-DEM difference change:")
print(f"Segment: {largest_index}->{largest_index + 1}")
print(f"Length: {profile[largest_index + 1][0] - profile[largest_index][0]:.2f} m")
print(f"Difference before: {differences[largest_index]:+.2f} m")
print(f"Difference after: {differences[largest_index + 1]:+.2f} m")
print(f"Difference change: {changes[largest_index]:+.2f} m")

i = 91

segment_length = profile[i + 1][0] - profile[i][0]

gpx_rise = profile[i + 1][1] - profile[i][1]
dem_rise = dem_elevations[i + 1] - dem_elevations[i]

print()
print("Segment 91-92 grade comparison:")
print(f"GPX rise: {gpx_rise:+.2f} m")
print(f"DEM rise: {dem_rise:+.2f} m")
print(f"GPX grade: {100 * gpx_rise / segment_length:+.2f}%")
print(f"DEM grade: {100 * dem_rise / segment_length:+.2f}%")
print()
print("GPX elevations around segment 91-92:")

for i in range(88, 96):
    distance, elevation = profile[i]

    print(
        f"Point {i}: "
        f"distance={distance:.2f} m, "
        f"elevation={elevation:.2f} m"
    )
start = 90
end = 95

distance = profile[end][0] - profile[start][0]

gpx_rise = profile[end][1] - profile[start][1]
dem_rise = dem_elevations[end] - dem_elevations[start]

print()
print("Extended grade comparison 90-95:")
print(f"Distance: {distance:.2f} m")
print(f"GPX rise: {gpx_rise:+.2f} m")
print(f"DEM rise: {dem_rise:+.2f} m")
print(f"GPX grade: {100 * gpx_rise / distance:+.2f}%")
print(f"DEM grade: {100 * dem_rise / distance:+.2f}%")



dem_profile = [
    (profile[i][0], dem_elevations[i])
    for i in range(len(profile))
]

gpx_50m = sample_elevation_profile(
    profile,
    step=50.0,
)

dem_50m = sample_elevation_profile(
    dem_profile,
    step=50.0,
)

print()
print("Stelvio 50 m sampling:")
print(f"GPX samples: {len(gpx_50m)}")
print(f"DEM samples: {len(dem_50m)}")
print(f"First distance: {gpx_50m[0][0]:.2f} m")
print(f"Last distance: {gpx_50m[-1][0]:.2f} m")

same_distances = all(
    gpx[0] == dem[0]
    for gpx, dem in zip(gpx_50m, dem_50m)
)

print(f"Same distances: {same_distances}")

print()
print("First five 50 m intervals:")

for i in range(5):
    distance = gpx_50m[i + 1][0] - gpx_50m[i][0]

    gpx_rise = gpx_50m[i + 1][1] - gpx_50m[i][1]
    dem_rise = dem_50m[i + 1][1] - dem_50m[i][1]

    gpx_grade = 100.0 * gpx_rise / distance
    dem_grade = 100.0 * dem_rise / distance

    print(
        f"{gpx_50m[i][0]:.0f}-{gpx_50m[i + 1][0]:.0f} m: "
        f"GPX={gpx_grade:+.2f}%, "
        f"DEM={dem_grade:+.2f}%, "
        f"difference={gpx_grade - dem_grade:+.2f} pp"
    )


gpx_grades = calculate_profile_grades(gpx_50m)
dem_grades = calculate_profile_grades(dem_50m)

print()
print("Stelvio grade profiles:")
print(f"GPX segments: {len(gpx_grades)}")
print(f"DEM segments: {len(dem_grades)}")

same_intervals = all(
    gpx[:2] == dem[:2]
    for gpx, dem in zip(gpx_grades, dem_grades)
)

print(f"Same intervals: {same_intervals}")
print(f"First GPX grade: {gpx_grades[0][2]:+.2f}%")
print(f"First DEM grade: {dem_grades[0][2]:+.2f}%")

threshold = 5.0

significant_disagreements = [
    i
    for i, (gpx, dem) in enumerate(
        zip(gpx_grades, dem_grades)
    )
    if abs(gpx[2] - dem[2]) > threshold
]

total_segments = len(gpx_grades)
significant_count = len(significant_disagreements)

print()
print("Stelvio 50 m grade disagreement:")
print(f"Total segments: {total_segments}")
print(f"Threshold: {threshold:.1f} percentage points")
print(f"Significant disagreements: {significant_count}")
print(
    f"Percentage: "
    f"{100.0 * significant_count / total_segments:.2f}%"
)
significant_length = sum(
    gpx_grades[i][1] - gpx_grades[i][0]
    for i in significant_disagreements
)

total_length = sum(
    end - start
    for start, end, grade in gpx_grades
)

print()
print("Stelvio grade disagreement by distance:")
print(f"Total route length: {total_length / 1000:.3f} km")
print(f"Significant disagreement length: {significant_length / 1000:.3f} km")
print(
    f"Distance percentage: "
    f"{100.0 * significant_length / total_length:.2f}%"
)

integer_elevations = sum(
    elevation == int(elevation)
    for _, _, elevation in points
)

print()
print("GPX elevation precision:")
print(f"Total points: {len(points)}")
print(f"Integer elevations: {integer_elevations}")
print(
    f"Fractional elevations: "
    f"{len(points) - integer_elevations}"
)

print()
print("GPX final point:")
print(f"Longitude: {points[-1][0]:.8f}")
print(f"Latitude: {points[-1][1]:.8f}")
print(f"GPX elevation: {points[-1][2]:.2f} m")
print(f"DEM elevation: {dem_elevations[-1]:.2f} m")

pass_lon = 10.4532056
pass_lat = 46.5286176

gpx_lon, gpx_lat, gpx_elevation = points[-1]

_, _, distance_to_pass = Geod(ellps="WGS84").inv(
    gpx_lon,
    gpx_lat,
    pass_lon,
    pass_lat,
)

print()
print("Stelvio summit reference:")
print(f"Distance GPX endpoint to OSM pass: {distance_to_pass:.2f} m")
print(f"GPX elevation: {gpx_elevation:.2f} m")
print(f"DEM elevation: {dem_elevations[-1]:.2f} m")
print(f"OSM pass elevation label: 2758 m")

print()
print("Last 10 GPX/DEM elevations:")

for i in range(len(points) - 10, len(points)):
    distance, gpx_z = profile[i]
    dem_z = dem_elevations[i]

    print(
        f"Point {i}: "
        f"distance={distance:.2f} m, "
        f"GPX={gpx_z:.2f} m, "
        f"DEM={dem_z:.2f} m, "
        f"diff={gpx_z - dem_z:+.2f} m"
    )

from stelvio_terrain.road_elevation import (
    find_suspicious_grade_segments,
)

suspicious_12 = find_suspicious_grade_segments(
    profile,
    max_grade_percent=12.0,
)

print()
print("Stelvio GPX grade check (12%):")
print(f"Segments above 12%: {len(suspicious_12)}")
print(f"Total GPX segments: {len(profile) - 1}")


suspicious_length_12 = sum(
    profile[i + 1][0] - profile[i][0]
    for i in suspicious_12
)

total_length = profile[-1][0] - profile[0][0]

print(f"Length above 12%: {suspicious_length_12:.2f} m")
print(
    f"Share of route above 12%: "
    f"{100 * suspicious_length_12 / total_length:.2f}%"
)

from stelvio_terrain.road_elevation import (
    sample_elevation_profile,
    calculate_profile_grades,
)

profile_100m = sample_elevation_profile(
    profile,
    step=100.0,
)

grades_100m = calculate_profile_grades(profile_100m)

length_above_12_100m = sum(
    end - start
    for start, end, grade in grades_100m
    if abs(grade) > 12.0
)

print()
print("GPX grade check — 100 m sampling:")
print(f"Intervals: {len(grades_100m)}")
print(f"Length above 12%: {length_above_12_100m:.2f} m")
print(
    f"Share above 12%: "
    f"{100 * length_above_12_100m / total_length:.2f}%"
)

dem_profile = [
    (distance, dem_z)
    for (distance, _), dem_z in zip(profile, dem_elevations)
]

dem_profile_100m = sample_elevation_profile(
    dem_profile,
    step=100.0,
)

dem_grades_100m = calculate_profile_grades(
    dem_profile_100m
)

dem_length_above_12 = sum(
    end - start
    for start, end, grade in dem_grades_100m
    if abs(grade) > 12.0
)

print()
print("DEM grade check — 100 m sampling:")
print(f"Intervals: {len(dem_grades_100m)}")
print(f"Length above 12%: {dem_length_above_12:.2f} m")
print(
    f"Share above 12%: "
    f"{100 * dem_length_above_12 / total_length:.2f}%"
)


gpx_only = 0
dem_only = 0
both = 0

for gpx_segment, dem_segment in zip(
    grades_100m,
    dem_grades_100m,
):
    gpx_steep = abs(gpx_segment[2]) > 12.0
    dem_steep = abs(dem_segment[2]) > 12.0

    if gpx_steep and dem_steep:
        both += 1
    elif gpx_steep:
        gpx_only += 1
    elif dem_steep:
        dem_only += 1

print()
print("GPX vs DEM — grade above 12%:")
print(f"GPX only: {gpx_only}")
print(f"DEM only: {dem_only}")
print(f"Both: {both}")
for gpx_segment, dem_segment in zip(
    grades_100m,
    dem_grades_100m,
):
    start, end, gpx_grade = gpx_segment
    dem_grade = dem_segment[2]

    if abs(gpx_grade) > 12.0 and abs(dem_grade) <= 12.0:
        print()
        print("First GPX-only steep interval:")
        print(f"Distance: {start:.0f}–{end:.0f} m")
        print(f"GPX grade: {gpx_grade:+.2f}%")
        print(f"DEM grade: {dem_grade:+.2f}%")
        break

print()
print("Road elevations at 800–900 m:")

for distance in (800.0, 900.0):
    gpx_z = interpolate_profile_elevation(
        profile,
        distance,
    )

    dem_z = interpolate_profile_elevation(
        dem_profile,
        distance,
    )

    print(
        f"{distance:.0f} m: "
        f"GPX={gpx_z:.2f} m, "
        f"DEM={dem_z:.2f} m, "
        f"GPX-DEM={gpx_z - dem_z:+.2f} m"
    )