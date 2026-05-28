import unittest

from fastapi.testclient import TestClient

from src.app import app, reset_activities
from src.auth import reset_auth_state


class AuthRoleTests(unittest.TestCase):
    def setUp(self):
        reset_auth_state()
        reset_activities()
        self.client = TestClient(app)

    def login(self, email, password):
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": password},
        )
        self.assertEqual(response.status_code, 200)
        return {"Authorization": "Bearer " + response.json()["token"]}

    def test_unauthenticated_requests_are_blocked(self):
        response = self.client.get("/activities")
        self.assertEqual(response.status_code, 401)

        response = self.client.post(
            "/activities",
            json={
                "name": "Science Club",
                "description": "Experiments",
                "schedule": "Mondays",
                "max_participants": 10,
            },
        )
        self.assertEqual(response.status_code, 401)

    def test_member_access_is_limited_to_member_actions(self):
        headers = self.login("michael@mergington.edu", "memberpass")

        activities_response = self.client.get("/activities", headers=headers)
        self.assertEqual(activities_response.status_code, 200)
        chess = activities_response.json()["Chess Club"]
        self.assertTrue(chess["is_registered"])
        self.assertNotIn("participants", chess)

        signup_response = self.client.post(
            "/activities/Art%20Club/signup",
            headers=headers,
        )
        self.assertEqual(signup_response.status_code, 200)

        delete_response = self.client.delete(
            "/activities/Art%20Club/unregister",
            headers=headers,
        )
        self.assertEqual(delete_response.status_code, 200)

        create_response = self.client.post(
            "/activities",
            headers=headers,
            json={
                "name": "Science Club",
                "description": "Experiments",
                "schedule": "Mondays",
                "max_participants": 10,
            },
        )
        self.assertEqual(create_response.status_code, 403)

        attendance_response = self.client.put(
            "/activities/Chess%20Club/attendance",
            headers=headers,
            json={
                "email": "michael@mergington.edu",
                "status": "present",
            },
        )
        self.assertEqual(attendance_response.status_code, 403)

    def test_signup_respects_activity_capacity(self):
        admin_headers = self.login("admin@mergington.edu", "adminpass")
        michael_headers = self.login("michael@mergington.edu", "memberpass")
        sophia_headers = self.login("sophia@mergington.edu", "memberpass")

        create_response = self.client.post(
            "/activities",
            headers=admin_headers,
            json={
                "name": "Robotics Club",
                "description": "Build robots",
                "schedule": "Fridays",
                "max_participants": 1,
            },
        )
        self.assertEqual(create_response.status_code, 200)

        first_signup = self.client.post(
            "/activities/Robotics%20Club/signup",
            headers=michael_headers,
        )
        self.assertEqual(first_signup.status_code, 200)

        second_signup = self.client.post(
            "/activities/Robotics%20Club/signup",
            headers=sophia_headers,
        )
        self.assertEqual(second_signup.status_code, 400)
        self.assertEqual(second_signup.json()["detail"], "Activity is full")

    def test_admin_can_manage_admin_only_operations(self):
        headers = self.login("admin@mergington.edu", "adminpass")

        create_response = self.client.post(
            "/activities",
            headers=headers,
            json={
                "name": "Science Club",
                "description": "Experiments and competitions",
                "schedule": "Mondays, 3:30 PM",
                "max_participants": 10,
            },
        )
        self.assertEqual(create_response.status_code, 200)

        update_response = self.client.put(
            "/activities/Science%20Club",
            headers=headers,
            json={
                "description": "Updated science lab sessions",
                "max_participants": 12,
            },
        )
        self.assertEqual(update_response.status_code, 200)

        attendance_response = self.client.put(
            "/activities/Chess%20Club/attendance",
            headers=headers,
            json={
                "email": "michael@mergington.edu",
                "status": "present",
            },
        )
        self.assertEqual(attendance_response.status_code, 200)

        activities_response = self.client.get("/activities", headers=headers)
        self.assertEqual(activities_response.status_code, 200)
        chess = activities_response.json()["Chess Club"]
        self.assertIn("participants", chess)
        self.assertEqual(chess["attendance"]["michael@mergington.edu"], "present")

        delete_response = self.client.delete(
            "/activities/Science%20Club",
            headers=headers,
        )
        self.assertEqual(delete_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
