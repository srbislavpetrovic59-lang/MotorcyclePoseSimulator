from dataclasses import dataclass
from stelvio_terrain.route_geometry import interpolate_elevation
import math



@dataclass(frozen=True)
class RoadElevationReference:
    """A recorded road elevation reference."""

    point_index: int
    elevation_m: float
    source: str
    verified: bool


def get_verified_reference_indices(
    references,
    excluded_indices=None,
):
    """Return verified indices, excluding specified indices."""

    if excluded_indices is None:
        excluded_indices = set()

    return {
        reference.point_index
        for reference in references
        if (
            reference.verified
            and reference.point_index not in excluded_indices
        )
    }




def get_safe_verified_indices(
    references,
    tolerance_m,
    point_count=None,
):
    """Return valid verified indices without conflicts."""

    references = list(references)

    if point_count is not None:
        if type(point_count) is not int or point_count < 0:
            raise ValueError(
                "Point count must be a non-negative integer"
            )

    for reference in references:
        if not reference.verified:
            continue

        index = reference.point_index

        if type(index) is not int or index < 0:
            raise ValueError(
                "Verified reference index must be "
                "a non-negative integer"
            )

        if point_count is not None and index >= point_count:
            raise ValueError(
                "Verified reference index is out of range"
            )

    conflicts = find_conflicting_references(
        references,
        tolerance_m=tolerance_m,
    )

    return get_verified_reference_indices(
        references,
        excluded_indices=conflicts,
    )



def get_verified_reference_elevation(
    references,
    point_index,
    tolerance_m,
):
    """Return mean elevation of agreeing verified references."""

    references = list(references)

    safe_indices = get_safe_verified_indices(
        references,
        tolerance_m=tolerance_m,
    )

    if point_index not in safe_indices:
        raise ValueError(
            "No safe verified reference for this point"
        )

    elevations = [
        reference.elevation_m
        for reference in references
        if (
            reference.point_index == point_index
            and reference.verified
        )
    ]

    return math.fsum(elevations) / len(elevations)



def apply_boundary_reference_elevations(
    profile,
    references,
    start,
    end,
    tolerance_m,
):
    """Apply verified boundary elevations to a profile copy."""

    if not (0 < start <= end < len(profile) - 1):
        raise ValueError("Zone must have two boundary points")

    references = list(references)

    left_index = start - 1
    right_index = end + 1

    safe_indices = get_safe_verified_indices(
        references,
        tolerance_m=tolerance_m,
        point_count=len(profile),
    )

    if (
        left_index not in safe_indices
        or right_index not in safe_indices
    ):
        raise ValueError(
            "Both boundaries require safe verified references"
        )

    left_elevation = get_verified_reference_elevation(
        references,
        point_index=left_index,
        tolerance_m=tolerance_m,
    )

    right_elevation = get_verified_reference_elevation(
        references,
        point_index=right_index,
        tolerance_m=tolerance_m,
    )

    corrected = list(profile)

    left_distance, _ = corrected[left_index]
    right_distance, _ = corrected[right_index]

    corrected[left_index] = (
        left_distance,
        left_elevation,
    )

    corrected[right_index] = (
        right_distance,
        right_elevation,
    )

    return corrected



def reconstruct_road_zone_from_references(
    profile,
    references,
    start,
    end,
    tolerance_m,
    max_allowed_grade,
):
    """Reconstruct a road zone using verified elevations."""

    references = list(references)

    # 1. Postavi potvrđene visine na granice zone.
    profile_with_boundaries = apply_boundary_reference_elevations(
        profile,
        references,
        start=start,
        end=end,
        tolerance_m=tolerance_m,
    )

    # 2. Izdvoji potvrđene, nekonfliktne indekse.
    verified_indices = get_safe_verified_indices(
        references,
        tolerance_m=tolerance_m,
        point_count=len(profile),
    )

    # 3. Rekonstruiši unutrašnjost zone.
    corrected = reconstruct_road_zone(
        profile_with_boundaries,
        start=start,
        end=end,
        max_allowed_grade=max_allowed_grade,
        verified_indices=verified_indices,
    )

    # 4. Proveri levi spoljašnji prelaz, ako postoji.
    left_boundary = start - 1

    if left_boundary > 0:
        if not is_road_grade_acceptable(
            corrected,
            left_boundary - 1,
            left_boundary,
            max_allowed_grade,
        ):
            raise ValueError(
                "Left transition exceeds allowed road grade"
            )

    # 5. Proveri desni spoljašnji prelaz, ako postoji.
    right_boundary = end + 1

    if right_boundary < len(corrected) - 1:
        if not is_road_grade_acceptable(
            corrected,
            right_boundary,
            right_boundary + 1,
            max_allowed_grade,
        ):
            raise ValueError(
                "Right transition exceeds allowed road grade"
            )

    return corrected



