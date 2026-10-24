import unittest
from app import app, db
from models import OrientationKB, Timetable, Event, Node, Edge


class TestLionPathPriorityFeatures(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_admin_flow_and_crud(self):
        # 1. Unauthenticated access should redirect to login
        res = self.client.get("/admin", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/admin/login", res.headers["Location"])

        # 2. Login as admin
        login_res = self.client.post("/admin/login", data={"username": "admin", "password": "lionpath2026"}, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b"Admin", login_res.data)

        # 3. Access admin dashboard - should list existing records
        dash_res = self.client.get("/admin")
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn(b"Existing Orientation FAQs", dash_res.data)
        self.assertIn(b"Registered Campus Landmarks", dash_res.data)
        self.assertIn(b"Class Schedules", dash_res.data)
        self.assertIn(b"Scheduled Campus Events", dash_res.data)

        # 4. Test FAQ Add & Delete
        add_faq = self.client.post("/admin/add_faq", data={
            "category": "fees",
            "question_pattern": "test question pattern dummy",
            "answer": "This is a dummy test answer."
        }, follow_redirects=True)
        self.assertEqual(add_faq.status_code, 200)
        self.assertIn(b"FAQ added successfully!", add_faq.data)
        
        with app.app_context():
            created_faq = OrientationKB.query.filter_by(question_pattern="test question pattern dummy").first()
            self.assertIsNotNone(created_faq)
            faq_id = created_faq.kb_id

        del_faq = self.client.post(f"/admin/delete_faq/{faq_id}", follow_redirects=True)
        self.assertEqual(del_faq.status_code, 200)
        self.assertIn(b"FAQ deleted successfully.", del_faq.data)

        # 5. Test Timetable Add & Delete
        add_tt = self.client.post("/admin/add_timetable", data={
            "course_code": "TEST 999",
            "course_title": "Automated Testing",
            "day": "Monday",
            "time": "7:00 AM - 8:00 AM",
            "venue": "Test Lab"
        }, follow_redirects=True)
        self.assertEqual(add_tt.status_code, 200)
        self.assertIn(b"Timetable for TEST 999 added successfully!", add_tt.data)

        with app.app_context():
            created_tt = Timetable.query.filter_by(course_code="TEST 999").first()
            self.assertIsNotNone(created_tt)
            self.assertEqual(created_tt.course_title, "Automated Testing")
            tt_id = created_tt.id

        del_tt = self.client.post(f"/admin/delete_timetable/{tt_id}", follow_redirects=True)
        self.assertEqual(del_tt.status_code, 200)
        self.assertIn(b"TEST 999", del_tt.data)
        self.assertIn(b"deleted successfully", del_tt.data)

        # 6. Test Event Add & Delete
        add_ev = self.client.post("/admin/add_event", data={
            "title": "LionPath Demo Day",
            "date_time": "Friday at 12:00 PM",
            "venue": "Faculty Boardroom"
        }, follow_redirects=True)
        self.assertEqual(add_ev.status_code, 200)
        self.assertIn(b"LionPath Demo Day", add_ev.data)

        with app.app_context():
            created_ev = Event.query.filter_by(title="LionPath Demo Day").first()
            self.assertIsNotNone(created_ev)
            ev_id = created_ev.id

        del_ev = self.client.post(f"/admin/delete_event/{ev_id}", follow_redirects=True)
        self.assertEqual(del_ev.status_code, 200)
        self.assertIn(b"LionPath Demo Day", del_ev.data)
        self.assertIn(b"deleted successfully.", del_ev.data)

        # 7. Test Node Add & Delete with Edge cascade
        add_node = self.client.post("/admin/add_node", data={
            "formal_name": "Temporary Test Annex",
            "informal_names": "temp annex",
            "category": "building",
            "description": "A temporary mock building"
        }, follow_redirects=True)
        self.assertEqual(add_node.status_code, 200)

        with app.app_context():
            created_node = Node.query.filter_by(formal_name="Temporary Test Annex").first()
            self.assertIsNotNone(created_node)
            node_id = created_node.node_id
            other_node = Node.query.first()
            test_edge = Edge(
                source_node_id=node_id,
                destination_node_id=other_node.node_id,
                instruction="Walk straight to other node",
                distance_meters=50
            )
            db.session.add(test_edge)
            db.session.commit()

        del_node = self.client.post(f"/admin/delete_node/{node_id}", follow_redirects=True)
        self.assertEqual(del_node.status_code, 200)
        self.assertIn(b"deleted successfully.", del_node.data)

        with app.app_context():
            orphans = Edge.query.filter((Edge.source_node_id == node_id) | (Edge.destination_node_id == node_id)).all()
            self.assertEqual(len(orphans), 0)

    def test_chatbot_smart_interactions(self):
        # Conversational Acknowledgment
        ack = self.client.post("/chat", json={"message": "okay, got it", "session_id": "test-session-ack"})
        self.assertIn("Glad to help", ack.get_json()["reply"])

        # Physics timetable test
        phy_init = self.client.post("/chat", json={"message": "when is physics?", "session_id": "test-session-phy"})
        data = phy_init.get_json()
        self.assertIn("PHY", data["reply"])

        # Department / Course mapping test (MTH -> Mathematics)
        math_res = self.client.post("/chat", json={"message": "when is maths?", "session_id": "test-session-mth"})
        self.assertTrue("MTH 111" in math_res.get_json()["reply"] or "MTH" in math_res.get_json()["reply"])

        # Typo tolerance (clerance -> faculty clearance)
        clearance_res = self.client.post("/chat", json={"message": "how to do clerance", "session_id": "test-session-clr"})
        clr_text = clearance_res.get_json()["reply"].lower()
        self.assertIn("clearance", clr_text)
        self.assertNotIn("medical centre", clr_text)

        # Campus Landmark Disambiguation (Library ambiguity test as shown in user screenshot)
        self.client.post("/chat", json={"message": "how do i get to physics department", "session_id": "test-session-lib-flow"})
        lib_q = self.client.post("/chat", json={"message": "library", "session_id": "test-session-lib-flow"})
        self.assertIn("Faculty of Physical Sciences Library", lib_q.get_json()["reply"])
        self.assertIn("Nnamdi Azikiwe Library", lib_q.get_json()["reply"])

        # Disambiguate to Faculty Library
        lib_choice = self.client.post("/chat", json={"message": "faculty", "session_id": "test-session-lib-flow"})
        res_choice = lib_choice.get_json()
        self.assertIn("Walking Route to Physics and Astronomy Building", res_choice["reply"])
        self.assertIn("Estimated Distance & Time", res_choice["reply"])
        self.assertIn("Pass through: Carver Building", res_choice["reply"])
        self.assertIn("Arrive at: Physics and Astronomy Building", res_choice["reply"])
        self.assertEqual(res_choice.get("image"), "physics.jpeg")

        # 1. Course Timetable Deduplication Test (GSP 101 across tracks prints once, not 7 times)
        tt_res = self.client.post("/chat", json={"message": "GSP 101", "session_id": "test-tt-dedup"})
        tt_reply = tt_res.get_json()["reply"]
        self.assertIn("GSP 101", tt_reply)
        self.assertIn("General Studies Building (GS Building)", tt_reply)
        self.assertLessEqual(tt_reply.count("GSP 101"), 2)

        # 2. Course Venue Navigation & Typo Handling (Resolving exact screenshot flop)
        nav_flop = self.client.post("/chat", json={"message": "how goi go for the GSP 101 class?", "session_id": "test-course-nav-flow"})
        nav_data1 = nav_flop.get_json()
        self.assertIn("General Studies Building", nav_data1["reply"])
        self.assertIn("Where are you starting from", nav_data1["reply"])
        self.assertIn("Carver Building", nav_data1.get("options", []))

        # Turn 2: User provides origin
        nav_turn2 = self.client.post("/chat", json={"message": "Carver Building", "session_id": "test-course-nav-flow"})
        nav_data2 = nav_turn2.get_json()
        self.assertIn("Walking Route to General Studies Building", nav_data2["reply"])
        self.assertIn("Estimated Distance & Time", nav_data2["reply"])
        self.assertEqual(nav_data2.get("destination_name"), "General Studies Building (GS Building)")

        # 3. Direct Route to Course Venue ('from Carver to GSP 101')
        direct_res = self.client.post("/chat", json={"message": "from Carver to GSP 101", "session_id": "test-direct-course"})
        self.assertIn("Walking Route to General Studies Building", direct_res.get_json()["reply"])

        # 4. Date & Time Utilities ('what is todays date?')
        date_res = self.client.post("/chat", json={"message": "what is todays date?", "session_id": "test-date"})
        date_reply = date_res.get_json()["reply"]
        self.assertIn("Today is", date_reply)
        self.assertNotIn("scheduled lectures", date_reply)


if __name__ == "__main__":
    unittest.main()
