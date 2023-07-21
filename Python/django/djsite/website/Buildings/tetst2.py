from django.contrib.gis.geos import Point, Polygon, GEOSGeometry
import requests
import pytest
import json

API_URL = "http://127.0.0.1:8000/api/buildings/"
def test_list_buildings():
    res = requests.get(API_URL + '')
    assert res.status_code == 200
    data = res.json()
    return data
@pytest.fixture
def get_big_distance_and_point():
    return (100000000, Point(0, 0))

@pytest.fixture
def get_big_distance_filtered_list(get_big_distance_and_point):
    res = requests.get(API_URL + '?dist={0}&&point={1},{2}'.
                       format(get_big_distance_and_point[0],
                              get_big_distance_and_point[1].x, get_big_distance_and_point[1].y))
    assert res.status_code == 200
    data = res.json()
    return data

@pytest.fixture
def get_full_building_list():
    return test_list_buildings()

def test_distance_filter_big(get_big_distance_filtered_list, get_full_building_list):
    assert get_big_distance_filtered_list == get_full_building_list

@pytest.fixture
def get_zero_distance_and_point():
    return (0, Point(-5, -5, srid=4326))

@pytest.fixture
def get_zero_distance_filtered_list(get_zero_distance_and_point):
    res = requests.get(API_URL + '?dist={0}&&point={1},{2}'.
                       format(get_zero_distance_and_point[0],
                              get_zero_distance_and_point[1].x, get_zero_distance_and_point[1].y))
    assert res.status_code == 200
    data = res.json()
    return (data, get_zero_distance_and_point[1])

def test_distance_filter_zero(get_zero_distance_filtered_list, get_full_building_list):
    filtered = get_zero_distance_filtered_list[0]["features"]
    full = get_full_building_list["features"]
    point = get_zero_distance_filtered_list[1]
    for feature in filtered:
        geom = GEOSGeometry(json.dumps(feature['geometry']))
        assert geom.covers(point)

    cnt_test = 0
    for feature in full:
        geom = GEOSGeometry(json.dumps(feature['geometry']))
        if geom.covers(point):
            cnt_test += 1
    cnt_api = len(filtered)
    assert cnt_api == cnt_test

@pytest.mark.skip(reason="no need to check now")
def test_distance_filter(get_full_building_list):
    for i in range(10):
        dist = 10
        x = 0.0
        y = 0.0
        for j in range(10):
            res = requests.get(API_URL + '?dist={0}&&point={1},{2}'.
                           format(dist, x, y))
            assert res.status_code == 200
            data = res.json()
            x += 2
            y += 2
        dist *= 10

def test_distance_filter(get_full_building_list):
    res = requests.get(API_URL + '?dist={0}&&point={1},{2}'.
                       format(5, 5, 5))

    assert res.status_code == 200
    res = requests.get(API_URL + '?&point={0},{1}'.
                       format(5, 5))
    assert res.status_code == 200
    data = res.json()
    data == get_full_building_list

    res = requests.get(API_URL + '??dist=&point={0},{1}'.
                       format(5, 5))
    assert res.status_code == 200
    data = res.json()
    data == get_full_building_list


@pytest.fixture
def post_new_polygon():
    x = 0
    y = 1
    d = {"geom": {"type": '', "coordinates": ''}}
    p = Polygon(((x, x), (y, y), (x, y), (x, x)), srid=4326)
    d["geom"]["type"] = p.geom_type
    d["geom"]["coordinates"] = p.coords
    res = requests.post(API_URL + '', json=d)
    assert res.status_code == 201
    newBuildingData = res.json()
    return newBuildingData

def test_distance_filtel_value(post_new_polygon):

    id = post_new_polygon["id"]
    res = requests.get(API_URL + '?dist=100000&point=0,2.0')
    filteredData = res.json()
    assert res.status_code == 200
    assert post_new_polygon not in filteredData["features"]

    res = requests.get(API_URL + '?dist=200000&point=0,2.0')
    filteredData = res.json()
    assert res.status_code == 200
    assert post_new_polygon in filteredData["features"]

    res = requests.delete(API_URL + str(id))
    assert res.status_code == 204
    return
