# Prioritized Implementation Plan

This plan is aligned to the current FastAPI + static frontend implementation.

## Priority Order

### P0 (Immediate reliability and data integrity)
1. Enforce capacity limits and signup validation
2. Persist data in SQLite with SQLModel/SQLAlchemy + migrations

### P1 (Core product capabilities)
3. Add admin activity CRUD API + admin UI workflow
4. Add authentication and role-based access control (admin/member)
5. Add attendance tracking (present/absent) after event date

### P2 (Quality and scale-readiness)
6. Add automated tests and CI pipeline
7. Add API hardening (rate limits, audit logging, input policy checks)

## Why this order

- **P0 first** prevents overbooking and data loss on restart.
- **P1 next** unlocks practical school operations and parity with more complete systems.
- **P2 last** improves maintainability and production-readiness once core workflows are stable.