def road_zone_has_safe_boundaries(
    references,
    start,
    end,
    point_count,
    tolerance_m,
):
    """Check whether both zone boundaries have safe references."""

    if type(point_count) is not int or point_count < 3:
        raise ValueError("Invalid point count")

    if (
        type(start) is not int
        or type(end) is not int
        or not (0 < start <= end < point_count - 1)
    ):
        raise ValueError("Invalid reconstruction zone")

    safe_indices = get_safe_verified_indices(
        references,
        tolerance_m=tolerance_m,
        point_count=point_count,
    )

    left_boundary = start - 1
    right_boundary = end + 1

    return (
        left_boundary in safe_indices
        and right_boundary in safe_indices
    )




def find_conflicting_references(references, tolerance_m):
    """Find point indices with conflicting verified elevations."""

    if not math.isfinite(tolerance_m) or tolerance_m < 0:
        raise ValueError(
            "Tolerance must be finite and non-negative"
        )

    elevations_by_index = {}

    for reference in references:
        if not reference.verified:
            continue

        if not math.isfinite(reference.elevation_m):
            raise ValueError(
                "Verified reference elevation must be finite"
            )

        elevations_by_index.setdefault(
            reference.point_index, []
        ).append(reference.elevation_m)

    conflicts = set()

    for point_index, elevations in elevations_by_index.items():
        if len(elevations) < 2:
            continue

        if max(elevations) - min(elevations) > tolerance_m:
            conflicts.add(point_index)

    return conflicts



def reference_matches_profile(
    profile,
    reference,
    tolerance_m,
):
    """Check whether reference elevation matches the profile."""

    if not math.isfinite(tolerance_m):
        raise ValueError("Tolerance must be finite")

    if tolerance_m < 0:
        raise ValueError("Tolerance must be non-negative")

    if not 0 <= reference.point_index < len(profile):
        raise ValueError("Reference index is out of range")

    profile_elevation = profile[reference.point_index][1]
    reference_elevation = reference.elevation_m

    if not math.isfinite(profile_elevation):
        raise ValueError("Profile elevation must be finite")

    if not math.isfinite(reference_elevation):
        raise ValueError("Reference elevation must be finite")

    difference = abs(
        profile_elevation - reference_elevation
    )

    return difference <= tolerance_m


def detect_elevation_spikes(profile, threshold_m=10.0):
    """Detect candidate isolated spikes and short elevated blocks."""
    if len(profile) < 3:
        return []

    # Promene visine između susednih tačaka.
    changes = [
        profile[i + 1][1] - profile[i][1]
        for i in range(len(profile) - 1)
    ]

    # Tražimo veliki skok i suprotan povratak.
    candidates = []

    for start in range(len(changes)):
        first_change = changes[start]

        if abs(first_change) <= threshold_m:
            continue

        first_distance = (
            profile[start + 1][0] - profile[start][0]
        )

        if first_distance <= 0:
            raise ValueError("Distances must be strictly increasing")

        first_grade = abs(first_change) / first_distance

        # Nagib do 15% ne smatramo anomalijom.
        if first_grade <= 0.15:
            continue

        for end in range(start + 1, min(start + 3, len(changes))):
            last_change = changes[end]

            last_distance = (
                profile[end + 1][0] - profile[end][0]
            )

            if last_distance <= 0:
                raise ValueError("Distances must be strictly increasing")

            last_grade = abs(last_change) / last_distance

            if (
                first_change * last_change < 0
                and abs(last_change) > threshold_m
                and last_grade > 0.15
            ):
                candidates.extend(range(start + 1, end + 1))
                break
    
    return sorted(set(candidates))


