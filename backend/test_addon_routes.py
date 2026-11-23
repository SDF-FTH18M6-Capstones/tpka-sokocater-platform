import unittest
from datetime import date
from decimal import Decimal

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from models import (
    User,
    Caterer,
    AddOn,
    Booking,
    BookingItem
)


class TestAddOnRoutes(unittest.TestCase):

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
        self.caterer_user = self.create_user(
            "caterer@example.com", "caterer"
        )

        self.customer_user = self.create_user(
            "customer@example.com", "customer"
        )

        self.other_caterer_user = self.create_user(
            "other@example.com", "caterer"
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

        # Create an add-on.
        self.addon = self.create_addon()

        # Create a booking for testing deletion conflicts.
        self.booking = Booking(
            customer_id=self.customer_user.id,
            caterer_id=self.caterer.id,
            event_date=date(2027, 6, 15),
            event_type="Wedding",
            event_location="Nairobi",
            guest_count=50,
            estimated_total=Decimal("25000.00")
        )

        db.session.add(self.booking)
        db.session.commit()

        # Create tokens.
        self.caterer_headers = self.create_token(
            self.caterer_user
        )

        self.customer_headers = self.create_token(
            self.customer_user
        )

        self.other_caterer_headers = self.create_token(
            self.other_caterer_user
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

    def create_addon(self, caterer=None):

        if caterer is None:
            caterer = self.caterer

        addon = AddOn(
            caterer_id=caterer.id,
            addon_name="Extra Drinks",
            description="Additional soft drinks",
            price=Decimal("200.00")
        )

        db.session.add(addon)
        db.session.commit()

        return addon

    def create_token(self, user):

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )

        return {
            "Authorization": f"Bearer {token}"
        }

    def valid_addon_data(self, caterer=None):

        if caterer is None:
            caterer = self.caterer

        return {
            "caterer_id": caterer.id,
            "addon_name": "Extra Drinks",
            "description": "Additional soft drinks",
            "price": "200.00"
        }

    # ==================================================
    # PUBLIC GET ROUTES
    # ==================================================

    def test_get_all_addons_successful(self):

        response = self.client.get("/api/addons")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["data"]), 1)

    def test_get_all_addons_without_token(self):

        response = self.client.get("/api/addons")

        self.assertEqual(response.status_code, 200)

    def test_get_single_addon_successful(self):

        response = self.client.get(
            f"/api/addons/{self.addon.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["data"]["addon_name"],
            "Extra Drinks"
        )

    def test_get_nonexistent_addon(self):

        response = self.client.get("/api/addons/99999")

        self.assertEqual(response.status_code, 404)

    # ==================================================
    # CREATE ADD-ON
    # ==================================================

    def test_caterer_can_create_addon(self):

        data = self.valid_addon_data()
        data["addon_name"] = "Extra Dessert"

        response = self.client.post(
            "/api/addons",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.get_json()["data"]["addon_name"],
            "Extra Dessert"
        )

    def test_create_addon_without_token(self):

        response = self.client.post(
            "/api/addons",
            json=self.valid_addon_data()
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_create_addon(self):

        response = self.client.post(
            "/api/addons",
            json=self.valid_addon_data(),
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_without_profile_cannot_create_addon(self):

        data = self.valid_addon_data()

        response = self.client.post(
            "/api/addons",
            json=data,
            headers=self.no_profile_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_create_addon_for_another_caterer(self):

        data = self.valid_addon_data(
            self.other_caterer
        )

        response = self.client.post(
            "/api/addons",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_create_addon_with_negative_price(self):

        data = self.valid_addon_data()
        data["price"] = "-100.00"

        response = self.client.post(
            "/api/addons",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_addon_without_name(self):

        data = self.valid_addon_data()
        data.pop("addon_name")

        response = self.client.post(
            "/api/addons",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_addon_with_whitespace_name(self):

        data = self.valid_addon_data()
        data["addon_name"] = "   "

        response = self.client.post(
            "/api/addons",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_addon_without_json(self):

        response = self.client.post(
            "/api/addons",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    # ==================================================
    # UPDATE ADD-ON
    # ==================================================

    def test_caterer_can_update_own_addon(self):

        response = self.client.put(
            f"/api/addons/{self.addon.id}",
            json={"addon_name": "Updated Drinks"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["data"]["addon_name"],
            "Updated Drinks"
        )

    def test_update_addon_without_token(self):

        response = self.client.put(
            f"/api/addons/{self.addon.id}",
            json={"addon_name": "Updated Drinks"}
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_update_addon(self):

        response = self.client.put(
            f"/api/addons/{self.addon.id}",
            json={"addon_name": "Updated Drinks"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_other_caterer_cannot_update_addon(self):

        response = self.client.put(
            f"/api/addons/{self.addon.id}",
            json={"addon_name": "Updated Drinks"},
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_update_nonexistent_addon(self):

        response = self.client.put(
            "/api/addons/99999",
            json={"addon_name": "Updated Drinks"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 404)

    def test_update_addon_with_empty_body(self):

        response = self.client.put(
            f"/api/addons/{self.addon.id}",
            json={},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_update_addon_with_negative_price(self):

        response = self.client.put(
            f"/api/addons/{self.addon.id}",
            json={"price": "-100.00"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_caterer_cannot_transfer_addon(self):

        response = self.client.put(
            f"/api/addons/{self.addon.id}",
            json={"caterer_id": self.other_caterer.id},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    # ==================================================
    # DELETE ADD-ON
    # ==================================================

    def test_caterer_can_delete_own_addon(self):

        response = self.client.delete(
            f"/api/addons/{self.addon.id}",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)

        deleted_addon = db.session.get(
            AddOn,
            self.addon.id
        )

        self.assertIsNone(deleted_addon)

    def test_delete_addon_without_token(self):

        response = self.client.delete(
            f"/api/addons/{self.addon.id}"
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_delete_addon(self):

        response = self.client.delete(
            f"/api/addons/{self.addon.id}",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_other_caterer_cannot_delete_addon(self):

        response = self.client.delete(
            f"/api/addons/{self.addon.id}",
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_nonexistent_addon(self):

        response = self.client.delete(
            "/api/addons/99999",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_addon_used_in_booking(self):

        booking_item = BookingItem(
            booking_id=self.booking.id,
            package_id=None,
            addon_id=self.addon.id,
            quantity=2,
            unit_price=Decimal("200.00")
        )

        db.session.add(booking_item)
        db.session.commit()

        response = self.client.delete(
            f"/api/addons/{self.addon.id}",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 409)

        existing_addon = db.session.get(
            AddOn,
            self.addon.id
        )

        self.assertIsNotNone(existing_addon)


if __name__ == "__main__":
    unittest.main()