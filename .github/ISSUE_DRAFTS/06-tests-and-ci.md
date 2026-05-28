## Title
Introduce automated tests and CI pipeline

## Summary
Add baseline quality gates to prevent regressions as feature scope expands.

## Problem
- No automated tests or CI checks currently validate behavior.

## Scope
- Add backend tests for activities list, signup, unregister, validation errors.
- Add tests for capacity and auth once implemented.
- Add GitHub Actions workflow for lint + tests.

## Acceptance Criteria
- CI runs on pull requests and main branch pushes.
- Core API flows are covered by automated tests.
- Failing tests block merge (or clearly fail status checks).

## Suggested Files
- `tests/*` (new)
- `.github/workflows/ci.yml` (new)
- `requirements.txt`

## Priority
P2

## Labels
enhancement, testing, ci, devex, priority:P2
