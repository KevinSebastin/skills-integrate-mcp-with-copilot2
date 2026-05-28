import copy
import unittest

from fastapi import HTTPException

import app as app_module


class AttendanceApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.initial_activities = copy.deepcopy(app_module.activities)

    def setUp(self):
        app_module.activities.clear()
        app_module.activities.update(copy.deepcopy(self.initial_activities))

    def test_mark_attendance_for_completed_activity(self):
        payload = app_module.mark_attendance(
            "Chess Club", "michael@mergington.edu", "present"
        )
        self.assertEqual(payload["attendance"]["status"], "present")
        self.assertEqual(
            app_module.activities["Chess Club"]["attendance"]["michael@mergington.edu"],
            "present",
        )

    def test_mark_attendance_for_future_activity_is_rejected(self):
        with self.assertRaises(HTTPException) as context:
            app_module.mark_attendance("Soccer Team", "liam@mergington.edu", "absent")

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail,
            "Attendance can only be marked for completed activities",
        )

    def test_attendance_history_empty_state(self):
        payload = app_module.get_student_attendance("not-enrolled@mergington.edu")
        self.assertEqual(payload["attendance_history"], [])
        self.assertEqual(
            payload["message"], "No attendance history found for this student"
        )

    def test_attendance_history_for_completed_activity(self):
        app_module.mark_attendance("Chess Club", "michael@mergington.edu", "present")
        payload = app_module.get_student_attendance("michael@mergington.edu")

        self.assertEqual(len(payload["attendance_history"]), 1)
        self.assertEqual(payload["attendance_history"][0]["activity"], "Chess Club")
        self.assertEqual(payload["attendance_history"][0]["status"], "present")


if __name__ == "__main__":
    unittest.main()
