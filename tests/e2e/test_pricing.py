def test_estimate_hatchback(client):
    resp = client.get("/pricing/estimate?car_type=HATCHBACK&distance_km=10")
    assert resp.status_code == 200
    assert resp.json()["total_paise"] == 6900

def test_estimate_sedan(client):
    resp = client.get("/pricing/estimate?car_type=SEDAN&distance_km=3")
    assert resp.status_code == 200
    assert resp.json()["total_paise"] == 6000

def test_invalid_car_type(client):
    resp = client.get("/pricing/estimate?car_type=SUV&distance_km=10")
    assert resp.status_code == 422

def test_negative_distance(client):
    resp = client.get("/pricing/estimate?car_type=HATCHBACK&distance_km=-1")
    assert resp.status_code == 422
