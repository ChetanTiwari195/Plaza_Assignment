def test_cancellation(client):
    u = client.post("/users", json={"name": "U", "phone": "c1"}).json()
    d = client.post("/drivers", json={"name": "D", "phone": "c2", "car_type": "HATCHBACK", "lat": 12.0, "lng": 77.0}).json()
    
    r = client.post("/rides", json={"user_id": u["id"], "pickup": {"lat": 12.0, "lng": 77.0}, "car_type": "HATCHBACK"}).json()
    assert r["status"] == "ONGOING"
    
    cancel_resp = client.post(f"/rides/{r['id']}/cancel").json()
    assert cancel_resp["status"] == "CANCELLED"
    
    # 5% of minimum fare for hatchback (5000 paise). 5% of 5000 = 250.
    assert cancel_resp["cancellation_fee_paise"] == 250
    
    # Check driver is available again at pickup location
    d_after = client.get(f"/drivers/{d['id']}").json()
    assert d_after["status"] == "AVAILABLE"
    assert d_after["lat"] == 12.0
    
def test_cancellation_with_surge(client):
    client.put("/admin/config", json={"surge_mode": "DEMAND_SUPPLY"})
    u1 = client.post("/users", json={"name": "U1", "phone": "c3"}).json()
    u2 = client.post("/users", json={"name": "U2", "phone": "c4"}).json()
    
    client.post("/drivers", json={"name": "D1", "phone": "c5", "car_type": "SEDAN", "lat": 12.0, "lng": 77.0})
    
    # ride 1 uses the 1 driver
    client.post("/rides", json={"user_id": u1["id"], "pickup": {"lat": 12.0, "lng": 77.0}, "car_type": "SEDAN"})
    
    client.post("/drivers", json={"name": "D2", "phone": "c6", "car_type": "SEDAN", "lat": 12.0, "lng": 77.0})
    # ride 2 surges 1.25
    r2 = client.post("/rides", json={"user_id": u2["id"], "pickup": {"lat": 12.0, "lng": 77.0}, "car_type": "SEDAN"}).json()
    
    cancel_resp = client.post(f"/rides/{r2['id']}/cancel").json()
    
    # Sedan minimum fare is 6000. Surge is 1.25 -> 7500. 5% of 7500 = 375.
    assert cancel_resp["cancellation_fee_paise"] == 375
