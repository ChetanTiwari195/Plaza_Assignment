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
- **Rejected/Rewritten:** Implemented a simple Protocol for coupons and a registry instead of complex inheritance. Stored codes upper-case.
- **Why:** To make adding new coupon types just a single new class, keeping things decoupled but not over-engineered.
