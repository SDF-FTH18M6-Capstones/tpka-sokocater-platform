
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
            "menu_name": "Wedding Menu",
            "description": "A special wedding menu"
        }

        result = self.schema.load(data)

        self.assertEqual(result["caterer_id"], 1)
        self.assertEqual(result["menu_name"], "Wedding Menu")

    def test_missing_menu_name(self):
        data = {
            "caterer_id": 1,
            "description": "A special menu"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_caterer_id(self):
        data = {
            "caterer_id": 0,
            "menu_name": "Wedding Menu"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)


class TestPackageSchema(unittest.TestCase):

    def setUp(self):
        self.schema = PackageSchema()

    def test_valid_package_data(self):
        data = {
            "caterer_id": 1,
            "package_name": "Premium Package",
            "description": "A premium catering package",
            "price_per_guest": "1500.00",
            "minimum_guests": 20,
            "maximum_guests": 100
        }

        result = self.schema.load(data)

        self.assertEqual(result["caterer_id"], 1)
        self.assertEqual(result["package_name"], "Premium Package")

    def test_missing_package_name(self):
        data = {
            "caterer_id": 1,
            "price_per_guest": "1500.00",
            "minimum_guests": 20
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_price_per_guest(self):
        data = {
            "caterer_id": 1,
            "package_name": "Premium Package",
            "price_per_guest": "0",
            "minimum_guests": 20
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_maximum_guests_less_than_minimum(self):
        data = {
            "caterer_id": 1,
            "package_name": "Premium Package",
            "price_per_guest": "1500.00",
            "minimum_guests": 50,
            "maximum_guests": 20
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)


class TestBookingSchema(unittest.TestCase):

    def setUp(self):
        self.schema = BookingSchema()

    def test_valid_booking_data(self):
        data = {
            "customer_id": 1,
            "caterer_id": 2,
            "event_date": "2027-05-20",
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100,
            "estimated_total": "150000.00"
        }

        result = self.schema.load(data)

        self.assertEqual(result["customer_id"], 1)
        self.assertEqual(result["caterer_id"], 2)
        self.assertEqual(result["event_type"], "Wedding")
        self.assertEqual(result["guest_count"], 100)
        self.assertEqual(
            result["estimated_total"],
            Decimal("150000.00")
        )

    def test_missing_customer_id(self):
        data = {
            "caterer_id": 2,
            "event_date": "2027-05-20",
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100,
            "estimated_total": "150000.00"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_customer_id(self):
        data = {
            "customer_id": 0,
            "caterer_id": 2,
            "event_date": "2027-05-20",
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100,
            "estimated_total": "150000.00"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_caterer_id(self):
        data = {
            "customer_id": 1,
            "caterer_id": 0,
            "event_date": "2027-05-20",
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100,
            "estimated_total": "150000.00"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_guest_count(self):
        data = {
            "customer_id": 1,
            "caterer_id": 2,
            "event_date": "2027-05-20",
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 0,
            "estimated_total": "150000.00"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_negative_estimated_total(self):
        data = {
            "customer_id": 1,
            "caterer_id": 2,
            "event_date": "2027-05-20",
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100,
            "estimated_total": "-100.00"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_event_date(self):
        data = {
            "customer_id": 1,
            "caterer_id": 2,
            "event_date": "not-a-date",
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100,
            "estimated_total": "150000.00"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_missing_event_type(self):
        data = {
            "customer_id": 1,
            "caterer_id": 2,
            "event_date": "2027-05-20",
            "event_location": "Nairobi",
            "guest_count": 100,
            "estimated_total": "150000.00"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_status_cannot_be_set_on_load(self):
        data = {
            "customer_id": 1,
            "caterer_id": 2,
            "event_date": "2027-05-20",
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100,
            "estimated_total": "150000.00",
            "status": "completed"
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_status_is_not_in_load_result(self):
        data = {
            "customer_id": 1,
            "caterer_id": 2,
            "event_date": "2027-05-20",
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100,
            "estimated_total": "150000.00"
        }

        result = self.schema.load(data)

        self.assertNotIn("status", result)

    def test_estimated_total_is_string_when_dumped(self):
        data = {
            "customer_id": 1,
            "caterer_id": 2,
            "event_date": date(2027, 5, 20),
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100,
            "estimated_total": Decimal("150000.00"),
            "status": "pending"
        }

        result = self.schema.dump(data)

        self.assertEqual(result["estimated_total"], "150000.00")


if __name__ == "__main__":
    unittest.main()
