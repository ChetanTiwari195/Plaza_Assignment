# AI Log

## PR 1: Foundation
- **Prompted:** Create the initial project skeleton, config, DB schema, and test setup.
- **Why:** To follow the strict architectural constraints of using no ORM and keeping the codebase minimal, enforcing ponytail rules.

## PR 2: Users, drivers, location
- **Prompted:** Add users and drivers registration and location update endpoints.
- **Rejected/Rewritten:** Used pure stdlib SQLite in the repository layer instead of abstraction layers or ORM features. Exceptions mapped cleanly at the API layer.
- **Why:** Kept the database operations explicitly in the repository and simple, aligning with minimal design requirements.
