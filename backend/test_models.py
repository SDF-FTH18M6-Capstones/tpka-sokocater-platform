
import unittest

from datetime import date
from decimal import Decimal

from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app import create_app
from extensions import db

# Import all 13 models
from models import (
    User,
    CatererProfile,
    Menu,
    MenuItem,
    Package,
    PackageItem,
    AddOn,
    Booking,
    BookingItem,
    Availability,
    Payment,
    Review,
    Notification
)


class TestSokoCaterModels(unittest.TestCase):

    def setUp(self):

        # Create a temporary testing application
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False
        })

        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create all database tables
        db.create_all()

    def tearDown(self):

        # Remove test records and tables
        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    # --------------------------------------------------
    # TEST 1: All 13 models can be imported
    # --------------------------------------------------

    def test_all_models_imported(self):

        model_classes = [
            User,
            CatererProfile,
            Menu,
            MenuItem,
            Package,
            PackageItem,
            AddOn,
            Booking,
            BookingItem,
            Availability,
            Payment,
            Review,
            Notification
        ]

        self.assertEqual(len(model_classes), 13)

        print("\nAll 13 models imported successfully.")

    # --------------------------------------------------
    # TEST 2: All 13 database tables can be created
    # --------------------------------------------------

    def test_all_tables_created(self):

        inspector = inspect(db.engine)

        expected_tables = {
            "users",
            "caterer_profiles",
            "menus",
            "menu_items",
            "packages",
            "package_items",
            "add_ons",
            "bookings",
            "booking_items",
            "availability",
            "payments",
            "reviews",
            "notifications"
        }

        actual_tables = set(inspector.get_table_names())

        self.assertEqual(actual_tables, expected_tables)

        print("\nAll 13 database tables created successfully.")

    # --------------------------------------------------
    # HELPER: Create sample user and caterer
    # --------------------------------------------------

    def create_sample_caterer(self):

        user = User(
            full_name="Kate Caterer",
            email="kate@example.com",
            password_hash="hashed_password",
            role="caterer"
        )

        db.session.add(user)
        db.session.flush()

        caterer = CatererProfile(
            user_id=user.id,
            business_name="Kate's Catering",
            location="Nairobi",
            verification_status="pending"
        )

        db.session.add(caterer)
        db.session.flush()

        return user, caterer

    # --------------------------------------------------
    # TEST 3: Relationships return correct records
    # --------------------------------------------------

    def test_model_relationships(self):

        user, caterer = self.create_sample_caterer()

        menu = Menu(
            caterer_id=caterer.id,
            menu_name="Wedding Menu"
        )

        db.session.add(menu)
        db.session.flush()

        menu_item = MenuItem(
            menu_id=menu.id,
            item_name="Chicken",
            price=Decimal("500.00")
        )

        db.session.add(menu_item)
        db.session.flush()

        package = Package(
            caterer_id=caterer.id,
            package_name="Wedding Package",
            price_per_guest=Decimal("1500.00"),
            minimum_guests=50,
            maximum_guests=200
        )

        db.session.add(package)
        db.session.flush()

        package_item = PackageItem(
            package_id=package.id,
            menu_item_id=menu_item.id
        )

        db.session.add(package_item)

        customer = User(
            full_name="Test Customer",
            email="customer@example.com",
            password_hash="hashed_password",
            role="customer"
        )

        db.session.add(customer)
        db.session.flush()

        booking = Booking(
            customer_id=customer.id,
            caterer_id=caterer.id,
            event_date=date(2027, 5, 20),
            event_type="Wedding",
            event_location="Nairobi",
            guest_count=100,
            estimated_total=Decimal("150000.00"),
            status="pending"
        )

        db.session.add(booking)
        db.session.flush()

        db.session.add(
            BookingItem(
                booking_id=booking.id,
                package_id=package.id,
                quantity=100,
                unit_price=Decimal("1500.00")
            )
        )

        db.session.add(
            Availability(
                caterer_id=caterer.id,
                available_date=date(2027, 5, 20),
                status="available"
            )
        )

        db.session.add(
            Payment(
                booking_id=booking.id,
                amount=Decimal("50000.00"),
                payment_method="M-Pesa",
                payment_status="pending"
            )
        )

        db.session.add(
            Review(
                customer_id=customer.id,
                caterer_id=caterer.id,
                booking_id=booking.id,
                rating=5,
                comment="Excellent service"
            )
        )

        db.session.add(
            Notification(
                user_id=customer.id,
                message="Your booking was received",
                notification_type="booking",
                is_read=False
            )
        )

        db.session.commit()

        # Verify relationships
        self.assertEqual(user.caterer_profile.id, caterer.id)

        self.assertEqual(caterer.menus[0].menu_name, "Wedding Menu")

        self.assertEqual(menu.menu_items[0].item_name, "Chicken")

        self.assertEqual(package.package_items[0].menu_item.id, menu_item.id)

        self.assertEqual(booking.customer.id, customer.id)

        self.assertEqual(booking.caterer.id, caterer.id)

        self.assertEqual(len(booking.booking_items), 1)

        self.assertEqual(len(booking.payments), 1)

        self.assertEqual(booking.review.rating, 5)

        self.assertEqual(len(customer.notifications), 1)

        print("\nModel relationships work correctly.")

    # --------------------------------------------------
    # TEST 4: Foreign keys reject invalid references
    # --------------------------------------------------

    def test_foreign_key_constraint(self):

        invalid_menu = Menu(
            caterer_id=9999,
            menu_name="Invalid Menu"
        )

        db.session.add(invalid_menu)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        print("\nForeign key constraints work correctly.")

    # --------------------------------------------------
    # TEST 5: Unique email constraint
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

        print("\nUnique email constraint works correctly.")

    # --------------------------------------------------
    # TEST 6: Rating must be between 1 and 5
    # --------------------------------------------------

    def test_invalid_rating_rejected(self):

        user, caterer = self.create_sample_caterer()

        customer = User(
            full_name="Customer",
            email="rating@example.com",
            password_hash="hashed_password",
            role="customer"
        )

        db.session.add(customer)
        db.session.flush()

        booking = Booking(
            customer_id=customer.id,
            caterer_id=caterer.id,
            event_date=date(2027, 6, 10),
            event_type="Birthday",
            event_location="Nairobi",
            guest_count=50,
            estimated_total=Decimal("50000.00"),
            status="completed"
        )

        db.session.add(booking)
        db.session.flush()

        review = Review(
            customer_id=customer.id,
            caterer_id=caterer.id,
            booking_id=booking.id,
            rating=6
        )

        db.session.add(review)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        print("\nInvalid review ratings are rejected.")

    # --------------------------------------------------
    # TEST 7: BookingItem must select package OR add-on
    # --------------------------------------------------

    def test_booking_item_constraint(self):

        user, caterer = self.create_sample_caterer()

        customer = User(
            full_name="Customer",
            email="booking@example.com",
            password_hash="hashed_password",
            role="customer"
        )

        db.session.add(customer)
        db.session.flush()

        booking = Booking(
            customer_id=customer.id,
            caterer_id=caterer.id,
            event_date=date(2027, 7, 15),
            event_type="Birthday",
            event_location="Nairobi",
            guest_count=30,
            estimated_total=Decimal("30000.00"),
            status="pending"
        )

        db.session.add(booking)
        db.session.flush()

        invalid_item = BookingItem(
            booking_id=booking.id,
            package_id=None,
            addon_id=None,
            quantity=1,
            unit_price=Decimal("1000.00")
        )

        db.session.add(invalid_item)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        print("\nBooking item selection constraint works correctly.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
