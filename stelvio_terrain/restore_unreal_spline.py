"""Restore Stelvio RoadSpline from the original CSV."""

import csv
import unreal

CSV_PATH = (
    r"C:\Vezbe\MotorcyclePoseSim"
    r"\stelvio_terrain\data\stelvio_route_unreal.csv"
)

actor_subsystem = unreal.get_editor_subsystem(
    unreal.EditorActorSubsystem
)

actors = actor_subsystem.get_all_level_actors()

roads = [
    actor for actor in actors
    if actor.get_class().get_name() == "BP_StelvioRoad_C"
]

print("Pronadjeno StelvioRoad aktera:", len(roads))

if len(roads) != 1:
    raise RuntimeError(
        f"Ocekivan 1 BP_StelvioRoad, pronadjeno: {len(roads)}"
    )

road = roads[0]

splines = road.get_components_by_class(
    unreal.SplineComponent
)

if len(splines) != 1:
    raise RuntimeError(
        f"Ocekivan 1 RoadSpline, pronadjeno: {len(splines)}"
    )

spline = splines[0]

print("Spline:", spline.get_name())
print("Broj tacaka:", spline.get_number_of_spline_points())

def restore_spline():
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        csv_points = list(csv.DictReader(f))

    if len(csv_points) != 3282:
        raise RuntimeError(
            f"Neocekivan broj CSV tacaka: {len(csv_points)}"
        )

    spline.clear_spline_points(False)

    for p in csv_points:
        spline.add_spline_point(
            unreal.Vector(
                float(p["X"]),
                float(p["Y"]),
                0.0
            ),
            unreal.SplineCoordinateSpace.LOCAL,
            False
        )

    for i in range(spline.get_number_of_spline_points()):
        spline.set_spline_point_type(
            i,
            unreal.SplinePointType.LINEAR,
            False
        )

    spline.update_spline()

    print("Obnovljeno tacaka:", spline.get_number_of_spline_points())
    print("Duzina (km):", spline.get_spline_length() / 100000)


print("Funkcija restore_spline je spremna.")