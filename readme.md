# Ride Hailing Backend

A fast, lightweight backend for a ride-hailing app built with Python and FastAPI.

## How to run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   uvicorn app.main:create_app --factory
   ```
3. Run the tests:
   ```bash
   pytest
   ```

**Example Curl Flow**:
```bash
# Register User
curl -X POST http://localhost:8000/users -H "Content-Type: application/json" -d '{"name": "Alice", "phone": "123"}'

# Register Driver
curl -X POST http://localhost:8000/drivers -H "Content-Type: application/json" -d '{"name": "Bob", "phone": "456", "car_type": "HATCHBACK", "lat": 12.0, "lng": 77.0}'

# Book Ride
curl -X POST http://localhost:8000/rides -H "Content-Type: application/json" -d '{"user_id": 1, "pickup": {"lat": 12.0, "lng": 77.0}, "car_type": "HATCHBACK"}'

# End Ride
curl -X POST http://localhost:8000/rides/1/end -H "Content-Type: application/json" -d '{"end_location": {"lat": 12.0, "lng": 77.1}}'
```

## Assumptions

- **Money & Units**: All money is in integer paise. Distance is in kilometers (haversine) rounded to 2 decimals.
- **Car Types**: HATCHBACK and SEDAN, with free upgrade from HATCHBACK to SEDAN if necessary. Fares are calculated using the requested car type's rates.
- **Pricing**: Slabs are marginal. Calculation is: `slab_total -> max(slab_total, minimum_fare) -> * surge_multiplier -> - coupon_discount -> max(0, result)`.
- **Coupons**: Validated at booking and snapshotted to the ride. If a coupon exceeds the fare, the result is floored at 0. No per-user limits.
- **Matching**: Haversine distance, 5km search radius default. Nearest driver first, tie-break by lower driver ID.
- **Booking**: Atomic claim via SQLite `UPDATE ... WHERE status = 'AVAILABLE'`.

## Key Design Decisions & Trade-offs

- **Layering rules**: API -> Services -> (Repositories, Domain). Domain contains pure python rules. Services orchestrate and handle transactions.
- **No ORM**: Hand-written standard library SQLite for simplicity and tight control, abiding by the ponytail rules of efficiency.
- **Integer Paise**: Avoiding floating-point precision issues with currency.
- **Extensibility Registries**: To add a new car type, tier, or coupon type, you only need to modify one central dictionary in the pure domain (e.g., `RATE_CARDS`, `COUPON_TYPES`).
- **Atomic Driver Claiming**: Handled securely at the database level by ensuring the UPDATE rowcount is 1.

## With More Time

- Road-distance / accumulated GPS distance instead of point-to-point haversine.
- Geospatial index (PostGIS or similar) instead of Python distance filtering.
- Per-user coupon usage limits.
- Payment processing integrations.
- Driver ratings flow and assignment priority based on ratings.
- Authentication and authorization.
- Database migrations tooling.
- Pagination for list endpoints (history).
- Idempotency keys for booking and ending rides.

## AI Usage

This project was built primarily by an AI coding assistant following the "Ponytail" minimalist philosophy. A detailed log of what was prompted and how it was implemented or challenged can be found in `docs/AI_LOG.md`.
