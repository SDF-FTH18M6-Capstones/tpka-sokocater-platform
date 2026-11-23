
import unittest
from datetime import timedelta
from decimal import Decimal

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from models import (
    User,
    Caterer,
    Menu,
    Package,
    MenuItem,
    PackageItem
)


class TestCatererRoutes(unittest.TestCase):

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

        self.caterer_user = self.create_user(
            email="caterer@example.com",
            role="caterer"
        )

        self.customer_user = self.create_user(
            email="customer@example.com",
            role="customer"
        )

        self.other_caterer_user = self.create_user(
            email="other@example.com",
            role="caterer"
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ==================================================
    # HELPER METHODS
    # ==================================================

    def create_user(
        self,
        full_name="Test User",
        email="test@example.com",
        role="customer"
    ):
        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash("password123"),
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return user

    def create_token(self, user):
        token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role
            }
        )

        return {
            "Authorization": f"Bearer {token}"
        }

    def create_caterer_profile(self, user=None, **overrides):
        if user is None:
            user = self.caterer_user

        verification_status = overrides.pop(
            "verification_status",
            "pending"
        )

        data = {
            "user_id": user.id,
            "business_name": "Fresh Foods Catering",
            "description": "Professional catering services",
            "location": "Nairobi",
            "contact_number": "0712345678",
            "business_image": "https://example.com/image.jpg"
        }

        data.update(overrides)

        caterer = Caterer(
            **data,
            verification_status=verification_status
        )

        db.session.add(caterer)
        db.session.commit()

        return caterer

    def valid_profile_data(self, user=None):
        if user is None:
            user = self.caterer_user

        return {
            "user_id": user.id,
            "business_name": "Fresh Foods Catering",
            "description": "Professional catering services",
            "location": "Nairobi",
            "contact_number": "0712345678",
            "business_image": "https://example.com/image.jpg"
        }

    def create_package(
        self,
        caterer,
        package_name="Wedding Package",
        price_per_guest="1500.00",
        minimum_guests=50,
        maximum_guests=200
    ):
        package = Package(
            caterer_id=caterer.id,
            package_name=package_name,
            description="A catering package",
            price_per_guest=Decimal(price_per_guest),
            minimum_guests=minimum_guests,
            maximum_guests=maximum_guests
        )

        db.session.add(package)
        db.session.commit()

        return package

    def create_menu_item(
        self,
        caterer,
        item_name="Chicken",
        price="500.00"
    ):
        menu = Menu(
            caterer_id=caterer.id,
            menu_name="Wedding Menu"
        )

        db.session.add(menu)
        db.session.flush()

        menu_item = MenuItem(
            menu_id=menu.id,
            item_name=item_name,
            description=f"{item_name} description",
            price=Decimal(price)
        )

        db.session.add(menu_item)
        db.session.commit()

        return menu_item

    # ==================================================
    # PUBLIC GET ROUTES
    # ==================================================

    def test_get_all_caterers_successful(self):
        self.create_caterer_profile()

        response = self.client.get("/api/caterers")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 1)

    def test_get_all_caterers_without_authentication(self):
        response = self.client.get("/api/caterers")

        self.assertEqual(response.status_code, 200)

    def test_pending_and_verified_caterers_are_publicly_visible(self):
        self.create_caterer_profile(
            user=self.caterer_user,
            verification_status="pending"
        )

        self.create_caterer_profile(
            user=self.other_caterer_user,
            verification_status="verified"
        )

        response = self.client.get("/api/caterers")

        self.assertEqual(response.status_code, 200)

        caterers = response.get_json()["data"]

        self.assertEqual(len(caterers), 2)

        statuses = {
            caterer["verification_status"]
            for caterer in caterers
        }

        self.assertEqual(
            statuses,
            {"pending", "verified"}
        )

    def test_get_single_caterer_successful(self):
        caterer = self.create_caterer_profile()

        response = self.client.get(
            f"/api/caterers/{caterer.id}"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(
            data["data"]["business_name"],
            "Fresh Foods Catering"
        )

    def test_get_single_caterer_not_found(self):
        response = self.client.get("/api/caterers/999")

        self.assertEqual(response.status_code, 404)

    # ==================================================
    # CREATE CATERER ROUTE
    # ==================================================

    def test_create_caterer_successful(self):
        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data(),
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 201)

        data = response.get_json()

        self.assertEqual(
            data["message"],
            "Caterer created successfully"
        )

        self.assertEqual(
            data["data"]["business_name"],
            "Fresh Foods Catering"
        )

        self.assertEqual(
            data["data"]["verification_status"],
            "pending"
        )

    def test_create_caterer_without_token(self):
        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data()
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_create_caterer_profile(self):
        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data(self.customer_user),
            headers=self.create_token(self.customer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_create_profile_for_another_user(self):
        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data(self.other_caterer_user),
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_duplicate_caterer_profile_rejected(self):
        self.create_caterer_profile()

        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data(),
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 409)

    def test_create_caterer_with_invalid_data(self):
        data = self.valid_profile_data()
        data["business_name"] = "A"

        response = self.client.post(
            "/api/caterers",
            json=data,
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_create_caterer_with_whitespace_business_name(self):
        data = self.valid_profile_data()
        data["business_name"] = "   "

        response = self.client.post(
            "/api/caterers",
            json=data,
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_create_caterer_with_whitespace_location(self):
        data = self.valid_profile_data()
        data["location"] = "   "

        response = self.client.post(
            "/api/caterers",
            json=data,
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_create_caterer_with_business_image_over_255_characters(self):
        data = self.valid_profile_data()
        data["business_image"] = "a" * 256

        response = self.client.post(
            "/api/caterers",
            json=data,
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_create_caterer_without_json(self):
        response = self.client.post(
            "/api/caterers",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_verification_status_cannot_be_supplied(self):
        data = self.valid_profile_data()
        data["verification_status"] = "verified"

        response = self.client.post(
            "/api/caterers",
            json=data,
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

        caterer = Caterer.query.filter_by(
            user_id=self.caterer_user.id
        ).first()

        self.assertIsNone(caterer)

    # ==================================================
    # UPDATE CATERER ROUTE
    # ==================================================

    def test_update_own_caterer_profile_successful(self):
        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={
                "business_name": "Updated Catering Business"
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.get_json()["data"]["business_name"],
            "Updated Catering Business"
        )

    def test_update_caterer_without_token(self):
        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={
                "business_name": "Updated Business"
            }
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_update_caterer_profile(self):
        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={
                "business_name": "Updated Business"
            },
            headers=self.create_token(self.customer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_update_another_profile(self):
        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={
                "business_name": "Unauthorized Update"
            },
            headers=self.create_token(self.other_caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_update_nonexistent_caterer(self):
        response = self.client.put(
            "/api/caterers/999",
            json={
                "business_name": "Updated Business"
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 404)

    def test_caterer_cannot_change_profile_ownership(self):
        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={
                "user_id": self.other_caterer_user.id
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_empty_update_request_is_rejected(self):
        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={},
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.get_json()["error"],
            "No update data provided"
        )

    def test_update_with_invalid_json_is_rejected(self):
        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            data="this is not valid JSON",
            content_type="application/json",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_caterer_cannot_change_verification_status(self):
        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={
                "verification_status": "verified"
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

        db.session.refresh(caterer)

        self.assertEqual(
            caterer.verification_status,
            "pending"
        )

    def test_update_with_whitespace_business_name_is_rejected(self):
        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={
                "business_name": "   "
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    # ==================================================
    # CATERER PACKAGES AND PRICE RANGE TESTS
    # ==================================================

    def test_caterer_detail_includes_packages(self):
        caterer = self.create_caterer_profile()

        self.create_package(
            caterer,
            package_name="Wedding Package",
            price_per_guest="1500.00"
        )

        response = self.client.get(
            f"/api/caterers/{caterer.id}"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()["data"]

        self.assertIn("packages", data)
        self.assertEqual(len(data["packages"]), 1)

        self.assertEqual(
            data["packages"][0]["package_name"],
            "Wedding Package"
        )

    def test_caterer_detail_includes_package_menu_items(self):
        caterer = self.create_caterer_profile()

        package = self.create_package(caterer)

        menu_item = self.create_menu_item(
            caterer,
            item_name="Chicken"
        )

        db.session.add(
            PackageItem(
                package_id=package.id,
                menu_item_id=menu_item.id
            )
        )

        db.session.commit()

        response = self.client.get(
            f"/api/caterers/{caterer.id}"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()["data"]

        package_data = data["packages"][0]

        self.assertEqual(
            len(package_data["menu_items"]),
            1
        )

        self.assertEqual(
            package_data["menu_items"][0]["item_name"],
            "Chicken"
        )

    def test_caterer_price_range_is_calculated_correctly(self):
        caterer = self.create_caterer_profile()

        self.create_package(
            caterer,
            package_name="Basic Package",
            price_per_guest="1000.00"
        )

        self.create_package(
            caterer,
            package_name="Premium Package",
            price_per_guest="3500.00"
        )

        self.create_package(
            caterer,
            package_name="Standard Package",
            price_per_guest="2000.00"
        )

        response = self.client.get(
            f"/api/caterers/{caterer.id}"
        )

        self.assertEqual(response.status_code, 200)

        price_range = response.get_json()["data"]["price_range"]

        self.assertEqual(
            price_range["min_price"],
            "1000.00"
        )

        self.assertEqual(
            price_range["max_price"],
            "3500.00"
        )

    def test_caterer_with_one_package_has_equal_min_and_max_price(self):
        caterer = self.create_caterer_profile()

        self.create_package(
            caterer,
            price_per_guest="2500.00"
        )

        response = self.client.get(
            f"/api/caterers/{caterer.id}"
        )

        self.assertEqual(response.status_code, 200)

        price_range = response.get_json()["data"]["price_range"]

        self.assertEqual(
            price_range["min_price"],
            "2500.00"
        )

        self.assertEqual(
            price_range["max_price"],
            "2500.00"
        )

    def test_caterer_without_packages_returns_empty_package_list(self):
        caterer = self.create_caterer_profile()

        response = self.client.get(
            f"/api/caterers/{caterer.id}"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()["data"]

        self.assertEqual(data["packages"], [])

    def test_caterer_without_packages_returns_null_price_range(self):
        caterer = self.create_caterer_profile()

        response = self.client.get(
            f"/api/caterers/{caterer.id}"
        )

        self.assertEqual(response.status_code, 200)

        price_range = response.get_json()["data"]["price_range"]

        self.assertIsNone(price_range["min_price"])
        self.assertIsNone(price_range["max_price"])

    # ==================================================
    # INVALID JWT IDENTITY AND TOKEN TESTS
    # ==================================================

    def test_invalid_jwt_identity_is_rejected(self):
        token = create_access_token(
            identity="not-an-integer",
            additional_claims={
                "role": "caterer"
            }
        )

        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data(),
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        self.assertEqual(response.status_code, 401)

    def test_invalid_token_is_rejected(self):
        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data(),
            headers={
                "Authorization": "Bearer invalid.jwt.token"
            }
        )

        self.assertEqual(response.status_code, 422)

    def test_expired_token_is_rejected(self):
        expired_token = create_access_token(
            identity=str(self.caterer_user.id),
            additional_claims={
                "role": "caterer"
            },
            expires_delta=timedelta(seconds=-1)
        )

        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data(),
            headers={
                "Authorization": f"Bearer {expired_token}"
            }
        )

        self.assertEqual(response.status_code, 401)

    # ==================================================
    # DELETE CATERER ROUTE
    # ==================================================

    def test_delete_own_caterer_profile_successful(self):
        caterer = self.create_caterer_profile()

        caterer_id = caterer.id

        response = self.client.delete(
            f"/api/caterers/{caterer_id}",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 200)

        self.assertIsNone(
            db.session.get(Caterer, caterer_id)
        )

    def test_delete_caterer_with_related_menu_returns_conflict(self):
        caterer = self.create_caterer_profile()

        menu = Menu(
            caterer_id=caterer.id,
            menu_name="Lunch Menu"
        )

        db.session.add(menu)
        db.session.commit()

        caterer_id = caterer.id
        menu_id = menu.id

        response = self.client.delete(
            f"/api/caterers/{caterer_id}",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 409)

        self.assertIsNotNone(
            db.session.get(Caterer, caterer_id)
        )

        self.assertIsNotNone(
            db.session.get(Menu, menu_id)
        )

    def test_delete_caterer_without_token(self):
        caterer = self.create_caterer_profile()

        response = self.client.delete(
            f"/api/caterers/{caterer.id}"
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_delete_caterer_profile(self):
        caterer = self.create_caterer_profile()

        response = self.client.delete(
            f"/api/caterers/{caterer.id}",
            headers=self.create_token(self.customer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_delete_another_profile(self):
        caterer = self.create_caterer_profile()

        response = self.client.delete(
            f"/api/caterers/{caterer.id}",
            headers=self.create_token(self.other_caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_nonexistent_caterer(self):
        response = self.client.delete(
            "/api/caterers/999",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
