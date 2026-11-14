
import unittest

from marshmallow import ValidationError
from schemas import CatererSchema, MenuSchema, PackageSchema


class TestCatererSchema(unittest.TestCase):

    def setUp(self):
        self.schema = CatererSchema()

    def test_valid_caterer_data(self):
        data = {
            "user_id": 1,
            "business_name": "Kate's Catering",
            "description": "Professional catering services",
            "location": "Nairobi",
            "contact_number": "0712345678",
            "business_image": "https://example.com/image.jpg"
        }

        result = self.schema.load(data)

        self.assertEqual(result["business_name"], "Kate's Catering")
        self.assertEqual(result["user_id"], 1)

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
            "business_name": "Kate's Catering",
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
            "description": "Wedding food selection"
        }

        result = self.schema.load(data)

        self.assertEqual(result["menu_name"], "Wedding Menu")
        self.assertEqual(result["caterer_id"], 1)

    def test_missing_menu_name(self):
        data = {
            "caterer_id": 1,
            "description": "Wedding food selection"
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
            "package_name": "Wedding Package",
            "description": "Premium wedding catering",
            "price_per_guest": "1500.00",
            "minimum_guests": 50,
            "maximum_guests": 300
        }

        result = self.schema.load(data)

        self.assertEqual(result["package_name"], "Wedding Package")
        self.assertEqual(result["minimum_guests"], 50)

    def test_negative_price(self):
        data = {
            "caterer_id": 1,
            "package_name": "Wedding Package",
            "price_per_guest": "-100",
            "minimum_guests": 50
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_maximum_guests_less_than_minimum(self):
        data = {
            "caterer_id": 1,
            "package_name": "Wedding Package",
            "price_per_guest": "1500.00",
            "minimum_guests": 100,
            "maximum_guests": 50
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_missing_package_name(self):
        data = {
            "caterer_id": 1,
            "price_per_guest": "1500.00",
            "minimum_guests": 50
        }

        with self.assertRaises(ValidationError):
            self.schema.load(data)


if __name__ == "__main__":
    unittest.main()
