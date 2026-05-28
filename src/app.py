"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from datetime import date
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "event_date": "2025-01-10",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "attendance": {}
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "event_date": "2025-02-20",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "attendance": {}
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "event_date": "2025-03-15",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "attendance": {}
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "event_date": "2030-04-12",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        "attendance": {}
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "event_date": "2030-05-18",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        "attendance": {}
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "event_date": "2030-06-14",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        "attendance": {}
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "event_date": "2025-04-09",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        "attendance": {}
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "event_date": "2030-07-22",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        "attendance": {}
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "event_date": "2025-05-30",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
        "attendance": {}
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    activity["attendance"].pop(email, None)
    return {"message": f"Unregistered {email} from {activity_name}"}


@app.post("/activities/{activity_name}/attendance")
def mark_attendance(activity_name: str, email: str, status: str):
    """Mark attendance for an enrolled student in a completed activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    event_date = date.fromisoformat(activity["event_date"])
    if event_date > date.today():
        raise HTTPException(
            status_code=400,
            detail="Attendance can only be marked for completed activities"
        )

    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not enrolled in this activity"
        )

    normalized_status = status.lower()
    if normalized_status not in {"present", "absent"}:
        raise HTTPException(
            status_code=400,
            detail="Attendance status must be either present or absent"
        )

    activity["attendance"][email] = normalized_status
    return {
        "message": f"Marked {email} as {normalized_status} for {activity_name}",
        "attendance": {
            "activity": activity_name,
            "email": email,
            "status": normalized_status,
            "event_date": activity["event_date"]
        }
    }


@app.get("/students/{email}/attendance")
def get_student_attendance(email: str):
    """Get attendance history for completed activities for a given student email"""
    attendance_history = []

    for activity_name, activity in activities.items():
        event_date = date.fromisoformat(activity["event_date"])
        if event_date > date.today() or email not in activity["participants"]:
            continue

        attendance_history.append(
            {
                "activity": activity_name,
                "event_date": activity["event_date"],
                "status": activity["attendance"].get(email, "not_marked")
            }
        )

    if not attendance_history:
        return {
            "attendance_history": [],
            "message": "No attendance history found for this student"
        }

    return {"attendance_history": attendance_history}
