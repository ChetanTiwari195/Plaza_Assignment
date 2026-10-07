def test_create_get_delete_coupon(client):
    # create
    resp = client.post("/coupons", json={"code": "save20", "type": "PERCENT", "value": 20})
    assert resp.status_code == 201
    
    # get (case insensitive lookup)
    resp = client.get("/coupons/SAVE20")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SAVE20"
    
    # duplicate
    resp = client.post("/coupons", json={"code": "SAVE20", "type": "FLAT", "value": 100})
    assert resp.status_code == 409
    
    # delete
    assert client.delete("/coupons/SAVE20").status_code == 204
    assert client.get("/coupons/SAVE20").status_code == 404
    
    # delete unknown
    assert client.delete("/coupons/UNKNOWN").status_code == 404

def test_invalid_coupon_values(client):
    assert client.post("/coupons", json={"code": "c1", "type": "PERCENT", "value": 0}).status_code == 422
    assert client.post("/coupons", json={"code": "c2", "type": "PERCENT", "value": 101}).status_code == 422
    assert client.post("/coupons", json={"code": "c3", "type": "FLAT", "value": 0}).status_code == 422
    
    # flat coupon cannot have max discount
    assert client.post("/coupons", json={"code": "c4", "type": "FLAT", "value": 100, "max_discount_paise": 50}).status_code == 422
