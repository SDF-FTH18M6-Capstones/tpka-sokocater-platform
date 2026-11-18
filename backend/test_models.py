
import unittest

from datetime import date
from decimal import Decimal

from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app import create_app
from extensions import db

from models import (
    User,
    Caterer,
    Menu,
    Package,
    Booking,
    Order
)


class TestSokoCaterModels(unittest.TestCase):

    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False
        })

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --------------------------------------------------
    # HELPER: Create a sample user and caterer
    # --------------------------------------------------

    def create_sample_caterer(self):

        user = User(
            full_name="Kate Caterer",
            email="kate@example.com",
            password_hash="hashed_password",
            phone="0712345678",
            role="caterer"
        )

        db.session.add(user)
        db.session.flush()

        caterer = Caterer(
            user_id=user.id,
            business_name="Kate's Catering",
            location="Nairobi",
            description="Professional catering services",
            contact_number="0712345678"
        )

        db.session.add(caterer)
        db.session.flush()

        return user, caterer

    # --------------------------------------------------
    # TEST 1: All six models can be imported
    # --------------------------------------------------

    def test_all_models_imported(self):

        model_classes = [
            User,
            Caterer,
            Menu,
            Package,
            Booking,
            Order
        ]

        self.assertEqual(len(model_classes), 6)

    # --------------------------------------------------
    # TEST 2: Exactly six database tables are created
    # --------------------------------------------------

    def test_all_tables_created(self):

        inspector = inspect(db.engine)

        expected_tables = {
            "users",
            "caterers",
            "menus",
            "packages",
            "bookings",
            "orders"
        }

        actual_tables = set(inspector.get_table_names())

        self.assertEqual(actual_tables, expected_tables)

    # --------------------------------------------------
    # TEST 3: Model relationships work correctly
    # --------------------------------------------------

    def test_model_relationships(self):

        user, caterer = self.create_sample_caterer()

        menu = Menu(
            caterer_id=caterer.id,
            name="Wedding Menu",
            description="Wedding food selection",
            price=Decimal("500.00")
        )

        package = Package(
            caterer_id=caterer.id,
            name="Wedding Package",
            category="Wedding Catering",
            description="Complete wedding catering package"
        )

        db.session.add_all([menu, package])
        db.session.flush()

        customer = User(
            full_name="Test Customer",
            email="customer@example.com",
            password_hash="hashed_password",
            phone="0798765432",
            role="customer"
        )

        db.session.add(customer)
        db.session.flush()

        booking = Booking(
            user_id=customer.id,
            caterer_id=caterer.id,
            package_id=package.id,
            event_type="Wedding",
            event_date=date(2027, 5, 20),
            event_location="Nairobi",
            guest_count=100,
            price_per_person=Decimal("1500.00"),
            estimated_total=Decimal("150000.00"),
            status="pending"
        )

        order = Order(
            user_id=customer.id,
            caterer_id=caterer.id,
            menu_id=menu.id,
            quantity=2,
            unit_price=Decimal("500.00"),
            total_amount=Decimal("1000.00"),
            status="pending"
        )

        db.session.add_all([booking, order])
        db.session.commit()

        # User and caterer relationship
        self.assertEqual(user.caterer.id, caterer.id)
        self.assertEqual(caterer.user.id, user.id)

        # Caterer and menu relationship
        self.assertEqual(caterer.menus[0].name, "Wedding Menu")
        self.assertEqual(menu.caterer.id, caterer.id)

        # Caterer and package relationship
        self.assertEqual(caterer.packages[0].name, "Wedding Package")
        self.assertEqual(package.caterer.id, caterer.id)

        # Customer and booking relationship
        self.assertEqual(customer.bookings[0].id, booking.id)
        self.assertEqual(booking.user.id, customer.id)

        # Booking and package relationship
        self.assertEqual(booking.package.id, package.id)

        # Booking and caterer relationship
        self.assertEqual(booking.caterer.id, caterer.id)

        # Customer and order relationship
        self.assertEqual(customer.orders[0].id, order.id)
        self.assertEqual(order.user.id, customer.id)

        # Order and menu relationship
        self.assertEqual(order.menu.id, menu.id)

        # Order and caterer relationship
        self.assertEqual(order.caterer.id, caterer.id)

    # --------------------------------------------------
    # TEST 4: Foreign keys reject invalid references
    # --------------------------------------------------

    def test_foreign_key_constraint(self):

        invalid_menu = Menu(
            caterer_id=9999,
            name="Invalid Menu",
            description="Menu with invalid caterer",
            price=Decimal("500.00")
        )

        db.session.add(invalid_menu)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 5: User email must be unique
    # --------------------------------------------------

    def test_unique_email_constraint(self):

        user1 = User(
            full_name="First User",
            email="same@example.com",
            password_hash="hashed_password",
            role="customer"
        )

        user2 = User(
            full_name="Second User",
            email="same@example.com",
            password_hash="hashed_password",
            role="customer"
        )

        db.session.add(user1)
        db.session.commit()

        db.session.add(user2)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 6: A user cannot have multiple caterer profiles
    # --------------------------------------------------

    def test_one_caterer_per_user(self):

        user, caterer = self.create_sample_caterer()

        second_caterer = Caterer(
            user_id=user.id,
            business_name="Another Catering Business",
            location="Nairobi",
            contact_number="0700000000"
        )

        db.session.add(second_caterer)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 7: Invalid package categories are rejected
    # --------------------------------------------------

    def test_invalid_package_category_rejected(self):

        user, caterer = self.create_sample_caterer()

        package = Package(
            caterer_id=caterer.id,
            name="Invalid Package",
            category="Invalid Category"
        )

        db.session.add(package)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 8: Booking guest count must be positive
    # --------------------------------------------------

    def test_invalid_booking_guest_count_rejected(self):

        user, caterer = self.create_sample_caterer()

        package = Package(
            caterer_id=caterer.id,
            name="Birthday Package",
            category="Private Parties"
        )

        db.session.add(package)
        db.session.flush()

        customer = User(
            full_name="Customer",
            email="booking@example.com",
            password_hash="hashed_password",
            role="customer"
        )

        db.session.add(customer)
        db.session.flush()

        booking = Booking(
            user_id=customer.id,
            caterer_id=caterer.id,
            package_id=package.id,
            event_type="Birthday",
            event_date=date(2027, 6, 10),
            event_location="Nairobi",
            guest_count=0,
            price_per_person=Decimal("1000.00"),
            estimated_total=Decimal("0.00"),
            status="pending"
        )

        db.session.add(booking)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 9: Order quantity must be positive
    # --------------------------------------------------

    def test_invalid_order_quantity_rejected(self):

        user, caterer = self.create_sample_caterer()

        menu = Menu(
            caterer_id=caterer.id,
            name="Lunch Menu",
            price=Decimal("500.00")
        )

        db.session.add(menu)
        db.session.flush()

        customer = User(
            full_name="Order Customer",
            email="order@example.com",
            password_hash="hashed_password",
            role="customer"
        )

        db.session.add(customer)
        db.session.flush()

        order = Order(
            user_id=customer.id,
            caterer_id=caterer.id,
            menu_id=menu.id,
            quantity=0,
            unit_price=Decimal("500.00"),
            total_amount=Decimal("0.00"),
            status="pending"
        )

        db.session.add(order)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()


if __name__ == "__main__":
    unittest.main(verbosity=2)
