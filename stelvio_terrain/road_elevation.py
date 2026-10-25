


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

