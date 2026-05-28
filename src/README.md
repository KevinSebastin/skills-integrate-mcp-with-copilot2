# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Unregister from activities
- Persist activities and enrollments in SQLite

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Start the application from the `src` directory:

   ```
   python app.py
   ```

   On first startup, the app creates `db/activities.sqlite` and seeds the
   default activities automatically.

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

4. To reset the local database and re-seed the starter data, delete:

   ```
   db/activities.sqlite
   ```

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister from an activity                                        |

## Data Model

The application uses a simple SQLite-backed data model with meaningful identifiers:

1. **Activities** - Stored with a stable integer ID and unique activity name:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of linked enrollments

2. **Enrollments** - Stored separately with a stable integer ID:
   - Linked activity ID
   - Student email
   - Enrollment timestamp

The database schema is initialized automatically on startup using SQL DDL
statements, and existing activities and enrollments persist across server
restarts.
