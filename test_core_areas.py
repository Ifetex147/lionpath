import unittest
from app import app
from models import Node, Edge, Timetable, OrientationKB

class TestLionPathCoreWorkflows(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_gates_to_venues(self):
        """Category 1: Entrance Gates to Faculty Lecture Venues and Departments"""
        gate_journeys = [
            ("from UNN 1st Gate to Carver Building", "Carver Building", True), # Long distance -> Keke advice
            ("from UNN 2nd Gate to FPSLT", "Faculty of Physical Sciences Lecture Theatre (FPSLT)", True),
            ("from Odenigwe Gate to NCSB", "New Computer Science Building (NCSB)", False),
            ("from Odim Gate to Science Lecture Theatre", "Faculty of Physical Sciences Lecture Theatre (FPSLT)", True),
        ]
        for query, expected_dest, expect_keke in gate_journeys:
            res = self.client.post("/chat", json={"message": query, "session_id": "test-gate-suite"})
            data = res.get_json()
            reply = data.get("reply", "")
            self.assertEqual(data.get("destination_name"), expected_dest, f"Failed destination for: {query}")
            self.assertIn("Walking Route", reply)
            self.assertIn("Estimated Distance & Time", reply)
            if expect_keke:
                self.assertIn("Campus Transit Advice", reply, f"Expected Keke advice for: {query}")

    def test_hostels_to_departments(self):
        """Category 2: Hostels to Faculty Departments & Lecture Venues"""
        hostel_journeys = [
            ("from Bello to Science Lecture Theatre", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
            ("from Aja-Nwachukwu to Carver Building", "Carver Building"),
            ("from Akintola to GS Building", "General Studies Building (GS Building)"),
            ("from Eyo-Ita to Computer Science", "New Computer Science Building (NCSB)"),
        ]
        for query, expected_dest in hostel_journeys:
            res = self.client.post("/chat", json={"message": query, "session_id": "test-hostel-suite"})
            data = res.get_json()
            self.assertEqual(data.get("destination_name"), expected_dest, f"Failed for: {query}")

    def test_venue_to_venue(self):
        """Category 3: Lecture Venue to Lecture Venue (Class Hopper)"""
        venue_journeys = [
            ("from FPSLT to General Studies Building", "General Studies Building (GS Building)"),
            ("from Carver to Abuja Building", "Abuja Building (Prof. Ezeilo Building)"),
            ("from NCSB to FPSLT", "Faculty of Physical Sciences Lecture Theatre (FPSLT)"),
        ]
        for query, expected_dest in venue_journeys:
            res = self.client.post("/chat", json={"message": query, "session_id": "test-venue-suite"})
            data = res.get_json()
            self.assertEqual(data.get("destination_name"), expected_dest, f"Failed for: {query}")

    def test_fresher_essential_landmarks(self):
        """Category 4: Essential Fresher Landmarks (Bookshop, Medical, Student Affairs, NAL)"""
        landmarks = [
            ("from Carver to Bookshop", "University Bookshop"),
            ("from Carver to Medical Centre", "University Medical Centre"),
            ("from Carver to Student Affairs", "Student Affairs Building"),
            ("from Carver to NAL Library", "Nnamdi Azikiwe Library (NAL)"),
        ]
        for query, expected_dest in landmarks:
            res = self.client.post("/chat", json={"message": query, "session_id": "test-landmark-suite"})
            data = res.get_json()
            self.assertEqual(data.get("destination_name"), expected_dest, f"Failed for: {query}")

    def test_library_ambiguity_handling(self):
        """Category 5: Library and Canteen Disambiguation"""
        sid = "test-lib-ambig-suite"
        # User just asks "where is library"
        res1 = self.client.post("/chat", json={"message": "where is library", "session_id": sid})
        d1 = res1.get_json()
        self.assertIn("Which library do you want directions to?", d1.get("reply", ""))
        self.assertIn("Faculty Library", d1.get("options", []))
        self.assertIn("Main Library (NAL)", d1.get("options", []))

        # User chooses "faculty"
        res2 = self.client.post("/chat", json={"message": "faculty", "session_id": sid})
        d2 = res2.get_json()
        self.assertIn("Where are you starting from", d2.get("reply", ""))

        # User chooses origin "Carver"
        res3 = self.client.post("/chat", json={"message": "Carver Building", "session_id": sid})
        d3 = res3.get_json()
        self.assertEqual(d3.get("destination_name"), "Faculty of Physical Sciences Library")

    def test_course_venue_wayfinding(self):
        """Category 6: Courses to Lecture Venues (GSP 101, COS 101, PHY 115)"""
        sid = "test-course-suite"
        # 1. GSP 101
        res = self.client.post("/chat", json={"message": "where does GSP 101 hold?", "session_id": sid})
        d = res.get_json()
        self.assertIn("General Studies Building", d.get("reply", ""))
        self.assertIn("Where are you starting from", d.get("reply", ""))

        # 2. COS 101
        res2 = self.client.post("/chat", json={"message": "how do I get to COS 101 class?", "session_id": "cos-flow"})
        d2 = res2.get_json()
        self.assertIn("New Computer Science Building", d2.get("reply", ""))

        # 3. Direct route with origin
        res3 = self.client.post("/chat", json={"message": "from Carver to GSP 101", "session_id": "gsp-direct"})
        d3 = res3.get_json()
        self.assertEqual(d3.get("destination_name"), "General Studies Building (GS Building)")

    def test_orientation_core_faqs(self):
        """Category 7: Verified UNN Orientation & Academic Policies"""
        faqs = [
            ("how do I pay school fees?", "Remita"),
            ("what documents are required for clearance?", "Carver Building"),
            ("how do I apply for hostel accommodation?", "Makintouch"),
            ("how is CGPA calculated?", "UNN 5-Point"),
            ("how to register for library card?", "500"),
            ("medical registration requirements?", "Medical Centre"),
        ]
        for query, expected_keyword in faqs:
            res = self.client.post("/chat", json={"message": query, "session_id": "test-faq-suite"})
            reply = res.get_json().get("reply", "")
            self.assertIn(expected_keyword, reply, f"Failed FAQ: {query}")

    def test_timetable_dedup_and_lookups(self):
        """Category 8: Lecture Timetables by Department, Code & Day"""
        # Standalone GSP 101 must be clean and deduplicated
        res = self.client.post("/chat", json={"message": "GSP 101", "session_id": "tt-1"})
        reply = res.get_json().get("reply", "")
        self.assertIn("GSP 101", reply)
        self.assertLessEqual(reply.count("GSP 101"), 2)

        # Department lookup
        res_cs = self.client.post("/chat", json={"message": "Computer Science timetable", "session_id": "tt-2"})
        self.assertIn("Computer Science", res_cs.get_json().get("reply", ""))

        # Day lookup
        res_mon = self.client.post("/chat", json={"message": "classes on Monday", "session_id": "tt-3"})
        self.assertIn("Monday", res_mon.get_json().get("reply", ""))

    def test_gate_discrimination_and_second_gate(self):
        """Category 9: Precise Gate Resolution and Ordinal Discrimination (1st Gate vs 2nd Gate)"""
        from resolver import resolve_location

        # 1. Resolver battery check: All 1st gate variations resolve to 1st Gate, all 2nd gate to 2nd Gate
        with app.app_context():
            self.assertEqual(resolve_location("UNN 2nd Gate").formal_name, "UNN 2nd Gate (Abuja / Franco Gate)")
            self.assertEqual(resolve_location("2nd Gate").formal_name, "UNN 2nd Gate (Abuja / Franco Gate)")
            self.assertEqual(resolve_location("second gate").formal_name, "UNN 2nd Gate (Abuja / Franco Gate)")
            self.assertEqual(resolve_location("UNN second gate").formal_name, "UNN 2nd Gate (Abuja / Franco Gate)")
            self.assertEqual(resolve_location("UNN 1st Gate").formal_name, "UNN 1st Gate (Main Gate)")
            self.assertEqual(resolve_location("1st Gate").formal_name, "UNN 1st Gate (Main Gate)")
            self.assertEqual(resolve_location("first gate").formal_name, "UNN 1st Gate (Main Gate)")
            self.assertEqual(resolve_location("UNN first gate").formal_name, "UNN 1st Gate (Main Gate)")
            self.assertEqual(resolve_location("UNN Gate").formal_name, "UNN 1st Gate (Main Gate)")

        # 2. Multi-turn Wayfinding starting from UNN 2nd Gate
        sid = "test-second-gate-multiturn"
        res1 = self.client.post("/chat", json={"message": "take me to Abuja Building", "session_id": sid})
        d1 = res1.get_json()
        self.assertIn("Where are you starting from", d1.get("reply", ""))
        self.assertIn("UNN 2nd Gate (Abuja / Franco Gate)", d1.get("options", []))

        res2 = self.client.post("/chat", json={"message": "UNN 2nd Gate", "session_id": sid})
        d2 = res2.get_json()
        reply2 = d2.get("reply", "")
        self.assertIn("UNN 2nd Gate (Abuja / Franco Gate)", reply2)
        self.assertNotIn("UNN 1st Gate", reply2)
        self.assertEqual(d2.get("source_name"), "UNN 2nd Gate (Abuja / Franco Gate)")
        self.assertEqual(d2.get("destination_name"), "Abuja Building (Prof. Ezeilo Building)")


if __name__ == "__main__":
    unittest.main()
