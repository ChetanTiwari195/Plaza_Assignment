def test_happy_path_book_and_end(client):
    u = client.post("/users", json={"name": "U", "phone": "1"}).json()
    d = client.post("/drivers", json={"name": "D", "phone": "2", "car_type": "HATCHBACK", "lat": 12.9716, "lng": 77.5946}).json()
    
    resp = client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.9716, "lng": 77.5946}, "car_type": "HATCHBACK"})
    assert resp.status_code == 201
    ride = resp.json()
    assert ride["status"] == "ONGOING"
    assert ride["driver"]["id"] == d["id"]
    
    assert client.get(f"/drivers/{d['id']}").json()["status"] == "ON_RIDE"
    
    end_lat = 12.9716 - (10.0 / 111.195)
    end_lng = 77.5946
    
    resp = client.post(f"/rides/{ride['id']}/end", json={"end_location": {"lat": end_lat, "lng": end_lng}})
    assert resp.status_code == 200
    ended = resp.json()
    assert ended["status"] == "COMPLETED"
    assert ended["fare"]["total_paise"] == 6900
    
    driver_after = client.get(f"/drivers/{d['id']}").json()
    assert driver_after["status"] == "AVAILABLE"
    assert driver_after["lat"] == end_lat

def test_no_driver_in_radius(client):
    u = client.post("/users", json={"name": "U2", "phone": "3"}).json()
    client.post("/drivers", json={"name": "D2", "phone": "4", "car_type": "HATCHBACK", "lat": 12.0, "lng": 77.0})
    
    resp = client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.9, "lng": 77.5}, "car_type": "HATCHBACK"})
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "NO_DRIVER_AVAILABLE"

def test_busy_driver_not_matched(client):
    u = client.post("/users", json={"name": "U3", "phone": "5"}).json()
    d = client.post("/drivers", json={"name": "D3", "phone": "6", "car_type": "HATCHBACK", "lat": 12.9, "lng": 77.5}).json()
    
    client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.9, "lng": 77.5}, "car_type": "HATCHBACK"})
    
    u2 = client.post("/users", json={"name": "U4", "phone": "7"}).json()
    resp = client.post("/rides", json={"user_id": u2["id"], "pickup": {"lat": 12.9, "lng": 77.5}, "car_type": "HATCHBACK"})
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "NO_DRIVER_AVAILABLE"

def test_nearest_driver_chosen(client):
    u = client.post("/users", json={"name": "U", "phone": "8"}).json()
    d1 = client.post("/drivers", json={"name": "D", "phone": "9", "car_type": "HATCHBACK", "lat": 12.9 + (4/111.195), "lng": 77.5}).json()
    d2 = client.post("/drivers", json={"name": "D", "phone": "10", "car_type": "HATCHBACK", "lat": 12.9 + (1/111.195), "lng": 77.5}).json()
    
    resp = client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.9, "lng": 77.5}, "car_type": "HATCHBACK"})
    assert resp.json()["driver"]["id"] == d2["id"]

def test_upgrade(client):
    u = client.post("/users", json={"name": "U", "phone": "11"}).json()
    client.post("/drivers", json={"name": "D", "phone": "12", "car_type": "SEDAN", "lat": 12.9, "lng": 77.5})
    
    resp = client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.9, "lng": 77.5}, "car_type": "HATCHBACK"})
    ride = resp.json()
    assert ride["assigned_car_type"] == "SEDAN"
    assert ride["requested_car_type"] == "HATCHBACK"
    
    end_lat = 12.9 - (10.0 / 111.195)
    resp = client.post(f"/rides/{ride['id']}/end", json={"end_location": {"lat": end_lat, "lng": 77.5}})
    assert resp.json()["fare"]["total_paise"] == 6900

def test_no_downgrade(client):
    u = client.post("/users", json={"name": "U", "phone": "13"}).json()
    client.post("/drivers", json={"name": "D", "phone": "14", "car_type": "HATCHBACK", "lat": 12.9, "lng": 77.5})
    
    resp = client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.9, "lng": 77.5}, "car_type": "SEDAN"})
    assert resp.status_code == 409
    
def test_user_active_ride(client):
    u = client.post("/users", json={"name": "U", "phone": "15"}).json()
    client.post("/drivers", json={"name": "D", "phone": "16", "car_type": "HATCHBACK", "lat": 12.9, "lng": 77.5})
    
    client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.9, "lng": 77.5}, "car_type": "HATCHBACK"})
    resp = client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.9, "lng": 77.5}, "car_type": "HATCHBACK"})
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "USER_HAS_ACTIVE_RIDE"

def test_invalid_coupon(client):
    u = client.post("/users", json={"name": "U", "phone": "17"}).json()
    resp = client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.9, "lng": 77.5}, "car_type": "HATCHBACK", "coupon_code": "INVALID"})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "INVALID_COUPON"
