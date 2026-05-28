## Title
Implement authentication and role-based access (admin/member)

## Summary
Introduce secure identity and authorization so only admins can manage sensitive workflows.

## Problem
- Current API is open and unauthenticated.
- No distinction between student and admin actions.

## Scope
- Add login/auth mechanism (session or token-based).
- Add role model (`admin`, `member`) and route protection.
- Restrict admin operations (activity CRUD, attendance management).
- Keep member operations limited to view/signup/unregister own actions.

## Acceptance Criteria
- Unauthenticated users cannot access protected admin routes.
- Admin-only endpoints enforce role checks.
- Member users can perform only allowed actions.
- Frontend reflects auth state and role-specific UI.

## Suggested Files
- `src/app.py`
- `src/static/index.html`
- `src/static/app.js`
- `src/auth/*` (new)

## Priority
P1

## Labels
enhancement, security, backend, frontend, auth, priority:P1
