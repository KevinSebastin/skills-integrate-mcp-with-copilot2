## Title
Harden API with rate limiting, audit logs, and policy checks

## Summary
Improve operational safety and traceability for production-like use.

## Problem
- No abuse protection or activity audit trail.
- Minimal observability for who changed enrollment/attendance data.

## Scope
- Add rate limiting on mutation endpoints.
- Add structured audit log entries for signup/unregister/admin actions.
- Add stricter policy checks (email domain, payload limits, input normalization).

## Acceptance Criteria
- Repeated abusive mutation requests are throttled.
- All mutating operations write audit events with actor + action + timestamp.
- Error responses remain user-friendly and consistent.

## Suggested Files
- `src/app.py`
- `src/logging/*` (new)
- `src/security/*` (new)

## Priority
P2

## Labels
enhancement, security, operations, backend, priority:P2
