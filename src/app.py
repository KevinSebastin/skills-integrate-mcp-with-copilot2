"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import Body, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
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
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


def get_activity_or_404(activity_name: str):
    """Return an activity or raise a 404 error."""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    return activities[activity_name]


def validate_text_field(value, field_name: str):
    """Validate and normalize a required text field."""
    if not isinstance(value, str) or not value.strip():
        raise HTTPException(status_code=400, detail=f"{field_name} is required")

    return value.strip()


def validate_activity_payload(payload: dict):
    """Validate admin activity payloads."""
    title = validate_text_field(payload.get("title"), "Title")
    description = validate_text_field(payload.get("description"), "Description")
    schedule = validate_text_field(payload.get("schedule"), "Schedule")
    capacity = payload.get("capacity")

    if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Capacity must be a positive integer"
        )

    return title, {
        "description": description,
        "schedule": schedule,
        "max_participants": capacity
    }


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/admin/activities")
def create_activity(payload: dict = Body(...)):
    """Create a new activity."""
    title, activity_data = validate_activity_payload(payload)

    if title in activities:
        raise HTTPException(status_code=400, detail="Activity already exists")

    activities[title] = {
        **activity_data,
        "participants": []
    }
    return {"message": f"Created activity {title}"}


@app.put("/admin/activities/{activity_name}")
def update_activity(activity_name: str, payload: dict = Body(...)):
    """Update an existing activity."""
    existing_activity = get_activity_or_404(activity_name)
    title, activity_data = validate_activity_payload(payload)

    if title != activity_name and title in activities:
        raise HTTPException(status_code=400, detail="Activity already exists")

    if activity_data["max_participants"] < len(existing_activity["participants"]):
        raise HTTPException(
            status_code=400,
            detail="Capacity cannot be lower than current participant count"
        )

    updated_activity = {
        **activity_data,
        "participants": existing_activity["participants"]
    }

    if title != activity_name:
        del activities[activity_name]

    activities[title] = updated_activity
    return {"message": f"Updated activity {title}"}


@app.delete("/admin/activities/{activity_name}")
def delete_activity(activity_name: str):
    """Delete an activity."""
    get_activity_or_404(activity_name)
    del activities[activity_name]
    return {"message": f"Deleted activity {activity_name}"}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    activity = get_activity_or_404(activity_name)

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
    activity = get_activity_or_404(activity_name)

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
