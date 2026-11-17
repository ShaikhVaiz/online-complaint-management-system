import os
import sys
import unittest
import json
import uuid

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

# Set test environment with isolated test db
import tempfile
os.environ["PORT"] = "5999"
test_db = os.path.join(tempfile.gettempdir(), "test_complaint_db.sqlite")
os.environ["SQLITE_PATH"] = test_db

import app

class TestComplaintSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.app.config["TESTING"] = True
        app.app.config["SECRET_KEY"] = "test_secret_key"

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except Exception:
                pass

    def setUp(self):
        self.client = app.app.test_client()

    def test_01_duplicate_email_registration(self):
        """Requirement 1: Test duplicate email registration."""
        payload = {
            "full_name": "Duplicate Email Test",
            "student_id": f"TEST_ROLL_{uuid.uuid4().hex[:6]}",
            "email": "rahul.sharma@college.com", # already exists in seeds
            "password": "Password@123"
        }
        res = self.client.post("/api/register", json=payload)
        data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("message"), "A student with this Email or Roll Number is already registered.")

    def test_02_duplicate_roll_number_registration(self):
        """Requirement 2: Test duplicate roll number registration."""
        payload = {
            "full_name": "Duplicate Roll Test",
            "student_id": "CS101", # already exists in seeds
            "email": f"test_{uuid.uuid4().hex[:6]}@college.com",
            "password": "Password@123"
        }
        res = self.client.post("/api/register", json=payload)
        data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("message"), "A student with this Email or Roll Number is already registered.")

    def test_03_successful_student_registration(self):
        """Requirement 3: Test successful student registration."""
        unique_id = uuid.uuid4().hex[:6]
        payload = {
            "full_name": f"Student {unique_id}",
            "student_id": f"CS_NEW_{unique_id}",
            "email": f"student_{unique_id}@college.com",
            "password": "Student@Strong123"
        }
        res = self.client.post("/api/register", json=payload)
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get("success"))
        self.assertIn("registered successfully", data.get("message", "").lower())

    def test_04_student_login(self):
        """Requirement 4: Test student login."""
        payload = {
            "role": "student",
            "identifier": "rahul.sharma@college.com",
            "password": "Student@123"
        }
        res = self.client.post("/api/login", json=payload)
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get("success"))

        me_res = self.client.get("/api/me")
        me_data = me_res.get_json()
        self.assertTrue(me_data.get("logged_in"))
        self.assertEqual(me_data.get("role"), "student")
        self.assertEqual(me_data.get("student_id"), "CS101")

    def test_05_admin_login(self):
        """Requirement 5: Test admin login."""
        payload = {
            "role": "admin",
            "identifier": "admin@college.com",
            "password": "Admin@123"
        }
        res = self.client.post("/api/login", json=payload)
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get("success"))

        me_res = self.client.get("/api/me")
        me_data = me_res.get_json()
        self.assertTrue(me_data.get("logged_in"))
        self.assertEqual(me_data.get("role"), "admin")

    def test_06_complaint_listing_and_details(self):
        """Requirement 6: Test complaint listing and complaint details."""
        self.client.post("/api/login", json={"role": "admin", "identifier": "admin@college.com", "password": "Admin@123"})
        res = self.client.get("/api/complaints")
        self.assertEqual(res.status_code, 200)
        complaints = res.get_json()
        self.assertIsInstance(complaints, list)
        self.assertGreater(len(complaints), 0)

        first = complaints[0]
        self.assertIn("id", first)
        self.assertIn("title", first)
        self.assertIn("category", first)
        self.assertIn("status", first)
        self.assertIn("has_image", first)
        self.assertIsNone(first.get("image_data"))

    def test_07_complaint_image_viewing(self):
        """Requirement 7: Test complaint image upload and on-demand image retrieval."""
        sample_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        create_payload = {
            "student_name": "Image Tester",
            "student_id": "CS_IMG",
            "category": "Laboratory",
            "title": "Broken Monitor with Photo",
            "description": "Image attachment test description",
            "image_data": sample_b64
        }
        post_res = self.client.post("/api/complaints", json=create_payload)
        post_data = post_res.get_json()
        self.assertEqual(post_res.status_code, 200)
        self.assertTrue(post_data.get("success"))
        comp_id = post_data.get("id")

        list_res = self.client.get("/api/complaints")
        items = list_res.get_json()
        matching = [c for c in items if c["id"] == comp_id]
        self.assertEqual(len(matching), 1)
        self.assertTrue(matching[0]["has_image"])
        self.assertIsNone(matching[0]["image_data"])

        img_res = self.client.get(f"/api/complaints/{comp_id}/image")
        self.assertEqual(img_res.status_code, 200)
        img_data = img_res.get_json()
        self.assertTrue(img_data.get("success"))
        self.assertEqual(img_data.get("image_data"), sample_b64)

    def test_08_complaint_status_updates(self):
        """Requirement 8: Test complaint status updates."""
        res = self.client.get("/api/complaints")
        complaints = res.get_json()
        target_id = complaints[0]["id"]

        up_res = self.client.put(f"/api/complaints/{target_id}/status", json={"status": "In Progress"})
        self.assertEqual(up_res.status_code, 200)
        self.assertTrue(up_res.get_json().get("success"))

        res2 = self.client.get("/api/complaints")
        updated = next(c for c in res2.get_json() if c["id"] == target_id)
        self.assertEqual(updated["status"], "In Progress")

        up_res2 = self.client.put(f"/api/complaints/{target_id}/status", json={"status": "Resolved"})
        self.assertEqual(up_res2.status_code, 200)
        self.assertTrue(up_res2.get_json().get("success"))

    def test_09_logout(self):
        """Requirement 9: Test logout."""
        self.client.post("/api/login", json={"role": "student", "identifier": "rahul.sharma@college.com", "password": "Student@123"})
        me1 = self.client.get("/api/me").get_json()
        self.assertTrue(me1.get("logged_in"))

        lo_res = self.client.post("/api/logout")
        self.assertEqual(lo_res.status_code, 200)
        self.assertTrue(lo_res.get_json().get("success"))

        me2 = self.client.get("/api/me").get_json()
        self.assertFalse(me2.get("logged_in"))

    def test_10_html_and_js_integrity(self):
        """Requirement 10: Verify frontend message visibility and structure in HTML/JS/CSS."""
        with open(os.path.join(APP_DIR, "index.html"), encoding="utf-8") as f:
            index_html = f.read()
        with open(os.path.join(APP_DIR, "script.js"), encoding="utf-8") as f:
            script_js = f.read()
        with open(os.path.join(APP_DIR, "style.css"), encoding="utf-8") as f:
            style_css = f.read()
        with open(os.path.join(APP_DIR, "admin.html"), encoding="utf-8") as f:
            admin_html = f.read()

        self.assertIn('id="authMessage"', index_html)
        self.assertIn('switchAuthTab', index_html)
        self.assertIn('showAuthMessage', script_js)
        self.assertIn('clearAuthMessage', script_js)
        self.assertIn('openComplaintPhoto', script_js)
        self.assertIn('/api/complaints/${complaintId}/image', script_js)
        self.assertIn('.message-box.error', style_css)
        self.assertIn('display: block !important;', style_css)
        self.assertIn('id="adminTableBody"', admin_html)
        self.assertIn('initAdminPage', admin_html)

if __name__ == "__main__":
    unittest.main()
