"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

try:
    from .db import (
        ActivityNotFoundError,
        DuplicateEnrollmentError,
        EnrollmentNotFoundError,
        add_enrollment,
        get_activities as load_activities,
        initialize_database,
        remove_enrollment,
    )
except ImportError:  # pragma: no cover - supports running `python app.py`
    from db import (
        ActivityNotFoundError,
        DuplicateEnrollmentError,
        EnrollmentNotFoundError,
        add_enrollment,
        get_activities as load_activities,
        initialize_database,
        remove_enrollment,
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities",
    lifespan=lifespan,
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_all_activities():
    return load_activities()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    try:
        add_enrollment(activity_name, email)
    except ActivityNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Activity not found") from exc
    except DuplicateEnrollmentError as exc:
        raise HTTPException(status_code=400, detail="Student is already signed up") from exc

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    try:
        remove_enrollment(activity_name, email)
    except ActivityNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Activity not found") from exc
    except EnrollmentNotFoundError as exc:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity",
        ) from exc

    return {"message": f"Unregistered {email} from {activity_name}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