def group_consecutive_spikes(spikes):
    """Group consecutive spike indices into inclusive intervals."""
    if not spikes:
        return []

    indices = sorted(set(spikes))

    groups = []
    start = indices[0]
    end = indices[0]

    for index in indices[1:]:
        if index == end + 1:
            end = index
        else:
            groups.append((start, end))
            start = index
            end = index

    groups.append((start, end))

    return groups



def expand_spike_interval(start, end, point_count):
    """Expand an inclusive interval by one neighboring point."""
    if point_count <= 0:
        raise ValueError("Point count must be positive")

    if not (0 <= start <= end < point_count):
        raise ValueError("Invalid spike interval")

    expanded_start = max(0, start - 1)
    expanded_end = min(point_count - 1, end + 1)

    return expanded_start, expanded_end



def merge_spike_zones(zones):
    """Merge overlapping or adjacent inclusive intervals."""
    if not zones:
        return []

    sorted_zones = sorted(zones)

    merged = [sorted_zones[0]]

    for start, end in sorted_zones[1:]:
        previous_start, previous_end = merged[-1]

        if start <= previous_end + 1:
            merged[-1] = (
                previous_start,
                max(previous_end, end),
            )
        else:
            merged.append((start, end))

    return merged



def interpolate_road_elevation_zone(profile, start, end):
    """Interpolate elevations inside a zone using its boundary points."""
    if not (0 < start <= end < len(profile) - 1):
        raise ValueError("Zone must have two boundary points")

    left_distance, left_elevation = profile[start - 1]
    right_distance, right_elevation = profile[end + 1]

    if right_distance <= left_distance:
        raise ValueError("Boundary distances must be increasing")

    corrected = list(profile)

    for i in range(start, end + 1):
        distance, _ = profile[i]

        t = (
            (distance - left_distance)
            / (right_distance - left_distance)
        )

        elevation = (
            left_elevation
            + t * (right_elevation - left_elevation)
        )

        corrected[i] = (distance, elevation)

    return corrected



def calculate_road_grade(point_a, point_b):
    """Calculate signed road grade between two profile points."""
    distance_a, elevation_a = point_a
    distance_b, elevation_b = point_b

    horizontal_distance = distance_b - distance_a

    if horizontal_distance <= 0:
        raise ValueError(
            "Road distance must be strictly increasing"
        )

    elevation_change = elevation_b - elevation_a

    return elevation_change / horizontal_distance


def calculate_road_grade_change(profile, index):
    """Return absolute grade change at an interior point."""

    if not 0 < index < len(profile) - 1:
        raise ValueError(
            "Index must refer to an interior point"
        )

    grade_before = calculate_road_grade(
        profile[index - 1],
        profile[index],
    )

    grade_after = calculate_road_grade(
        profile[index],
        profile[index + 1],
    )

    return abs(grade_after - grade_before)


def calculate_vertical_curvature(profile, index):
    """Estimate signed vertical curvature at an interior point."""

    if not 0 < index < len(profile) - 1:
        raise ValueError(
            "Index must refer to an interior point"
        )

    point_before = profile[index - 1]
    point_current = profile[index]
    point_after = profile[index + 1]

    grade_before = calculate_road_grade(
        point_before,
        point_current,
    )

    grade_after = calculate_road_grade(
        point_current,
        point_after,
    )

    length_before = point_current[0] - point_before[0]
    length_after = point_after[0] - point_current[0]

    average_length = (length_before + length_after) / 2.0

    return (grade_after - grade_before) / average_length


def find_max_vertical_curvature(curvature_profile):
    """Return the point with the largest absolute curvature."""

    if not curvature_profile:
        raise ValueError("Curvature profile must not be empty")

    return max(
        curvature_profile,
        key=lambda point: abs(point[1]),
    )

