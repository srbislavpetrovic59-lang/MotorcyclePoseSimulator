import csv
import json
from pyproj import Transformer


_transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32632",
    always_xy=True,
)


def geographic_to_unreal(
    lon,
    lat,
    origin_lon,
    origin_lat,
):
    x, y = _transformer.transform(lon, lat)

    origin_x, origin_y = _transformer.transform(
        origin_lon,
        origin_lat,
    )

    return (
        (x - origin_x) * 100.0,
        (y - origin_y) * 100.0,
    )
'''
Šta smo uradili?
- EPSG:4326 — geografske koordinate iz OSM-a.
- EPSG:32632 — UTM projekcija, u metrima.
- Množenje sa 100 — pretvaranje metara u Unreal centimetre.
- Oduzimanje početnih koordinata — početak trase postaje (0, 0).
Za sada računamo samo X i Y. Visinu Z dodaćemo kasnije, odvojeno, kako smo se dogovorili.'''



def load_route_coordinates(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    geometry = data["geometry"]

    if geometry["type"] != "LineString":
        raise ValueError("Expected LineString geometry")

    return [
        (lon, lat)
        for lon, lat in geometry["coordinates"]
    ]
'''Ova funkcija čita koordinate iz GeoJSON datoteke, bez menjanja originala.
Za sada pretpostavljamo da je naša trasa predstavljena kao prvi Feature sa geometrijom LineString.'''



def route_to_unreal(route):
    if not route:
        return []

    origin_lon, origin_lat = route[0]

    return [
        geographic_to_unreal(
            lon=lon,
            lat=lat,
            origin_lon=origin_lon,
            origin_lat=origin_lat,
        )
        for lon, lat in route
    ]
'''Funkcija:
- Prima listu geografskih koordinata (lon, lat).
- Koristi prvu tačku kao koordinatni početak (0, 0).
- Pretvara sve koordinate u Unreal centimetre.
- Čuva redosled tačaka, što je važno za serpentine.
Za sada radimo samo sa X i Y koordinatama. Visine ćemo dodati zasebno.'''



def export_unreal_route_csv(points, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(["X", "Y"])
        writer.writerows(points)
    '''Ova funkcija:
    - Čuva redosled svih koordinata.
    - Upisuje X i Y u centimetrima.
    - Ne menja originalni GeoJSON.
    - Priprema podatke za buduću Unreal Spline putanju.
    '''
    # iz PS:python -c "from stelvio_terrain.unreal_coordinates import load_route_coordinates, route_to_unreal, export_unreal_route_csv; route=load_route_coordinates('stelvio_terrain/data/stelvio_east_route.geojson'); points=route_to_unreal(route); export_unreal_route_csv(points, 'stelvio_terrain/data/stelvio_route_unreal.csv'); print('Exported points:', len(points))"
    # kreira CSV datoteku sa koordinatama u Unreal Engine formatu, spremnu za uvoz u Unreal Spline.