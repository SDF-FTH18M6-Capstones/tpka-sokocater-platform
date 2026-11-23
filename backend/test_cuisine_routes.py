
import unittest

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from models import User, Caterer, Cuisine, CatererCuisine


class TestCuisineRoutes(unittest.TestCase):

    def setUp(self):

        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "JWT_SECRET_KEY": "sokocater-test-secret-key-for-unit-tests-2026"
        })

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        self.client = self.app.test_client()

        # Create users.
        self.admin_user = self.create_user(
            "admin@example.com", "admin"
        )

        self.caterer_user = self.create_user(
            "caterer@example.com", "caterer"
        )

        self.other_caterer_user = self.create_user(
            "other@example.com", "caterer"
        )

        self.customer_user = self.create_user(
            "customer@example.com", "customer"
        )

        self.no_profile_user = self.create_user(
            "no-profile@example.com", "caterer"
        )

        # Create caterer profiles.
        self.caterer = self.create_caterer(
            self.caterer_user
        )

        self.other_caterer = self.create_caterer(
            self.other_caterer_user,
            "Other Catering Business"
        )

        # Create cuisines.
        self.kenyan = self.create_cuisine("Kenyan")
        self.indian = self.create_cuisine("Indian")

        # Create an existing cuisine assignment.
        self.assignment = self.create_assignment(
            self.caterer,
            self.kenyan
        )

        # Create authentication headers.
        self.admin_headers = self.create_token(
            self.admin_user
        )

        self.caterer_headers = self.create_token(
            self.caterer_user
        )

        self.other_caterer_headers = self.create_token(
            self.other_caterer_user
        )

        self.customer_headers = self.create_token(
            self.customer_user
        )

        self.no_profile_headers = self.create_token(
            self.no_profile_user
        )

    def tearDown(self):

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ==================================================
    # HELPERS
    # ==================================================

    def create_user(self, email, role):

        user = User(
            full_name="Test User",
            email=email,
            password_hash=generate_password_hash("password123"),
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return user

    def create_caterer(
        self,
        user,
        business_name="Fresh Foods Catering"
    ):

        caterer = Caterer(
            user_id=user.id,
            business_name=business_name,
            description="Professional catering services",
            location="Nairobi",
            contact_number="0712345678",
            verification_status="pending"
        )

        db.session.add(caterer)
        db.session.commit()

        return caterer

    def create_cuisine(self, name):

        cuisine = Cuisine(cuisine_name=name)

        db.session.add(cuisine)
        db.session.commit()

        return cuisine

    def create_assignment(self, caterer, cuisine):

        assignment = CatererCuisine(
            caterer_id=caterer.id,
            cuisine_id=cuisine.id
        )

        db.session.add(assignment)
        db.session.commit()

        return assignment

    def create_token(self, user):

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )

        return {
            "Authorization": f"Bearer {token}"
        }

    # ==================================================
    # CUISINE GET TESTS
    # ==================================================

    def test_get_cuisines(self):

        response = self.client.get("/api/cuisines")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    # ==================================================
    # CUISINE CREATE TESTS
    # ==================================================

    def test_admin_can_create_cuisine(self):

        response = self.client.post(
            "/api/cuisines",
            json={"cuisine_name": "Chinese"},
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json["cuisine"]["cuisine_name"],
            "Chinese"
        )

    def test_create_cuisine_requires_authentication(self):

        response = self.client.post(
            "/api/cuisines",
            json={"cuisine_name": "Chinese"}
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_create_cuisine(self):

        response = self.client.post(
            "/api/cuisines",
            json={"cuisine_name": "Chinese"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_create_cuisine(self):

        response = self.client.post(
            "/api/cuisines",
            json={"cuisine_name": "Chinese"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_create_cuisine_rejects_invalid_json(self):

        response = self.client.post(
            "/api/cuisines",
            data="invalid",
            content_type="application/json",
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_cuisine_rejects_missing_name(self):

        response = self.client.post(
            "/api/cuisines",
            json={},
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_cuisine_rejects_whitespace_name(self):

        response = self.client.post(
            "/api/cuisines",
            json={"cuisine_name": "   "},
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_duplicate_cuisine(self):

        response = self.client.post(
            "/api/cuisines",
            json={"cuisine_name": "Kenyan"},
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 409)

    # ==================================================
    # CUISINE UPDATE TESTS
    # ==================================================

    def test_admin_can_update_cuisine(self):

        response = self.client.put(
            f"/api/cuisines/{self.kenyan.id}",
            json={"cuisine_name": "East African"},
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["cuisine"]["cuisine_name"],
            "East African"
        )

    def test_update_cuisine_requires_authentication(self):

        response = self.client.put(
            f"/api/cuisines/{self.kenyan.id}",
            json={"cuisine_name": "East African"}
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_update_cuisine(self):

        response = self.client.put(
            f"/api/cuisines/{self.kenyan.id}",
            json={"cuisine_name": "East African"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_update_cuisine(self):

        response = self.client.put(
            f"/api/cuisines/{self.kenyan.id}",
            json={"cuisine_name": "East African"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_update_missing_cuisine(self):

        response = self.client.put(
            "/api/cuisines/999",
            json={"cuisine_name": "East African"},
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 404)

    def test_update_cuisine_rejects_empty_body(self):

        response = self.client.put(
            f"/api/cuisines/{self.kenyan.id}",
            json={},
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_update_cuisine_rejects_duplicate_name(self):

        response = self.client.put(
            f"/api/cuisines/{self.kenyan.id}",
            json={"cuisine_name": "Indian"},
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 409)

    def test_update_cuisine_rejects_whitespace_name(self):

        response = self.client.put(
            f"/api/cuisines/{self.kenyan.id}",
            json={"cuisine_name": "   "},
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 400)

    # ==================================================
    # CUISINE DELETE TESTS
    # ==================================================

    def test_admin_can_delete_unassigned_cuisine(self):

        chinese = self.create_cuisine("Chinese")

        response = self.client.delete(
            f"/api/cuisines/{chinese.id}",
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(
            db.session.get(Cuisine, chinese.id)
        )

    def test_delete_cuisine_requires_authentication(self):

        response = self.client.delete(
            f"/api/cuisines/{self.indian.id}"
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_delete_cuisine(self):

        response = self.client.delete(
            f"/api/cuisines/{self.indian.id}",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_delete_cuisine(self):

        response = self.client.delete(
            f"/api/cuisines/{self.indian.id}",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_missing_cuisine(self):

        response = self.client.delete(
            "/api/cuisines/999",
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_assigned_cuisine(self):

        response = self.client.delete(
            f"/api/cuisines/{self.kenyan.id}",
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 409)

        self.assertIsNotNone(
            db.session.get(Cuisine, self.kenyan.id)
        )

    # ==================================================
    # CATERER CUISINE GET TESTS
    # ==================================================

    def test_get_caterer_cuisines(self):

        response = self.client.get("/api/caterer-cuisines")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    def test_filter_caterer_cuisines_by_caterer(self):

        response = self.client.get(
            f"/api/caterer-cuisines?caterer_id={self.caterer.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    def test_filter_caterer_cuisines_rejects_invalid_id(self):

        response = self.client.get(
            "/api/caterer-cuisines?caterer_id=invalid"
        )

        self.assertEqual(response.status_code, 400)

    # ==================================================
    # CATERER CUISINE ASSIGNMENT TESTS
    # ==================================================

    def test_caterer_can_assign_cuisine(self):

        response = self.client.post(
            "/api/caterer-cuisines",
            json={
                "caterer_id": self.caterer.id,
                "cuisine_id": self.indian.id
            },
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 201)

    def test_assign_cuisine_requires_authentication(self):

        response = self.client.post(
            "/api/caterer-cuisines",
            json={
                "caterer_id": self.caterer.id,
                "cuisine_id": self.indian.id
            }
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_assign_cuisine(self):

        response = self.client.post(
            "/api/caterer-cuisines",
            json={
                "caterer_id": self.caterer.id,
                "cuisine_id": self.indian.id
            },
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_without_profile_cannot_assign_cuisine(self):

        response = self.client.post(
            "/api/caterer-cuisines",
            json={
                "caterer_id": self.caterer.id,
                "cuisine_id": self.indian.id
            },
            headers=self.no_profile_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_assign_cuisine_to_another_profile(self):

        response = self.client.post(
            "/api/caterer-cuisines",
            json={
                "caterer_id": self.other_caterer.id,
                "cuisine_id": self.indian.id
            },
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_assign_cuisine_rejects_missing_fields(self):

        response = self.client.post(
            "/api/caterer-cuisines",
            json={"cuisine_id": self.indian.id},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_assign_cuisine_rejects_invalid_cuisine(self):

        response = self.client.post(
            "/api/caterer-cuisines",
            json={
                "caterer_id": self.caterer.id,
                "cuisine_id": 999
            },
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 404)

    def test_assign_duplicate_cuisine(self):

        response = self.client.post(
            "/api/caterer-cuisines",
            json={
                "caterer_id": self.caterer.id,
                "cuisine_id": self.kenyan.id
            },
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 409)

    # ==================================================
    # CATERER CUISINE REMOVAL TESTS
    # ==================================================

    def test_caterer_can_remove_own_cuisine(self):

        response = self.client.delete(
            f"/api/caterer-cuisines/{self.assignment.id}",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)

        self.assertIsNone(
            db.session.get(CatererCuisine, self.assignment.id)
        )

    def test_remove_assignment_requires_authentication(self):

        response = self.client.delete(
            f"/api/caterer-cuisines/{self.assignment.id}"
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_remove_assignment(self):

        response = self.client.delete(
            f"/api/caterer-cuisines/{self.assignment.id}",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_other_caterer_cannot_remove_assignment(self):

        response = self.client.delete(
            f"/api/caterer-cuisines/{self.assignment.id}",
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_remove_missing_assignment(self):

        response = self.client.delete(
            "/api/caterer-cuisines/999",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
