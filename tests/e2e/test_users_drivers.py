def test_register_user(client):
    resp = client.post("/users", json={"name": "Alice", "phone": "123"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Alice"
    assert data["phone"] == "123"
    assert "id" in data
    
    # fetch -> same data
    resp2 = client.get(f"/users/{data['id']}")
    assert resp2.status_code == 200
    assert resp2.json() == data

def test_duplicate_user_phone(client):
    client.post("/users", json={"name": "Bob", "phone": "456"})
    resp = client.post("/users", json={"name": "Charlie", "phone": "456"})
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "DUPLICATE_PHONE"

def test_register_driver(client):
    resp = client.post("/drivers", json={"name": "Dave", "phone": "789", "car_type": "HATCHBACK", "lat": 12.0, "lng": 77.0})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Dave"
    assert data["phone"] == "789"
    assert data["car_type"] == "HATCHBACK"
    assert data["rating"] == 5.0
    assert data["status"] == "AVAILABLE"

def test_invalid_driver(client):
    # invalid car type
    resp = client.post("/drivers", json={"name": "Eve", "phone": "111", "car_type": "SUV", "lat": 12.0, "lng": 77.0})
    assert resp.status_code == 422
    
    # invalid lat
    resp = client.post("/drivers", json={"name": "Eve", "phone": "111", "car_type": "HATCHBACK", "lat": 91.0, "lng": 77.0})
    assert resp.status_code == 422
    
    # invalid rating
    resp = client.post("/drivers", json={"name": "Eve", "phone": "111", "car_type": "HATCHBACK", "lat": 12.0, "lng": 77.0, "rating": 6.0})
    assert resp.status_code == 422

def test_update_location(client):
    resp = client.post("/drivers", json={"name": "Frank", "phone": "222", "car_type": "SEDAN", "lat": 10.0, "lng": 10.0})
    driver_id = resp.json()["id"]
    
    resp2 = client.put(f"/drivers/{driver_id}/location", json={"lat": 12.0, "lng": 15.0})
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["lat"] == 12.0
    assert data["lng"] == 15.0
    
    # fetch shows new coords
    resp3 = client.get(f"/drivers/{driver_id}")
    assert resp3.json()["lat"] == 12.0

def test_driver_not_found(client):
    assert client.get("/drivers/999").status_code == 404
    assert client.put("/drivers/999/location", json={"lat": 0, "lng": 0}).status_code == 404

def test_user_not_found(client):
    assert client.get("/users/999").status_code == 404
