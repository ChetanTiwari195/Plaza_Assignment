def test_ride_history_empty(client):
    u = client.post("/users", json={"name": "U", "phone": "h1"}).json()
    resp = client.get(f"/users/{u['id']}/rides")
    assert resp.status_code == 200
    assert resp.json() == {"rides": []}

def test_ride_history(client):
    u = client.post("/users", json={"name": "U", "phone": "h2"}).json()
    d = client.post("/drivers", json={"name": "D", "phone": "h3", "car_type": "HATCHBACK", "lat": 12.0, "lng": 77.0}).json()
    
    # create ongoing
    r1 = client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.0, "lng": 77.0}, "car_type": "HATCHBACK"}).json()
    
    # History default
    h = client.get(f"/users/{u['id']}/rides").json()["rides"]
    assert len(h) == 1
    assert h[0]["status"] == "ONGOING"
    
    # History with status
    assert len(client.get(f"/users/{u['id']}/rides?status=COMPLETED").json()["rides"]) == 0
    
    # End ride
    client.post(f"/rides/{r1['id']}/end", json={"end_location": {"lat": 12.0, "lng": 77.1}})
    
    # create second ride
    r2 = client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.0, "lng": 77.1}, "car_type": "HATCHBACK"}).json()
    
    # History default (newest first)
    h = client.get(f"/users/{u['id']}/rides").json()["rides"]
    assert len(h) == 2
    assert h[0]["id"] == r2["id"]
    assert h[1]["id"] == r1["id"]
    
    # History COMPLETED
    hc = client.get(f"/users/{u['id']}/rides?status=COMPLETED").json()["rides"]
    assert len(hc) == 1
    assert hc[0]["id"] == r1["id"]
    assert "fare" in hc[0]

def test_driver_history(client):
    u = client.post("/users", json={"name": "U", "phone": "h4"}).json()
    d = client.post("/drivers", json={"name": "D", "phone": "h5", "car_type": "HATCHBACK", "lat": 12.0, "lng": 77.0}).json()
    client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.0, "lng": 77.0}, "car_type": "HATCHBACK"})
    
    h = client.get(f"/drivers/{d['id']}/rides").json()["rides"]
    assert len(h) == 1
    assert h[0]["status"] == "ONGOING"

def test_history_404_422(client):
    assert client.get("/users/999/rides").status_code == 404
    assert client.get("/drivers/999/rides").status_code == 404
    
    u = client.post("/users", json={"name": "U", "phone": "h6"}).json()
    assert client.get(f"/users/{u['id']}/rides?status=BOGUS").status_code == 422
