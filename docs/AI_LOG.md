# AI Log

## PR 1: Foundation
- **Prompted:** Create the initial project skeleton, config, DB schema, and test setup.
- **Rejected/Rewritten:** Did not use an ORM or background jobs, keeping dependencies thin as specified. Relied on pure stdlib SQLite instead of SQLAlchemy.
- **Why:** To follow the strict architectural constraints of using no ORM and keeping the codebase minimal, enforcing ponytail rules.