def generate_uniform_distances(total_distance, step_m):
    """Generate uniform distances, including the route endpoint."""

    if not math.isfinite(total_distance) or total_distance < 0:
        raise ValueError("Total distance must be finite and nonnegative")

    if not math.isfinite(step_m) or step_m <= 0:
        raise ValueError("Step must be finite and positive")

    count = int(total_distance // step_m)

    distances = [
        i * step_m
        for i in range(count + 1)
    ]

    if distances[-1] < total_distance:
        distances.append(total_distance)

    return distances


def resample_elevation_profile(profile, step_m):
    """Resample elevation profile at uniform distances."""

    if not profile:
        raise ValueError("Elevation profile must not be empty")

    distances = generate_uniform_distances(
        total_distance=profile[-1][0],
        step_m=step_m,
    )

    return [
        (
            distance,
            interpolate_elevation(profile, distance),
        )
        for distance in distances
    ]


def find_steep_road_segments(profile, max_grade):
    """Return indices of segments exceeding the grade limit."""

    if not math.isfinite(max_grade) or max_grade < 0:
        raise ValueError(
            "Maximum grade must be finite and nonnegative"
        )

    steep_segments = []

    for i in range(len(profile) - 1):
        grade = calculate_road_grade(
            profile[i],
            profile[i + 1],
        )

        if abs(grade) > max_grade:
            steep_segments.append(i)

    return steep_segments


def group_consecutive_segments(indices):
    """Group consecutive segment indices into inclusive ranges."""

    if not indices:
        return []

    sorted_indices = sorted(set(indices))

    groups = []
    start = sorted_indices[0]
    end = start

    for index in sorted_indices[1:]:
        if index == end + 1:
            end = index
        else:
            groups.append((start, end))
            start = index
            end = index

    groups.append((start, end))

    return groups


def calculate_vertical_curvature_profile(profile):
    """Calculate vertical curvature at all interior profile points."""

    result = []

    for index in range(1, len(profile) - 1):
        curvature = calculate_vertical_curvature(
            profile,
            index,
        )

        distance = profile[index][0]

        result.append((distance, curvature))

    return result


def max_road_grade_in_zone(profile, start, end):
    """Return maximum absolute grade within a profile zone."""
    if not (0 <= start < end < len(profile)):
        raise ValueError("Invalid road profile zone")

    max_grade = 0.0

    for i in range(start, end):
        grade = calculate_road_grade(
            profile[i],
            profile[i + 1],
        )

        max_grade = max(max_grade, abs(grade))

    return max_grade



def is_road_grade_acceptable(
    profile,
    start,
    end,
    max_allowed_grade,
):
    """Check whether all segment grades are within the limit."""
    if not 0 <= max_allowed_grade:
        raise ValueError(
            "Maximum allowed grade must be non-negative"
        )

    max_grade = max_road_grade_in_zone(
        profile,
        start,
        end,
    )

    return max_grade <= max_allowed_grade





def reconstruct_road_zone(
    profile,
    start,
    end,
    max_allowed_grade,
    suspect_indices=None,
    verified_indices=None,
):
    """Reconstruct a road zone using validated boundaries."""

    if not (0 < start <= end < len(profile) - 1):
        raise ValueError("Zone must have two boundary points")

    left_boundary = start - 1
    right_boundary = end + 1

    # Odbijamo već označene sumnjive granice.
    if suspect_indices is not None:
        if (
            left_boundary in suspect_indices
            or right_boundary in suspect_indices
        ):
            raise ValueError(
                "Reconstruction boundary is marked as suspect"
            )

    # Ako su zadate potvrđene reference,
    # obe granične tačke moraju biti potvrđene.
    if verified_indices is not None:
        if (
            left_boundary not in verified_indices
            or right_boundary not in verified_indices
        ):
            raise ValueError(
                "Reconstruction boundaries are not verified"
            )

    corrected = interpolate_road_elevation_zone(
        profile,
        start,
        end,
    )

    if not is_road_grade_acceptable(
        corrected,
        left_boundary,
        right_boundary,
        max_allowed_grade,
    ):
        raise ValueError(
            "Reconstructed road grade exceeds allowed limit"
        )

    return corrected


def find_constant_elevation_runs(
    profile,
    min_length_m,
):
    runs = []
    start = 0

    for i in range(1, len(profile) + 1):
        if (
            i == len(profile)
            or profile[i][1] != profile[start][1]
        ):
            if i - start >= 2:
                length = (
                    profile[i - 1][0]
                    - profile[start][0]
                )

                if length >= min_length_m:
                    runs.append((start, i - 1))

            start = i

    return runs



def get_constant_elevation_run_indices(runs):
    indices = set()

    for start, end in runs:
        indices.update(range(start, end + 1))

    return indices

def is_point_in_constant_elevation_run(
    point_index,
    plateau_indices,
):
    return point_index in plateau_indices


def get_non_plateau_indices(
    point_count,
    plateau_indices,
):
    return set(range(point_count)) - plateau_indices


def is_gpx_segment_length_acceptable(
    segment_length_m,
    min_length_m,
    max_length_m,
):
    return (
        min_length_m
        <= segment_length_m
        <= max_length_m
    )


def elevation_difference(gpx_elevation, dem_elevation):
    return gpx_elevation - dem_elevation

def is_elevation_difference_acceptable(difference, tolerance):
    return abs(difference) <= tolerance


def elevation_difference_change(previous_difference, current_difference):
    return current_difference - previous_difference


def elevation_difference_change_rate(difference_change, segment_length):
    if segment_length <= 0:
        raise ValueError("Segment length must be positive")

    return difference_change / segment_length


def elevation_grade_disagreement_percent(difference_change, segment_length):
    return 100.0 * elevation_difference_change_rate(
        difference_change,
        segment_length,
    )


def is_grade_disagreement_significant(disagreement, threshold):
    return abs(disagreement) > threshold


def reconstruct_road_profile(profile):
    for i in range(1, len(profile)):
        previous_distance = profile[i - 1][0]
        current_distance = profile[i][0]

        if current_distance <= previous_distance:
            raise ValueError(
                "Profile distances must be strictly increasing"
            )

    return list(profile)


def is_road_grade_suspicious(
    distance,
    elevation_change,
    max_grade_percent,
):
    if distance <= 0:
        raise ValueError("Distance must be positive")

    grade_percent = 100.0 * elevation_change / distance

    return abs(grade_percent) > max_grade_percent



def find_suspicious_grade_segments(profile, max_grade_percent):
    suspicious_segments = []

    for i in range(len(profile) - 1):
        distance = profile[i + 1][0] - profile[i][0]
        elevation_change = profile[i + 1][1] - profile[i][1]

        if distance == 0:
            continue

        if is_road_grade_suspicious(
            distance,
            elevation_change,
            max_grade_percent,
        ):
            suspicious_segments.append(i)

    return suspicious_segments

    for i in range(len(profile) - 1):
        distance = profile[i + 1][0] - profile[i][0]
        elevation_change = profile[i + 1][1] - profile[i][1]

        if is_road_grade_suspicious(
            distance,
            elevation_change,
            max_grade_percent,
        ):
            suspicious_segments.append(i)

    return suspicious_segments


def correct_isolated_elevation_spike(profile, index):
    if index <= 0 or index >= len(profile) - 1:
        raise ValueError(
            "Correction requires two neighboring points"
        )
    result = list(profile)

    distance_before, elevation_before = profile[index - 1]
    distance_after, elevation_after = profile[index + 1]
    distance_current = profile[index][0]
    
    if distance_after <= distance_before:
        raise ValueError(
            "Neighbor distances must be strictly increasing"
        )
    if not (
        distance_before < distance_current < distance_after
    ):
        raise ValueError(
            "Current point must lie between its neighbors"
        )
    fraction = (
        (distance_current - distance_before)
        / (distance_after - distance_before)
    )

    corrected_elevation = (
        elevation_before
        + fraction * (elevation_after - elevation_before)
    )

    result[index] = (
        distance_current,
        corrected_elevation,
    )

    return result



def is_isolated_elevation_spike(
    grade_before,
    grade_after,
    threshold,
):
    opposite_directions = (
        grade_before * grade_after < 0
    )

    both_steep = (
        abs(grade_before) > threshold
        and abs(grade_after) > threshold
    )

    return opposite_directions and both_steep



def is_profile_elevation_spike(profile, index, threshold):
    if index <= 0 or index >= len(profile) - 1:
        raise ValueError(
            "Spike detection requires two neighboring points"
        )

    distance_before, elevation_before = profile[index - 1]
    distance_current, elevation_current = profile[index]
    distance_after, elevation_after = profile[index + 1]

    if not (
        distance_before < distance_current < distance_after
    ):
        raise ValueError(
            "Profile distances must be strictly increasing"
        )

    grade_before = 100.0 * (
        elevation_current - elevation_before
    ) / (distance_current - distance_before)

    grade_after = 100.0 * (
        elevation_after - elevation_current
    ) / (distance_after - distance_current)

    return is_isolated_elevation_spike(
        grade_before,
        grade_after,
        threshold,
    )


def interpolate_profile_elevation(profile, distance):
    for i in range(len(profile) - 1):
        d0, z0 = profile[i]
        d1, z1 = profile[i + 1]

        if d0 <= distance <= d1:
            if d1 == d0:
                return z0

            fraction = (distance - d0) / (d1 - d0)

            return z0 + fraction * (z1 - z0)

    raise ValueError("Distance is outside profile range")


def sample_elevation_profile(profile, step):
    if step <= 0:
        raise ValueError("Step must be positive")

    start_distance = profile[0][0]
    end_distance = profile[-1][0]

    result = []
    distance = start_distance

    while distance <= end_distance:
        elevation = interpolate_profile_elevation(
            profile,
            distance,
        )
        result.append((distance, elevation))
        distance = start_distance + len(result) * step
    if result[-1][0] < end_distance:
        result.append(profile[-1])
    return result


def calculate_profile_grades(profile):
    grades = []

    for i in range(len(profile) - 1):
        start_distance, start_elevation = profile[i]
        end_distance, end_elevation = profile[i + 1]

        distance = end_distance - start_distance

        if distance <= 0:
            raise ValueError(
                "Profile distances must be strictly increasing"
            )

        elevation_change = end_elevation - start_elevation
        grade = 100.0 * elevation_change / distance

        grades.append(
            (start_distance, end_distance, grade)
        )

    return grades


def should_correct_road_elevation(
    grade_disagreement,
    confirmed_error,
):
    return confirmed_error is True



def apply_road_elevation_correction(
    profile,
    index,
    corrected_elevation,
    confirmed_error,
    max_grade_percent=None,
):
    if not 0 <= index < len(profile):
        raise IndexError("Road profile index out of range")

    result = list(profile)

    if not should_correct_road_elevation(
        grade_disagreement=0.0,
        confirmed_error=confirmed_error,
    ):
        return result

    distance, _ = result[index]
    result[index] = (distance, corrected_elevation)

    if max_grade_percent is not None:
        start = max(0, index - 1)
        end = min(len(result), index + 2)

        local_profile = result[start:end]

        if not is_road_profile_grade_acceptable(
            local_profile,
            max_grade_percent,
        ):
            raise ValueError(
                "Correction exceeds maximum road grade"
            )

    return result


def is_road_profile_grade_acceptable(
    profile,
    max_grade_percent,
):
    grades = calculate_profile_grades(profile)

    return all(
        abs(grade) <= max_grade_percent
        for _, _, grade in grades
    )


def create_road_elevation_anchor(
    distance,
    elevation,
    source,
    confirmed=False,
):
    return {
        "distance": distance,
        "elevation": elevation,
        "source": source,
        "confirmed": confirmed,
    }


def apply_road_elevation_anchor(
    profile,
    index,
    anchor,
    max_grade_percent=None,
):
    if not 0 <= index < len(profile):
        raise IndexError("Road profile index out of range")

    profile_distance = profile[index][0]
    anchor_distance = anchor["distance"]

    if abs(profile_distance - anchor_distance) > 1e-6:
        raise ValueError(
            "Anchor distance does not match profile distance"
        )

    return apply_road_elevation_correction(
        profile,
        index=index,
        corrected_elevation=anchor["elevation"],
        confirmed_error=anchor["confirmed"],
        max_grade_percent=max_grade_percent,
    )