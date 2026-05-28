## Title
Enforce activity capacity limits and strengthen signup validation

## Summary
Prevent over-enrollment and improve signup data quality in the `POST /activities/{activity_name}/signup` flow.

## Problem
- `max_participants` is displayed but not enforced.
- Signup currently accepts any email format/domain and has no policy checks.

## Scope
- Backend: enforce `participants.length < max_participants` before append.
- Backend: validate school email domain (e.g., `@mergington.edu`) and normalize emails to lowercase.
- Backend: return clear HTTP errors for full activity and invalid email policy.
- Frontend: display user-friendly error messages for these cases.

## Acceptance Criteria
- Signup returns `409` (or `400`) when an activity is full.
- Signup rejects invalid/non-school email with clear error detail.
- Existing duplicate-signup guard continues to work.
- UI shows actionable feedback for all failure states.

## Suggested Files
- `src/app.py`
- `src/static/app.js`

## Priority
P0

## Labels
enhancement, backend, frontend, validation, priority:P0
