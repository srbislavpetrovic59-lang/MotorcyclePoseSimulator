import pytest

from stelvio_terrain.unreal_coordinates import (
    geographic_to_unreal, route_to_unreal, load_route_coordinates,
) 


def test_route_origin_maps_to_unreal_zero():
    origin_lon = 10.55
    origin_lat = 46.60

    x, y = geographic_to_unreal(
        lon=origin_lon,
        lat=origin_lat,
        origin_lon=origin_lon,
        origin_lat=origin_lat,
    )

    assert x == pytest.approx(0.0)
    assert y == pytest.approx(0.0)


def test_eastward_movement_increases_unreal_x():
    origin_lon = 10.55
    origin_lat = 46.60

    x, y = geographic_to_unreal(
        lon=10.551,
        lat=origin_lat,
        origin_lon=origin_lon,
        origin_lat=origin_lat,
    )

    assert x > 0.0


def test_northward_movement_increases_unreal_y():
    origin_lon = 10.55
    origin_lat = 46.60

    x, y = geographic_to_unreal(
        lon=origin_lon,
        lat=46.601,
        origin_lon=origin_lon,
        origin_lat=origin_lat,
    )

    assert y > 0.0
    '''Ovo su osnovne provere smerova. UTM projekcija ima malu rotaciju koordinatne mreže u odnosu
    na geografski sever, što ćemo imati u vidu pri postavljanju mape.Sva tri testa prolaze. Naša transformacija geografskih koordinata u Unreal Engine centimetre radi,
    a smerovi X i Y su ispravni.'''


def test_load_stelvio_route_coordinates():
   
    coordinates = load_route_coordinates(
        "stelvio_terrain/data/stelvio_east_route.geojson"
    )

    assert len(coordinates) > 3000

    lon, lat = coordinates[0]

    assert 10.0 < lon < 11.0
    assert 46.0 < lat < 47.0
    '''Ovaj test proverava da možemo da učitamo našu postojeću trasu
    sa približno 3.282 koordinate i da su koordinate u očekivanom geografskom području.'''


def test_convert_route_to_unreal_coordinates():

    route = [
        (10.5500, 46.6000),
        (10.5510, 46.6000),
        (10.5510, 46.6010),
    ]

    result = route_to_unreal(route)

    assert len(result) == 3

    # Prva tačka postaje koordinatni početak.
    assert result[0] == pytest.approx((0.0, 0.0))

    # Pomeranje na istok.
    assert result[1][0] > 0.0

    # Pomeranje na sever.
    assert result[2][1] > result[1][1]
    '''Želimo da funkcija route_to_unreal() automatski koristi prvu tačku trase kao koordinatni početak
    i vrati sve tačke u centimetrima'''

    #Sada ćemo napisati prvi test za izvoz koordinata u CSV datoteku.



def test_export_unreal_route_csv(tmp_path):
    import csv

    from stelvio_terrain.unreal_coordinates import (
        export_unreal_route_csv,
    )

    points = [
        (0.0, 0.0),
        (125.5, 84.2),
    ]

    output = tmp_path / "route.csv"

    export_unreal_route_csv(points, output)

    with open(output, newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    assert rows[0] == ["X", "Y"]
    assert len(rows) == 3
    assert float(rows[1][0]) == 0.0
    assert float(rows[1][1]) == 0.0
    assert float(rows[2][0]) == 125.5
    assert float(rows[2][1]) == 84.2
    
