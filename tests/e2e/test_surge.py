def test_admin_config(client):
    assert client.get("/admin/config").json()["surge_mode"] == "OFF"
    client.put("/admin/config", json={"surge_mode": "DEMAND_SUPPLY"})
    assert client.get("/admin/config").json()["surge_mode"] == "DEMAND_SUPPLY"

def test_surge_pricing(client):
    client.put("/admin/config", json={"surge_mode": "DEMAND_SUPPLY"})
    
    u1 = client.post("/users", json={"name": "U1", "phone": "s1"}).json()
    u2 = client.post("/users", json={"name": "U2", "phone": "s2"}).json()
    u3 = client.post("/users", json={"name": "U3", "phone": "s3"}).json()
    
    # create 1 driver
    d1 = client.post("/drivers", json={"name": "D1", "phone": "s4", "car_type": "HATCHBACK", "lat": 12.0, "lng": 77.0}).json()
    
    # demand = 1 (this user), supply = 1 (d1) -> ratio 1 -> surge 1.0
    r1 = client.post("/rides", json={"user_id": u1["id"], "pickup": {"lat": 12.0, "lng": 77.0}, "car_type": "HATCHBACK"}).json()
    assert r1["surge_multiplier"] == 1.0
    
    # create another driver to serve next requests
    d2 = client.post("/drivers", json={"name": "D2", "phone": "s5", "car_type": "HATCHBACK", "lat": 12.0, "lng": 77.0}).json()
    
    # now ongoing = 1 (r1), supply = 1 (d2) -> demand = 1(r1) + 1(this user) = 2. ratio = 2/1 = 2.0 -> surge 1.25
    r2 = client.post("/rides", json={"user_id": u2["id"], "pickup": {"lat": 12.0, "lng": 77.0}, "car_type": "HATCHBACK"}).json()
    assert r2["surge_multiplier"] == 1.25
    
    d3 = client.post("/drivers", json={"name": "D3", "phone": "s6", "car_type": "HATCHBACK", "lat": 12.0, "lng": 77.0}).json()
    # ongoing = 2 (r1, r2), supply = 1 (d3) -> demand = 2 + 1 = 3. ratio = 3/1 = 3.0 -> surge 1.5
    r3 = client.post("/rides", json={"user_id": u3["id"], "pickup": {"lat": 12.0, "lng": 77.0}, "car_type": "HATCHBACK"}).json()
    assert r3["surge_multiplier"] == 1.5
    
    # test fare computation with surge
    # end r3, 10km away. 
    end_lat = 12.0 - (10.0 / 111.195)
    ended = client.post(f"/rides/{r3['id']}/end", json={"end_location": {"lat": end_lat, "lng": 77.0}}).json()
    # 6900 * 1.5 = 10350
    assert ended["fare"]["total_paise"] == 10350
