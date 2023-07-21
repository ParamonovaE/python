from django.contrib.gis.geos import Polygon, GEOSGeometry
import requests
import pytest
import json

API_URL = "http://127.0.0.1:8000/api/buildings/"

def test_list_buildings():
    res = requests.get(API_URL + '')
    assert res.status_code == 200
    data = res.json()
    return data

def test_correct_very_big_area_filter():
    res = requests.get(API_URL + '?min=0&max=1000000000000000')
    assert res.status_code == 200
    data = res.json()
    data == test_list_buildings()
    return data

def test_correct_incorrect_args_area_filter():
    res = requests.get(API_URL + '?min=asd&max=asd000000')
    assert res.status_code == 400
    res = requests.get(API_URL + '?min=123&max=asd000000')
    assert res.status_code == 400
    res = requests.get(API_URL + '?min=asd&max=1000000')
    assert res.status_code == 400
    return 0

def test_empty_args_area_filter():
    res = requests.get(API_URL + '?min=&max=')
    assert res.status_code == 200
    res = requests.get(API_URL + '?min=&max=1000000')
    assert res.status_code == 200
    res = requests.get(API_URL + '?min=0&max=')
    assert res.status_code == 200
    return 0

def test_empty_incorrect_args_names_area_filter():
    res = requests.get(API_URL + '?mi&ma=')
    assert res.status_code == 200
    res = requests.get(API_URL + '?mi&max=1000000')
    assert res.status_code == 200
    res = requests.get(API_URL + '?m=0&max=')
    assert res.status_code == 200
    return 0

def test_zero_max_area_filter():
    res = requests.get(API_URL + '?max=0')
    assert res.status_code == 200
    data = res.json()
    assert len(data["features"]) == 0
    return 0

@pytest.fixture
def post_new_polygon():
    x = 0
    y = 1
    d = {"geom": {"type": '', "coordinates": ''}}
    # area is 1/2 square degree or ~ 6160500000 square meters
    p = Polygon(((x, x), (y, y), (x, y), (x, x)), srid=4326)
    d["geom"]["type"] = p.geom_type
    d["geom"]["coordinates"] = p.coords
    res = requests.post(API_URL + '', json=d)
    assert res.status_code == 201
    newBuildingData = res.json()
    return newBuildingData

#Checking that value which should be in filtered get is in filtered get
def test_area_filter_value_in(post_new_polygon):

    id = post_new_polygon["id"]

    res = requests.get(API_URL + '?min=6000000000&max=7000000000')
    filteredData = res.json()
    assert res.status_code == 200
    assert post_new_polygon in filteredData["features"]

    res = requests.get(API_URL + '?min=600000000000&max=70000000000000')
    filteredData = res.json()
    assert res.status_code == 200
    assert post_new_polygon not in filteredData["features"]

    res = requests.delete(API_URL + str(id))
    assert res.status_code == 204