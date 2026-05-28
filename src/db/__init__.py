import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).with_name("activities.sqlite")


class ActivityNotFoundError(LookupError):
    pass


class DuplicateEnrollmentError(ValueError):
    pass


class EnrollmentNotFoundError(ValueError):
    pass

INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
    },
}


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                schedule TEXT NOT NULL,
                max_participants INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id INTEGER NOT NULL,
                student_email TEXT NOT NULL,
                enrolled_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE,
                UNIQUE(activity_id, student_email)
            );
            """
        )

        activity_count = connection.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
        if activity_count == 0:
            seed_database(connection)


def seed_database(connection):
    for name, activity in INITIAL_ACTIVITIES.items():
        cursor = connection.execute(
            """
            INSERT INTO activities (name, description, schedule, max_participants)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                activity["description"],
                activity["schedule"],
                activity["max_participants"],
            ),
        )

        for email in activity["participants"]:
            connection.execute(
                """
                INSERT INTO enrollments (activity_id, student_email)
                VALUES (?, ?)
                """,
                (cursor.lastrowid, email),
            )


def get_activities():
    with get_connection() as connection:
        activities = {
            row["name"]: {
                "description": row["description"],
                "schedule": row["schedule"],
                "max_participants": row["max_participants"],
                "participants": [],
            }
            for row in connection.execute(
                """
                SELECT id, name, description, schedule, max_participants
                FROM activities
                ORDER BY id
                """
            )
        }

        for row in connection.execute(
            """
            SELECT activities.name, enrollments.student_email
            FROM enrollments
            JOIN activities ON activities.id = enrollments.activity_id
            ORDER BY activities.id, enrollments.id
            """
        ):
            activities[row["name"]]["participants"].append(row["student_email"])

        return activities


def get_activity_id(connection, activity_name):
    row = connection.execute(
        "SELECT id FROM activities WHERE name = ?",
        (activity_name,),
    ).fetchone()
    if row is None:
        raise ActivityNotFoundError(activity_name)

    return row["id"]


def add_enrollment(activity_name, email):
    with get_connection() as connection:
        activity_id = get_activity_id(connection, activity_name)

        try:
            connection.execute(
                """
                INSERT INTO enrollments (activity_id, student_email)
                VALUES (?, ?)
                """,
                (activity_id, email),
            )
        except sqlite3.IntegrityError as exc:
            if "UNIQUE constraint failed: enrollments.activity_id, enrollments.student_email" in str(exc):
                raise DuplicateEnrollmentError(email) from exc
            raise


def remove_enrollment(activity_name, email):
    with get_connection() as connection:
        activity_id = get_activity_id(connection, activity_name)
        result = connection.execute(
            """
            DELETE FROM enrollments
            WHERE activity_id = ? AND student_email = ?
            """,
            (activity_id, email),
        )

        if result.rowcount == 0:
            raise EnrollmentNotFoundError(email)
