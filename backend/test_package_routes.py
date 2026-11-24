
import unittest
from datetime import timedelta
from decimal import Decimal

from app import create_app
from extensions import db
from models import (
    User,
    Caterer,
    Package,
    Menu,
    MenuItem,
    PackageItem,
    AddOn,
    PackageAddOn
)
from flask_jwt_extended import create_access_token


class TestPackageRoutes(unittest.TestCase):

    def setUp(self):

        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "JWT_SECRET_KEY": "sokocater-test-secret-key-for-unit-tests-2026"
        })

        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # ==========================================
        # CREATE USERS
        # ==========================================

        self.customer = User(
            full_name="Test Customer",
            email="customer@test.com",
            password_hash="hashedpassword",
            role="customer"
        )

        self.caterer_user = User(
            full_name="Test Caterer",
            email="caterer@test.com",
            password_hash="hashedpassword",
            role="caterer"
        )

        self.other_caterer_user = User(
            full_name="Other Caterer",
            email="other@test.com",
            password_hash="hashedpassword",
            role="caterer"
        )

        self.food_caterer_user = User(
            full_name="Food Caterer",
            email="food@test.com",
            password_hash="hashedpassword",
            role="caterer"
        )

        db.session.add_all([
            self.customer,
            self.caterer_user,
            self.other_caterer_user,
            self.food_caterer_user
        ])

        db.session.commit()

        # ==========================================
        # CREATE CATERER PROFILES
        # ==========================================

        self.caterer = Caterer(
            user_id=self.caterer_user.id,
            business_name="Test Catering",
            location="Nairobi",
            category="Wedding",
            verification_status="pending"
        )

        self.other_caterer = Caterer(
            user_id=self.other_caterer_user.id,
            business_name="Other Catering",
            location="Nairobi",
            category="Corporate",
            verification_status="pending"
        )

        self.food_caterer = Caterer(
            user_id=self.food_caterer_user.id,
            business_name="Food Only Catering",
            location="Nairobi",
            category="Food",
            verification_status="pending"
        )

        db.session.add_all([
            self.caterer,
            self.other_caterer,
            self.food_caterer
        ])

        db.session.commit()

        # ==========================================
        # CREATE EXISTING PACKAGE
        # ==========================================

        self.package = Package(
            caterer_id=self.caterer.id,
            package_name="Wedding Package",
            description="A wedding catering package",
            price_per_guest=Decimal("1500.00"),
            minimum_guests=20,
            maximum_guests=200
        )

        db.session.add(self.package)
        db.session.commit()

        # ==========================================
        # CREATE JWT TOKENS
        # ==========================================

        self.caterer_token = create_access_token(
            identity=str(self.caterer_user.id),
            additional_claims={"role": "caterer"}
        )

        self.other_caterer_token = create_access_token(
            identity=str(self.other_caterer_user.id),
            additional_claims={"role": "caterer"}
        )

        self.food_caterer_token = create_access_token(
            identity=str(self.food_caterer_user.id),
            additional_claims={"role": "caterer"}
        )

        self.customer_token = create_access_token(
            identity=str(self.customer.id),
            additional_claims={"role": "customer"}
        )

        self.caterer_headers = {
            "Authorization": f"Bearer {self.caterer_token}"
        }

        self.other_caterer_headers = {
            "Authorization": f"Bearer {self.other_caterer_token}"
        }

        self.food_caterer_headers = {
            "Authorization": f"Bearer {self.food_caterer_token}"
        }

        self.customer_headers = {
            "Authorization": f"Bearer {self.customer_token}"
        }

        # ==========================================
        # VALID PACKAGE DATA
        # ==========================================

        self.valid_package_data = {
            "caterer_id": self.caterer.id,
            "package_name": "Birthday Package",
            "description": "Birthday catering package",
            "price_per_guest": "1200.00",
            "minimum_guests": 10,
            "maximum_guests": 100
        }

    def tearDown(self):

        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    # ==========================================
    # HELPER: CREATE MENU ITEM
    # ==========================================

    def create_menu_item(self, caterer, item_name):

        menu = Menu(
            caterer_id=caterer.id,
            menu_name=f"{item_name} Menu",
            description="Test menu"
        )

        db.session.add(menu)
        db.session.flush()

        menu_item = MenuItem(
            menu_id=menu.id,
            item_name=item_name,
            description=f"{item_name} description",
            price=Decimal("250.00")
        )

        db.session.add(menu_item)
        db.session.commit()

        return menu_item

    # ==========================================
    # HELPER: CREATE ADD-ON
    # ==========================================

    def create_addon(self, caterer, addon_name, addon_type):

        addon = AddOn(
            caterer_id=caterer.id,
            addon_name=addon_name,
            description=f"{addon_name} description",
            price=Decimal("5000.00"),
            addon_type=addon_type
        )

        db.session.add(addon)
        db.session.commit()

        return addon

    # ==========================================
    # GET ALL PACKAGES
    # ==========================================

    def test_get_all_packages(self):

        response = self.client.get("/api/packages")

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json)
        self.assertEqual(len(response.json["data"]), 1)

    # ==========================================
    # GET SINGLE PACKAGE
    # ==========================================

    def test_get_single_package(self):

        response = self.client.get(
            f"/api/packages/{self.package.id}"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.json["data"]["package_name"],
            "Wedding Package"
        )

    def test_get_nonexistent_package(self):

        response = self.client.get("/api/packages/999")

        self.assertEqual(response.status_code, 404)

    # ==========================================
    # CREATE PACKAGE
    # ==========================================

    def test_caterer_can_create_package(self):

        response = self.client.post(
            "/api/packages",
            json=self.valid_package_data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.json["data"]["package_name"],
            "Birthday Package"
        )

    def test_create_package_without_token(self):

        response = self.client.post(
            "/api/packages",
            json=self.valid_package_data
        )

        self.assertEqual(response.status_code, 401)

    def test_create_package_with_invalid_token(self):

        response = self.client.post(
            "/api/packages",
            json=self.valid_package_data,
            headers={
                "Authorization": "Bearer invalid.jwt.token"
            }
        )

        self.assertEqual(response.status_code, 422)

    def test_create_package_with_expired_token(self):

        expired_token = create_access_token(
            identity=str(self.caterer_user.id),
            additional_claims={"role": "caterer"},
            expires_delta=timedelta(seconds=-1)
        )

        response = self.client.post(
            "/api/packages",
            json=self.valid_package_data,
            headers={
                "Authorization": f"Bearer {expired_token}"
            }
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_create_package(self):

        response = self.client.post(
            "/api/packages",
            json=self.valid_package_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_without_profile_cannot_create_package(self):

        user = User(
            full_name="No Profile Caterer",
            email="noprofile@test.com",
            password_hash="hashedpassword",
            role="caterer"
        )

        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": "caterer"}
        )

        response = self.client.post(
            "/api/packages",
            json=self.valid_package_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_create_package_for_another_caterer(self):

        data = self.valid_package_data.copy()
        data["caterer_id"] = self.other_caterer.id

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_create_package_with_invalid_data(self):

        data = self.valid_package_data.copy()
        data["package_name"] = "A"

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_package_without_json(self):

        response = self.client.post(
            "/api/packages",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    # ==========================================
    # UPDATE PACKAGE
    # ==========================================

    def test_caterer_can_update_own_package(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"package_name": "Updated Wedding Package"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.json["data"]["package_name"],
            "Updated Wedding Package"
        )

    def test_update_package_without_token(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"package_name": "Updated Package"}
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_update_package(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"package_name": "Updated Package"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_update_another_caterers_package(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"package_name": "Changed Package"},
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_update_nonexistent_package(self):

        response = self.client.put(
            "/api/packages/999",
            json={"package_name": "Updated Package"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 404)

    def test_caterer_cannot_transfer_package_to_another_caterer(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"caterer_id": self.other_caterer.id},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_update_package_with_invalid_data(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"package_name": "A"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_update_package_without_json(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    # ==========================================
    # ADDITIONAL PACKAGE UPDATE VALIDATION TESTS
    # ==========================================

    def test_update_minimum_guests_above_existing_maximum(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"minimum_guests": 250},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

        db.session.refresh(self.package)

        self.assertEqual(self.package.minimum_guests, 20)
        self.assertEqual(self.package.maximum_guests, 200)

    def test_update_maximum_guests_below_existing_minimum(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"maximum_guests": 10},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

        db.session.refresh(self.package)

        self.assertEqual(self.package.minimum_guests, 20)
        self.assertEqual(self.package.maximum_guests, 200)

    def test_update_package_with_empty_json(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    # ==========================================
    # DELETE PACKAGE
    # ==========================================

    def test_caterer_can_delete_own_package(self):

        response = self.client.delete(
            f"/api/packages/{self.package.id}",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)

        deleted_package = db.session.get(
            Package,
            self.package.id
        )

        self.assertIsNone(deleted_package)

    def test_delete_package_without_token(self):

        response = self.client.delete(
            f"/api/packages/{self.package.id}"
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_delete_package(self):

        response = self.client.delete(
            f"/api/packages/{self.package.id}",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_delete_another_caterers_package(self):

        response = self.client.delete(
            f"/api/packages/{self.package.id}",
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_nonexistent_package(self):

        response = self.client.delete(
            "/api/packages/999",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 404)

    # ==========================================
    # PACKAGE MENU ITEM TESTS
    # ==========================================

    def test_caterer_can_create_package_with_menu_items(self):

        item1 = self.create_menu_item(
            self.caterer,
            "Pilau"
        )

        item2 = self.create_menu_item(
            self.caterer,
            "Chicken"
        )

        data = self.valid_package_data.copy()
        data["menu_item_ids"] = [item1.id, item2.id]

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 201)

        returned_ids = {
            item["id"]
            for item in response.json["data"]["menu_items"]
        }

        self.assertEqual(
            returned_ids,
            {item1.id, item2.id}
        )

    def test_caterer_cannot_use_another_caterers_menu_item(self):

        other_item = self.create_menu_item(
            self.other_caterer,
            "Beef Stew"
        )

        data = self.valid_package_data.copy()
        data["menu_item_ids"] = [other_item.id]

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_caterer_can_update_package_menu_items(self):

        item1 = self.create_menu_item(
            self.caterer,
            "Pilau"
        )

        item2 = self.create_menu_item(
            self.caterer,
            "Chapati"
        )

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={
                "menu_item_ids": [item1.id, item2.id]
            },
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = {
            item["id"]
            for item in response.json["data"]["menu_items"]
        }

        self.assertEqual(
            returned_ids,
            {item1.id, item2.id}
        )

    def test_caterer_can_clear_package_menu_items(self):

        item = self.create_menu_item(
            self.caterer,
            "Rice"
        )

        initial_response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"menu_item_ids": [item.id]},
            headers=self.caterer_headers
        )

        self.assertEqual(initial_response.status_code, 200)

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"menu_item_ids": []},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.json["data"]["menu_items"],
            []
        )

    # ==========================================
    # PACKAGE ADD-ON TESTS
    # ==========================================

    def test_wedding_caterer_can_create_package_with_all_addon_types(self):

        venue = self.create_addon(self.caterer, "Garden Venue", "venue")
        chairs = self.create_addon(self.caterer, "Guest Chairs", "chairs")
        tables = self.create_addon(self.caterer, "Dining Tables", "tables")
        materials = self.create_addon(self.caterer, "Decor Materials", "materials")

        data = self.valid_package_data.copy()
        data["addon_ids"] = [
            venue.id,
            chairs.id,
            tables.id,
            materials.id
        ]

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 201)

        returned_types = {
            addon["addon_type"]
            for addon in response.json["data"]["addons"]
        }

        self.assertEqual(
            returned_types,
            {"venue", "chairs", "tables", "materials"}
        )

    def test_corporate_caterer_can_use_chairs_and_tables(self):

        chairs = self.create_addon(
            self.other_caterer,
            "Corporate Chairs",
            "chairs"
        )

        tables = self.create_addon(
            self.other_caterer,
            "Conference Tables",
            "tables"
        )

        data = {
            "caterer_id": self.other_caterer.id,
            "package_name": "Corporate Meeting Package",
            "description": "Corporate event package",
            "price_per_guest": "1800.00",
            "minimum_guests": 10,
            "maximum_guests": 100,
            "addon_ids": [chairs.id, tables.id]
        }

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 201)

        returned_ids = {
            addon["id"]
            for addon in response.json["data"]["addons"]
        }

        self.assertEqual(
            returned_ids,
            {chairs.id, tables.id}
        )

    def test_corporate_caterer_cannot_use_venue(self):

        venue = self.create_addon(
            self.other_caterer,
            "Corporate Venue",
            "venue"
        )

        data = {
            "caterer_id": self.other_caterer.id,
            "package_name": "Corporate Package",
            "description": "Corporate event package",
            "price_per_guest": "1500.00",
            "minimum_guests": 10,
            "maximum_guests": 100,
            "addon_ids": [venue.id]
        }

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_corporate_caterer_cannot_use_materials(self):

        materials = self.create_addon(
            self.other_caterer,
            "Decor Materials",
            "materials"
        )

        data = {
            "caterer_id": self.other_caterer.id,
            "package_name": "Corporate Package",
            "description": "Corporate event package",
            "price_per_guest": "1500.00",
            "minimum_guests": 10,
            "maximum_guests": 100,
            "addon_ids": [materials.id]
        }

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_food_caterer_cannot_add_non_food_components(self):

        chairs = self.create_addon(
            self.food_caterer,
            "Food Event Chairs",
            "chairs"
        )

        data = {
            "caterer_id": self.food_caterer.id,
            "package_name": "Food Package",
            "description": "Food only package",
            "price_per_guest": "1000.00",
            "minimum_guests": 5,
            "maximum_guests": 50,
            "addon_ids": [chairs.id]
        }

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.food_caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_caterer_cannot_use_another_caterers_addon(self):

        other_addon = self.create_addon(
            self.other_caterer,
            "Other Caterer Chairs",
            "chairs"
        )

        data = self.valid_package_data.copy()
        data["addon_ids"] = [other_addon.id]

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_caterer_can_update_package_addons(self):

        venue = self.create_addon(
            self.caterer,
            "Wedding Venue",
            "venue"
        )

        chairs = self.create_addon(
            self.caterer,
            "Wedding Chairs",
            "chairs"
        )

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"addon_ids": [venue.id, chairs.id]},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = {
            addon["id"]
            for addon in response.json["data"]["addons"]
        }

        self.assertEqual(
            returned_ids,
            {venue.id, chairs.id}
        )

    def test_caterer_can_clear_package_addons(self):

        venue = self.create_addon(
            self.caterer,
            "Wedding Venue",
            "venue"
        )

        initial_response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"addon_ids": [venue.id]},
            headers=self.caterer_headers
        )

        self.assertEqual(initial_response.status_code, 200)

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"addon_ids": []},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["addons"], [])
        self.assertEqual(response.json["data"]["addon_ids"], [])

    def test_duplicate_addon_ids_are_rejected(self):

        chairs = self.create_addon(
            self.caterer,
            "Wedding Chairs",
            "chairs"
        )

        data = self.valid_package_data.copy()
        data["addon_ids"] = [chairs.id, chairs.id]

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_addon_ids_are_rejected(self):

        data = self.valid_package_data.copy()
        data["addon_ids"] = [-1]

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_legacy_addon_without_type_cannot_be_package_component(self):

        legacy_addon = AddOn(
            caterer_id=self.caterer.id,
            addon_name="Waiter Service",
            description="Legacy standalone service",
            price=Decimal("8000.00"),
            addon_type=None
        )

        db.session.add(legacy_addon)
        db.session.commit()

        data = self.valid_package_data.copy()
        data["addon_ids"] = [legacy_addon.id]

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
