## Title
Add attendance tracking workflow (present/absent) for completed activities

## Summary
Extend beyond enrollment to actual attendance outcomes, with admin marking and member visibility.

## Problem
- System currently tracks signup only, not event attendance outcomes.

## Scope
- Add attendance data model linked to activity and student.
- Admin endpoint/UI to mark `present`/`absent` after event date.
- Member view to see attendance history per past activity.

## Acceptance Criteria
- Admin can mark attendance for each enrolled member on completed events.
- Attendance cannot be marked for future events.
- Member can view attendance status history.
- API and UI return clear empty states.

## Suggested Files
- `src/app.py`
- `src/static/index.html`
- `src/static/app.js`
- `src/static/styles.css`

## Priority
P1

## Labels
enhancement, backend, frontend, attendance, priority:P1
