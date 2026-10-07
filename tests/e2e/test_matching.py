def test_matching_strategy(client):
    client.put("/admin/config", json={"matching_strategy": "HIGHEST_RATED"})
    
    u = client.post("/users", json={"name": "U", "phone": "m1"}).json()
    
    # d1 is closer (1km), but rating 4.0
    d1 = client.post("/drivers", json={"name": "D1", "phone": "m2", "car_type": "HATCHBACK", "lat": 12.9 + (1/111.195), "lng": 77.5, "rating": 4.0}).json()
    
    # d2 is farther (4km), but rating 5.0
    d2 = client.post("/drivers", json={"name": "D2", "phone": "m3", "car_type": "HATCHBACK", "lat": 12.9 + (4/111.195), "lng": 77.5, "rating": 5.0}).json()
    
    # should pick d2 because of HIGHEST_RATED
    r = client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.9, "lng": 77.5}, "car_type": "HATCHBACK"}).json()
    assert r["driver"]["id"] == d2["id"]
    
    client.put("/admin/config", json={"matching_strategy": "NEAREST"})
    
    # create d3 (2km) rating 5.0, d4 (3km) rating 5.0
    d3 = client.post("/drivers", json={"name": "D3", "phone": "m4", "car_type": "HATCHBACK", "lat": 12.9 + (2/111.195), "lng": 77.5, "rating": 5.0}).json()
    d4 = client.post("/drivers", json={"name": "D4", "phone": "m5", "car_type": "HATCHBACK", "lat": 12.9 + (3/111.195), "lng": 77.5, "rating": 5.0}).json()
    
    # now strategy is nearest, d1 (1km) is the closest available driver
    u2 = client.post("/users", json={"name": "U2", "phone": "m6"}).json()
    r2 = client.post("/rides", json={"user_id": u2["id"], "pickup": {"lat": 12.9, "lng": 77.5}, "car_type": "HATCHBACK"}).json()
    assert r2["driver"]["id"] == d1["id"]
