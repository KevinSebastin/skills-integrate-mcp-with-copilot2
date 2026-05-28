"""
High School Management System API

A simple FastAPI application that allows members to browse and manage their
own extracurricular activity participation while reserving sensitive
administration workflows for admins.
"""

from copy import deepcopy
import os
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from auth import (
        authenticate_user,
        create_token_for_user,
        get_user_for_token,
        revoke_token,
    )
except ImportError:  # pragma: no cover - supports package imports in tests
    from src.auth import (
        authenticate_user,
        create_token_for_user,
        get_user_for_token,
        revoke_token,
    )


app = FastAPI(
    title="Mergington High School API",
    description="API for secure extracurricular activity management",
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(Path(__file__).parent, "static")),
    name="static",
)

security = HTTPBearer(auto_error=False)

INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "attendance": {},
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "attendance": {},
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "attendance": {},
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        "attendance": {},
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        "attendance": {},
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        "attendance": {},
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        "attendance": {},
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        "attendance": {},
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
        "attendance": {},
    },
}

activities = deepcopy(INITIAL_ACTIVITIES)


class LoginRequest(BaseModel):
    email: str
    password: str


class ActivityPayload(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    schedule: str = Field(min_length=1)
    max_participants: int = Field(gt=0)


class ActivityUpdatePayload(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = Field(default=None, min_length=1)
    schedule: str | None = Field(default=None, min_length=1)
    max_participants: int | None = Field(default=None, gt=0)


class AttendancePayload(BaseModel):
    email: str
    status: Literal["present", "absent"]


def reset_activities() -> None:
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user = get_user_for_token(credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return user


def require_admin(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


def get_activity_or_404(activity_name: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    return activities[activity_name]


def serialize_activity(activity_name: str, current_user: dict):
    activity = activities[activity_name]
    payload = {
        "description": activity["description"],
        "schedule": activity["schedule"],
        "max_participants": activity["max_participants"],
        "spots_left": activity["max_participants"] - len(activity["participants"]),
    }

    if current_user["role"] == "admin":
        payload["participants"] = list(activity["participants"])
        payload["attendance"] = dict(activity.get("attendance", {}))
    else:
        payload["is_registered"] = current_user["email"] in activity["participants"]
        payload["attendance_status"] = activity.get("attendance", {}).get(
            current_user["email"]
        )

    return payload


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.post("/auth/login")
def login(credentials: LoginRequest):
    user = authenticate_user(credentials.email, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_token_for_user(user)
    return {"token": token, "user": user}


@app.post("/auth/logout")
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    _current_user=Depends(get_current_user),
):
    if credentials is not None:
        revoke_token(credentials.credentials)

    return {"message": "Logged out successfully"}


@app.get("/auth/me")
def get_authenticated_user(current_user=Depends(get_current_user)):
    return current_user


@app.get("/activities")
def get_activities(current_user=Depends(get_current_user)):
    return {
        activity_name: serialize_activity(activity_name, current_user)
        for activity_name in activities
    }


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, current_user=Depends(get_current_user)):
    """Sign up the authenticated user for an activity."""
    activity = get_activity_or_404(activity_name)
    email = current_user["email"]

    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    activity["participants"].append(email)
    activity.setdefault("attendance", {}).pop(email, None)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str, current_user=Depends(get_current_user)
):
    """Unregister the authenticated user from an activity."""
    activity = get_activity_or_404(activity_name)
    email = current_user["email"]

    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity",
        )

    activity["participants"].remove(email)
    activity.setdefault("attendance", {}).pop(email, None)
    return {"message": f"Unregistered {email} from {activity_name}"}


@app.post("/activities")
def create_activity(
    activity: ActivityPayload,
    _current_user=Depends(require_admin),
):
    if activity.name in activities:
        raise HTTPException(status_code=400, detail="Activity already exists")

    activities[activity.name] = {
        "description": activity.description,
        "schedule": activity.schedule,
        "max_participants": activity.max_participants,
        "participants": [],
        "attendance": {},
    }
    return {"message": f"Created activity {activity.name}"}


@app.put("/activities/{activity_name}")
def update_activity(
    activity_name: str,
    update: ActivityUpdatePayload,
    _current_user=Depends(require_admin),
):
    activity = get_activity_or_404(activity_name)

    new_name = update.name or activity_name
    if new_name != activity_name and new_name in activities:
        raise HTTPException(status_code=400, detail="Activity already exists")

    if (
        update.max_participants is not None
        and update.max_participants < len(activity["participants"])
    ):
        raise HTTPException(
            status_code=400,
            detail="Max participants cannot be less than current participants",
        )

    updated_activity = {
        "description": update.description or activity["description"],
        "schedule": update.schedule or activity["schedule"],
        "max_participants": update.max_participants or activity["max_participants"],
        "participants": list(activity["participants"]),
        "attendance": dict(activity.get("attendance", {})),
    }

    if new_name != activity_name:
        activities.pop(activity_name)

    activities[new_name] = updated_activity
    return {"message": f"Updated activity {new_name}"}


@app.delete("/activities/{activity_name}")
def delete_activity(
    activity_name: str,
    _current_user=Depends(require_admin),
):
    get_activity_or_404(activity_name)
    activities.pop(activity_name)
    return {"message": f"Deleted activity {activity_name}"}


@app.put("/activities/{activity_name}/attendance")
def mark_attendance(
    activity_name: str,
    attendance: AttendancePayload,
    _current_user=Depends(require_admin),
):
    activity = get_activity_or_404(activity_name)

    if attendance.email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student must be registered before attendance can be recorded",
        )

    activity.setdefault("attendance", {})[attendance.email] = attendance.status
    return {
        "message": (
            f"Marked {attendance.email} as {attendance.status} for {activity_name}"
        )
    }
