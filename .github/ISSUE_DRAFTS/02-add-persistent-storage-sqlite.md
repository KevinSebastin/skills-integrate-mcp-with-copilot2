## Title
Replace in-memory activity store with SQLite persistence

## Summary
Move activities and enrollments from in-memory dicts to a SQLite-backed data model so data survives restarts.

## Problem
- Data currently resets whenever the server restarts.
- No durable history or stable IDs for records.

## Scope
- Introduce DB models for activities and enrollments.
- Add lightweight migration strategy (Alembic or SQLModel metadata init).
- Refactor `/activities`, signup, and unregister endpoints to DB reads/writes.
- Seed initial activities from script or startup task.

## Acceptance Criteria
- Restarting the app preserves activities and enrollments.
- GET/POST/DELETE endpoints remain functionally compatible.
- Data model supports future attendance and role-based features.
- Setup docs include DB initialization steps.

## Suggested Files
- `src/app.py`
- `requirements.txt`
- `src/README.md`
- `src/db/*` (new)

## Priority
P0

## Labels
enhancement, backend, database, priority:P0
