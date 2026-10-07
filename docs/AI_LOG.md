# AI Log

## PR 1: Foundation
- **Prompted:** Create the initial project skeleton, config, DB schema, and test setup.
- **Why:** To follow the strict architectural constraints of using no ORM and keeping the codebase minimal, enforcing ponytail rules.

## PR 2: Users, drivers, location
- **Prompted:** Add users and drivers registration and location update endpoints.
- **Rejected/Rewritten:** Used pure stdlib SQLite in the repository layer instead of abstraction layers or ORM features. Exceptions mapped cleanly at the API layer.
- **Why:** Kept the database operations explicitly in the repository and simple, aligning with minimal design requirements.

## PR 3: Pricing engine + car types
- **Prompted:** Add pure pricing engine domain logic for computing ride fares.
- **Why:** YAGNI. A simple registry perfectly serves the requirement to define car types in one place with minimal overhead.

## PR 4: Coupons
- **Prompted:** Add coupon models, registry, API endpoints, and validation logic.
- **Why:** To make adding new coupon types just a single new class, keeping things decoupled but not over-engineered.

## PR 5: Book ride, free upgrade, end ride
- **Prompted:** Add the core ride booking and ending logic, including atomic claim.
- **Rejected/Rewritten:** Sorted drivers in pure Python instead of a geospatial SQL index. 
- **Why:** Kept it lazy and simple per ponytail: haversine distance filtering in Python is extremely easy to read, uses no extensions, and perfectly fits the current constraints. SQLite's standard capabilities are completely sufficient for atomic row claiming via `UPDATE ... WHERE status = 'AVAILABLE'`.

## PR 6: Ride history
- **Prompted:** Add ride history queries for users and drivers with optional status filtering.
- **Rejected/Rewritten:** Avoided creating dedicated new endpoints under `/rides` for querying by user or driver ID. Instead attached them to the `/users/{id}/rides` and `/drivers/{id}/rides` endpoints.
- **Why:** RESTful resource hierarchies keep the API surface intuitive. Using simple SQLite `ORDER BY id DESC` keeps pagination absent per requirements while maintaining chronological correctness.

## PR 8: Surge pricing (Bonus)
- **Prompted:** Add surge pricing and admin configuration for surge mode.
- **Why:** YAGNI again. Fetching all available drivers / ongoing rides and doing Python haversine is O(N) where N is small, completely sufficient for this MVP, matching ponytail minimalism.

## PR 9: Matching Strategy (Bonus)
- **Prompted:** Add configuration for matching strategy (nearest vs highest rated).
- **Rejected/Rewritten:** Did not use a complex Strategy design pattern or dynamic imports. Just added an `if matching_strategy` block changing the `lambda` sort key of the candidates array.
- **Why:** Keeping the dispatch logic in one readable linear function makes it much easier to reason about tie-breaking rules compared to scattered objects.
