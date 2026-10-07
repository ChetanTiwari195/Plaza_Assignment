from app.domain.geo import haversine_km

def test_haversine_same_point():
    assert haversine_km(12.9716, 77.5946, 12.9716, 77.5946) == 0.0

def test_haversine_bengaluru():
    d = haversine_km(12.9716, 77.5946, 12.9784, 77.6408)
    assert 4.0 <= d <= 6.0

def test_haversine_equator_degree():
    d = haversine_km(0.0, 0.0, 0.0, 1.0)
    assert 110.5 <= d <= 111.5
