## 0. How to work

1. One branch + one PR per section below, merged to `main` **in order** (merge commits, not squash, so history shows evolution).
2. Make **at least 2-3 meaningful commits per PR** (e.g. `feat: ...`, `test: ...`, `refactor: ...`).
3. Every PR must leave `pytest` fully green. Do not start the next PR with failing tests.
4. Every PR ends by appending 2-4 lines to `docs/AI_LOG.md`: what was prompted, what was rejected/rewritten, why. (This feeds the README's AI-usage section.)
5. No dead code, no unused abstractions, no features outside the PR's scope. If a function isn't called or tested, delete it.
6. Don't add auth, pagination, background jobs, migrations tooling, or an ORM.

## 1. Locked decisions (the spec is ambiguous; these are final)

### Money & units
- All money is **integer paise** in DB, code, and API. API fields are suffixed `_paise`. ₹1 = 100 paise.
- Distance is in **km**, rounded to 2 decimals before pricing. Haversine, Earth radius 6371 km.
- Fare math uses `Decimal`; final per-slab and total amounts round **half-up to whole paise**.

### Car types
- `HATCHBACK`, `SEDAN`. Defined in **one registry** (`domain/pricing.py`): a rate card per car type, plus an upgrade path `UPGRADE_PATH = {HATCHBACK: [SEDAN], SEDAN: []}`. Adding an SUV later must only touch this registry and the `CarType` enum.

### Pricing rules
- Slabs are **marginal**: each km is charged at the rate of the slab it falls in (like income tax). The spec's gaps (2-3 km, 5-6 km) are resolved by treating boundaries as exactly 2 km and 5 km.
- Order of operations: `slab_total → max(slab_total, minimum_fare) → × surge_multiplier → − coupon_discount → max(0, result)`.
- The coupon **may** take the fare below the minimum fare (minimum applies before the coupon). Final total is floored at 0.
- **Upgrade rule:** if the user requested HATCHBACK and the assigned car is SEDAN, the fare is computed with **HATCHBACK rates** (that is "no extra cost"). SEDAN requests are never downgraded. Fares always use `requested_car_type`.

### Coupons
- Fields: `code` (unique, case-insensitive, stored upper-case), `type` (`PERCENT` | `FLAT`), `value` (PERCENT: 1-100; FLAT: paise > 0), `max_discount_paise` (nullable, PERCENT only), `expires_at` (nullable ISO datetime).
- A coupon is **validated at booking** (exists, not expired). Invalid coupon → booking **fails** with `INVALID_COUPON` (never silently ignored).
- The coupon definition is **snapshotted onto the ride** at booking. Deleting a coupon later does not affect ongoing rides. Delete is a hard delete.
- Discount is computed when the ride ends. No per-user usage limits.
- Adding a new coupon type must be one new class in `domain/coupons.py` plus one registry entry.

### Booking & matching
- Booking request carries **pickup only**; the end location is supplied when ending the ride. Distance = haversine(pickup, end_location).
- Default search radius: **5 km** from pickup (configurable via `Settings.search_radius_km`).
- Eligible drivers: status `AVAILABLE`, within radius of pickup, car type matches. Default strategy: **nearest**, tie-break by lowest driver id.
- Upgrade: for HATCHBACK requests, search HATCHBACK first; only if none are eligible, search SEDAN. A farther hatchback beats a nearer sedan.
- Driver statuses: `AVAILABLE`, `ON_RIDE`. Ride statuses: `ONGOING`, `COMPLETED`, `CANCELLED`.
- A user may have at most one `ONGOING` ride (409 `USER_HAS_ACTIVE_RIDE`). A driver may have at most one `ONGOING` ride.
- Drivers register with an initial location and car type, so a driver always has a location. Optional `rating` (0-5, default 5.0) is set at registration.
- On end ride: ride → `COMPLETED`, driver → `AVAILABLE` and driver's location is set to the end location.
- Straight-line (haversine) distance, not road distance, and not accumulated from location updates.

### Errors
All errors return JSON `{"error": {"code": "<CODE>", "message": "<text>"}}`.

| Code | HTTP |
|---|---|
| `VALIDATION_ERROR` | 422 |
| `USER_NOT_FOUND`, `DRIVER_NOT_FOUND`, `RIDE_NOT_FOUND`, `COUPON_NOT_FOUND` | 404 |
| `NO_DRIVER_AVAILABLE` | 409 |
| `USER_HAS_ACTIVE_RIDE` | 409 |
| `RIDE_NOT_ONGOING` | 409 |
| `COUPON_ALREADY_EXISTS` | 409 |
| `INVALID_COUPON` | 422 |
| `DUPLICATE_PHONE` | 409 |

## Architecture Rules

**Layering rules:** `api → services → (repositories, domain)`. `domain` imports nothing from the other layers. Routers never touch SQL. Business rules (pricing, matching, validation of coupons) never live in routers or repositories.

**SQLite rules:**
- One connection per request (FastAPI dependency), opened with `isolation_level=None`, and `PRAGMA foreign_keys=ON; PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;`.
- Multi-statement writes run inside `with transaction(conn):` which issues `BEGIN IMMEDIATE` / `COMMIT` / `ROLLBACK`.
- Tests use a **temp-file DB per test** (`tmp_path`), never `:memory:` (separate connections would not share it).
