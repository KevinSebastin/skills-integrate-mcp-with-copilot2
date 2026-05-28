## Title
Add admin activity CRUD (create, edit, archive/delete)

## Summary
Provide admin workflows to manage activities instead of hardcoded startup definitions.

## Problem
- Activities are currently static and cannot be managed through the application.

## Scope
- Add admin API endpoints: create/update/delete activities.
- Add admin UI section for activity management forms and list actions.
- Keep existing student activity browsing behavior intact.

## Acceptance Criteria
- Admin can create activities with title, description, schedule/date, capacity.
- Admin can edit and delete/archive activities.
- Student-facing list reflects changes immediately.
- Input validation and error handling are consistent.

## Suggested Files
- `src/app.py`
- `src/static/index.html`
- `src/static/app.js`
- `src/static/styles.css`

## Priority
P1

## Labels
enhancement, backend, frontend, admin, priority:P1
