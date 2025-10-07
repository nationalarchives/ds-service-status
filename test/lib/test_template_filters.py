import unittest

from app.lib.template_filters import previous_incidents


class TemplateFiltersTestCase(unittest.TestCase):
    def test_previous_incidents_none(self):
        heartbeats = [
            {"status": 1, "time": "2003-02-01T00:00:00"},
            {"status": 1, "time": "2003-02-01T00:01:00"},
            {"status": 1, "time": "2003-02-01T00:02:00"},
            {"status": 1, "time": "2003-02-01T00:03:00"},
            {"status": 1, "time": "2003-02-01T00:04:00"},
            {"status": 1, "time": "2003-02-01T00:05:00"},
            {"status": 1, "time": "2003-02-01T00:06:00"},
            {"status": 1, "time": "2003-02-01T00:07:00"},
            {"status": 1, "time": "2003-02-01T00:08:00"},
            {"status": 1, "time": "2003-02-01T00:09:00"},
        ]
        result = previous_incidents(heartbeats)
        self.assertEqual(result, [])

    def test_previous_incidents_all(self):
        heartbeats = [
            {"status": 0, "time": "2003-02-01T00:00:00"},
            {"status": 0, "time": "2003-02-01T00:01:00"},
            {"status": 0, "time": "2003-02-01T00:02:00"},
            {"status": 0, "time": "2003-02-01T00:03:00"},
            {"status": 0, "time": "2003-02-01T00:04:00"},
            {"status": 0, "time": "2003-02-01T00:05:00"},
            {"status": 0, "time": "2003-02-01T00:06:00"},
            {"status": 0, "time": "2003-02-01T00:07:00"},
            {"status": 0, "time": "2003-02-01T00:08:00"},
            {"status": 0, "time": "2003-02-01T00:09:00"},
        ]
        result = previous_incidents(heartbeats)
        self.assertEqual(len(result), 1)
        self.assertIsNotNone(result[0].get("start"))
        self.assertIsNone(result[0].get("end"))
        self.assertTrue(result[0].get("has_start"))
        self.assertFalse(result[0].get("has_end"))
        self.assertIsNotNone(result[0].get("duration_seconds"))

    def test_previous_incidents_ongoing(self):
        heartbeats = [
            {"status": 1, "time": "2003-02-01T00:00:00"},  # UP
            {"status": 1, "time": "2003-02-01T00:01:00"},
            {"status": 1, "time": "2003-02-01T00:02:00"},
            {"status": 1, "time": "2003-02-01T00:03:00"},
            {"status": 1, "time": "2003-02-01T00:04:00"},
            {"status": 1, "time": "2003-02-01T00:05:00"},
            {"status": 3, "time": "2003-02-01T00:06:00"},  # PENDING
            {"status": 0, "time": "2003-02-01T00:07:00"},  # DOWN
            {"status": 0, "time": "2003-02-01T00:08:00"},
            {"status": 0, "time": "2003-02-01T00:09:00"},
        ]
        result = previous_incidents(heartbeats)
        self.assertEqual(len(result), 1)
        self.assertIsNotNone(result[0].get("start"))
        self.assertIsNone(result[0].get("end"))
        self.assertTrue(result[0].get("has_start"))
        self.assertFalse(result[0].get("has_end"))
        self.assertIsNotNone(result[0].get("duration_seconds"))

    def test_previous_incidents_multiple(self):
        heartbeats = [
            {"status": 1, "time": "2003-02-01T00:00:00"},  # UP
            {"status": 3, "time": "2003-02-01T00:01:00"},  # PENDING
            {"status": 0, "time": "2003-02-01T00:02:00"},  # DOWN
            {"status": 1, "time": "2003-02-01T00:03:00"},  # UP
            {"status": 1, "time": "2003-02-01T00:04:00"},
            {"status": 3, "time": "2003-02-01T00:05:00"},  # PENDING, Not down yet
            {"status": 1, "time": "2003-02-01T00:06:00"},
            {"status": 0, "time": "2003-02-01T00:07:00"},  # DOWN
            {"status": 0, "time": "2003-02-01T00:08:00"},
            {"status": 1, "time": "2003-02-01T00:09:00"},  # UP
        ]
        result = previous_incidents(heartbeats)
        self.assertEqual(len(result), 3)
        for incident in result:
            self.assertIsNotNone(incident.get("start"))
            self.assertIsNotNone(incident.get("end"))
            self.assertTrue(incident.get("has_start"))
            self.assertTrue(incident.get("has_end"))
            self.assertIsNotNone(incident.get("duration_seconds"))

    def test_previous_incidents_hanging_on_start(self):
        heartbeats = [
            {"status": 0, "time": "2003-02-01T00:00:00"},  # DOWN
            {"status": 1, "time": "2003-02-01T00:01:00"},  # UP
            {"status": 1, "time": "2003-02-01T00:02:00"},
            {"status": 1, "time": "2003-02-01T00:03:00"},
            {"status": 1, "time": "2003-02-01T00:04:00"},
            {"status": 3, "time": "2003-02-01T00:05:00"},  # PENDING, Not down yet
            {"status": 0, "time": "2003-02-01T00:06:00"},  # DOWN
            {"status": 1, "time": "2003-02-01T00:07:00"},  # UP
            {"status": 1, "time": "2003-02-01T00:08:00"},
            {"status": 1, "time": "2003-02-01T00:09:00"},
        ]
        result = previous_incidents(heartbeats)
        self.assertEqual(len(result), 2)

        for incident in result:
            self.assertIsNotNone(incident.get("start"))
            self.assertIsNotNone(incident.get("end"))
            self.assertTrue(incident.get("has_start"))
            self.assertTrue(incident.get("has_end"))
            self.assertIsNotNone(incident.get("duration_seconds"))
