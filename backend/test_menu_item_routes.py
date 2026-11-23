
import unittest
from decimal import Decimal

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from models import User, Caterer, Menu, MenuItem, Package, PackageItem


class TestMenuItemRoutes(unittest.TestCase):

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

        self.caterer = self.create_caterer(self.caterer_user)
        self.other_caterer = self.create_caterer(
            self.other_caterer_user,
            "Other Catering Business"
        )

        self.menu = self.create_menu(self.caterer)
        self.other_menu = self.create_menu(self.other_caterer)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

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

    def create_caterer(self, user, business_name="Fresh Foods Catering"):

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

    def create_menu(self, caterer):

        menu = Menu(
            caterer_id=caterer.id,
            menu_name="Wedding Menu",
            description="Wedding food selection"
        )

        db.session.add(menu)
        db.session.commit()

        return menu

    def create_menu_item(self, menu=None):

        if menu is None:
            menu = self.menu

        item = MenuItem(
            menu_id=menu.id,
            item_name="Chicken",
            description="Roasted chicken",
            price=Decimal("500.00")
        )

        db.session.add(item)
        db.session.commit()

        return item

    def create_token(self, user):

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )

        return {"Authorization": f"Bearer {token}"}

    def valid_item_data(self, menu=None):

        if menu is None:
            menu = self.menu

        return {
            "menu_id": menu.id,
            "item_name": "Grilled Chicken",
            "description": "Freshly grilled chicken",
            "price": "750.00",
            "image_url": "https://example.com/chicken.jpg"
        }

    # --------------------------------------------------
    # PUBLIC GET ROUTES
    # --------------------------------------------------

    def test_get_all_menu_items_successful(self):

        self.create_menu_item()

        response = self.client.get("/api/menu-items")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["data"]), 1)

    def test_get_all_menu_items_without_token(self):

        response = self.client.get("/api/menu-items")

        self.assertEqual(response.status_code, 200)

    def test_get_single_menu_item_successful(self):

        item = self.create_menu_item()

        response = self.client.get(
            f"/api/menu-items/{item.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["data"]["item_name"],
            "Chicken"
        )

    def test_get_nonexistent_menu_item(self):

        response = self.client.get("/api/menu-items/999")

        self.assertEqual(response.status_code, 404)

    # --------------------------------------------------
    # CREATE MENU ITEM
    # --------------------------------------------------

    def test_create_menu_item_successful(self):

        response = self.client.post(
            "/api/menu-items",
            json=self.valid_item_data(),
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.get_json()["data"]["item_name"],
            "Grilled Chicken"
        )

    def test_create_menu_item_without_token(self):

        response = self.client.post(
            "/api/menu-items",
            json=self.valid_item_data()
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_create_menu_item(self):

        response = self.client.post(
            "/api/menu-items",
            json=self.valid_item_data(),
            headers=self.create_token(self.customer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_without_profile_cannot_create_menu_item(self):

        response = self.client.post(
            "/api/menu-items",
            json=self.valid_item_data(),
            headers=self.create_token(self.no_profile_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_add_item_to_another_caterers_menu(self):

        response = self.client.post(
            "/api/menu-items",
            json=self.valid_item_data(self.other_menu),
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_create_menu_item_with_nonexistent_menu(self):

        data = self.valid_item_data()
        data["menu_id"] = 999

        response = self.client.post(
            "/api/menu-items",
            json=data,
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 404)

    def test_create_menu_item_with_invalid_price(self):

        data = self.valid_item_data()
        data["price"] = "-100.00"

        response = self.client.post(
            "/api/menu-items",
            json=data,
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_create_menu_item_with_missing_name(self):

        data = self.valid_item_data()
        del data["item_name"]

        response = self.client.post(
            "/api/menu-items",
            json=data,
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_create_menu_item_with_whitespace_name(self):

        data = self.valid_item_data()
        data["item_name"] = "   "

        response = self.client.post(
            "/api/menu-items",
            json=data,
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_create_menu_item_without_json(self):

        response = self.client.post(
            "/api/menu-items",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------
    # UPDATE MENU ITEM
    # --------------------------------------------------

    def test_update_own_menu_item_successful(self):

        item = self.create_menu_item()

        response = self.client.put(
            f"/api/menu-items/{item.id}",
            json={"item_name": "Updated Chicken"},
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["data"]["item_name"],
            "Updated Chicken"
        )

    def test_update_menu_item_without_token(self):

        item = self.create_menu_item()

        response = self.client.put(
            f"/api/menu-items/{item.id}",
            json={"item_name": "Updated Chicken"}
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_update_menu_item(self):

        item = self.create_menu_item()

        response = self.client.put(
            f"/api/menu-items/{item.id}",
            json={"item_name": "Unauthorized"},
            headers=self.create_token(self.customer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_update_another_caterers_item(self):

        item = self.create_menu_item(self.other_menu)

        response = self.client.put(
            f"/api/menu-items/{item.id}",
            json={"item_name": "Unauthorized"},
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_update_nonexistent_menu_item(self):

        response = self.client.put(
            "/api/menu-items/999",
            json={"item_name": "Updated Chicken"},
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 404)

    def test_update_menu_item_with_empty_body(self):

        item = self.create_menu_item()

        response = self.client.put(
            f"/api/menu-items/{item.id}",
            json={},
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_update_menu_item_with_invalid_price(self):

        item = self.create_menu_item()

        response = self.client.put(
            f"/api/menu-items/{item.id}",
            json={"price": "-50.00"},
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_caterer_cannot_transfer_item_to_another_menu(self):

        item = self.create_menu_item()

        response = self.client.put(
            f"/api/menu-items/{item.id}",
            json={"menu_id": self.other_menu.id},
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    # --------------------------------------------------
    # DELETE MENU ITEM
    # --------------------------------------------------

    def test_delete_own_menu_item_successful(self):

        item = self.create_menu_item()

        response = self.client.delete(
            f"/api/menu-items/{item.id}",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(db.session.get(MenuItem, item.id))

    def test_delete_menu_item_without_token(self):

        item = self.create_menu_item()

        response = self.client.delete(
            f"/api/menu-items/{item.id}"
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_delete_menu_item(self):

        item = self.create_menu_item()

        response = self.client.delete(
            f"/api/menu-items/{item.id}",
            headers=self.create_token(self.customer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_delete_another_caterers_item(self):

        item = self.create_menu_item(self.other_menu)

        response = self.client.delete(
            f"/api/menu-items/{item.id}",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_nonexistent_menu_item(self):

        response = self.client.delete(
            "/api/menu-items/999",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_menu_item_used_in_package(self):

        item = self.create_menu_item()

        package = Package(
            caterer_id=self.caterer.id,
            package_name="Wedding Package",
            description="Wedding catering",
            price_per_guest=Decimal("1500.00"),
            minimum_guests=20,
            maximum_guests=200
        )

        db.session.add(package)
        db.session.flush()

        package_item = PackageItem(
            package_id=package.id,
            menu_item_id=item.id
        )

        db.session.add(package_item)
        db.session.commit()

        response = self.client.delete(
            f"/api/menu-items/{item.id}",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 409)

        self.assertIsNotNone(
            db.session.get(MenuItem, item.id)
        )


if __name__ == "__main__":
    unittest.main()
