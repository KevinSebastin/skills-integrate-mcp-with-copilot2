# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Log in as an admin or member
- Sign up for activities as the authenticated member
- Manage activities and attendance as an admin

## Getting Started

1. Install the dependencies:

   ```
   pip install -r ../requirements.txt
   ```

2. Run the application:

   ```
   python -m uvicorn src.app:app --reload
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                | Description                                            |
| ------ | --------------------------------------- | ------------------------------------------------------ |
| POST   | `/auth/login`                           | Log in and receive a bearer token                      |
| GET    | `/auth/me`                              | View the current authenticated user                    |
| GET    | `/activities`                           | Get the authenticated user's activity view             |
| POST   | `/activities/{activity_name}/signup`    | Sign up the current user for an activity               |
| DELETE | `/activities/{activity_name}/unregister`| Unregister the current user from an activity           |
| POST   | `/activities`                           | Create an activity (admin only)                        |
| PUT    | `/activities/{activity_name}`           | Update an activity (admin only)                        |
| DELETE | `/activities/{activity_name}`           | Delete an activity (admin only)                        |
| PUT    | `/activities/{activity_name}/attendance`| Mark attendance for a participant (admin only)         |

## Demo Accounts

- `admin@mergington.edu` / `adminpass`
- `michael@mergington.edu` / `memberpass`

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
