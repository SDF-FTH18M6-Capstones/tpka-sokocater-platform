
import unittest

from decimal import Decimal
from datetime import date

from marshmallow import ValidationError

from schemas import (
    CatererSchema,
    MenuSchema,
    PackageSchema,
    BookingSchema
)


class TestCatererSchema(unittest.TestCase):

    def setUp(self):
        self.schema = CatererSchema()

    def test_valid_caterer_data(self):
        data = {
            "user_id": 1,
            "business_name": "Kate Catering",
            "description": "Professional catering services",
            "location": "Nairobi",
            "contact_number": "0712345678"
        }

        result = self.schema.load(data)

        self.assertEqual(result["user_id"], 1)
        self.assertEqual(result["business_name"], "Kate Catering")

    def test_missing_business_name(self):
        data = {
            "user_id": 1,
            "location": "Nairobi",
            "contact_number": "0712345678"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_user_id(self):
        data = {
            "user_id": 0,
            "business_name": "Kate Catering",
            "location": "Nairobi",
            "contact_number": "0712345678"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)


class TestMenuSchema(unittest.TestCase):

    def setUp(self):
        self.schema = MenuSchema()

    def test_valid_menu_data(self):
        data = {
            "caterer_id": 1,
            "name": "Wedding Menu",
            "description": "A special wedding menu",
            "price": "500.00"
        }

        result = self.schema.load(data)

        self.assertEqual(result["caterer_id"], 1)
        self.assertEqual(result["name"], "Wedding Menu")
        self.assertEqual(result["price"], Decimal("500.00"))

    def test_missing_menu_name(self):
        data = {
            "caterer_id": 1,
            "description": "A special menu",
            "price": "500.00"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_caterer_id(self):
        data = {
            "caterer_id": 0,
            "name": "Wedding Menu",
            "price": "500.00"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_negative_menu_price(self):
        data = {
            "caterer_id": 1,
            "name": "Wedding Menu",
            "price": "-100.00"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)


class TestPackageSchema(unittest.TestCase):

    def setUp(self):
        self.schema = PackageSchema()

    def test_valid_package_data(self):
        data = {
            "caterer_id": 1,
            "name": "Premium Package",
            "category": "Wedding Catering",
            "description": "A premium catering package"
        }

        result = self.schema.load(data)

        self.assertEqual(result["caterer_id"], 1)
        self.assertEqual(result["name"], "Premium Package")
        self.assertEqual(result["category"], "Wedding Catering")

    def test_missing_package_name(self):
        data = {
            "caterer_id": 1,
            "category": "Wedding Catering"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_caterer_id(self):
        data = {
            "caterer_id": 0,
            "name": "Premium Package",
            "category": "Wedding Catering"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_package_category(self):
        data = {
            "caterer_id": 1,
            "name": "Premium Package",
            "category": "Invalid Category"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_all_valid_package_categories(self):

        categories = [
            "Food Catering",
            "Wedding Catering",
            "Corporate Events",
            "Private Parties"
        ]

        for category in categories:
            with self.subTest(category=category):
                data = {
                    "caterer_id": 1,
                    "name": "Test Package",
                    "category": category
                }

                result = self.schema.load(data)

                self.assertEqual(result["category"], category)


class TestBookingSchema(unittest.TestCase):

    def setUp(self):
        self.schema = BookingSchema()

    def valid_booking_data(self):
        return {
            "user_id": 1,
            "caterer_id": 2,
            "package_id": 3,
            "event_date": "2027-05-20",
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100,
            "price_per_person": "1500.00",
            "estimated_total": "150000.00"
        }

    def test_valid_booking_data(self):

        result = self.schema.load(self.valid_booking_data())

        self.assertEqual(result["user_id"], 1)
        self.assertEqual(result["caterer_id"], 2)
        self.assertEqual(result["package_id"], 3)
        self.assertEqual(result["event_type"], "Wedding")
        self.assertEqual(result["guest_count"], 100)

        self.assertEqual(
            result["price_per_person"],
            Decimal("1500.00")
        )

        self.assertEqual(
            result["estimated_total"],
            Decimal("150000.00")
        )

    def test_missing_user_id(self):

        data = self.valid_booking_data()
        del data["user_id"]

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_user_id(self):

        data = self.valid_booking_data()
        data["user_id"] = 0

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_caterer_id(self):

        data = self.valid_booking_data()
        data["caterer_id"] = 0

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_package_id(self):

        data = self.valid_booking_data()
        data["package_id"] = 0

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_guest_count(self):

        data = self.valid_booking_data()
        data["guest_count"] = 0

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_negative_price_per_person(self):

        data = self.valid_booking_data()
        data["price_per_person"] = "-100.00"

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_negative_estimated_total(self):

        data = self.valid_booking_data()
        data["estimated_total"] = "-100.00"

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_event_date(self):

        data = self.valid_booking_data()
        data["event_date"] = "not-a-date"

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_missing_event_type(self):

        data = self.valid_booking_data()
        del data["event_type"]

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_status_cannot_be_set_on_load(self):

        data = self.valid_booking_data()
        data["status"] = "completed"

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_status_is_not_in_load_result(self):

        result = self.schema.load(self.valid_booking_data())

        self.assertNotIn("status", result)

    def test_estimated_total_is_string_when_dumped(self):

        data = {
            "user_id": 1,
            "caterer_id": 2,
            "package_id": 3,
            "event_date": date(2027, 5, 20),
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100,
            "price_per_person": Decimal("1500.00"),
            "estimated_total": Decimal("150000.00"),
            "status": "pending"
        }

        result = self.schema.dump(data)

        self.assertEqual(result["estimated_total"], "150000.00")
        self.assertEqual(result["price_per_person"], "1500.00")


if __name__ == "__main__":
    unittest.main(verbosity=2)
