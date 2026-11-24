import unittest
from datetime import date
from decimal import Decimal

from app import create_app
from extensions import db
from models import (
    User,
    CatererProfile,
    Booking,
    Review
)
from flask_jwt_extended import create_access_token


class TestReviewRoutes(unittest.TestCase):

    def setUp(self):

        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "JWT_SECRET_KEY": "sokocater-review-test-secret-2026"
        })

        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        self.customer1 = User(
            full_name="Customer One",
            email="customer1@example.com",
            password_hash="test-password",
            role="customer"
        )

        self.customer2 = User(
            full_name="Customer Two",
            email="customer2@example.com",
            password_hash="test-password",
            role="customer"
        )

        self.caterer_user = User(
            full_name="Caterer One",
            email="caterer@example.com",
            password_hash="test-password",
            role="caterer"
        )

        db.session.add_all([
            self.customer1,
            self.customer2,
            self.caterer_user
        ])

        db.session.commit()

        self.caterer = CatererProfile(
            user_id=self.caterer_user.id,
            business_name="Test Catering",
            location="Nairobi",
            verification_status="approved",
            category="Food"
        )

        db.session.add(self.caterer)
        db.session.commit()

        self.customer1_token = create_access_token(
            identity=str(self.customer1.id),
            additional_claims={"role": "customer"}
        )

        self.customer2_token = create_access_token(
            identity=str(self.customer2.id),
            additional_claims={"role": "customer"}
        )

        self.caterer_token = create_access_token(
            identity=str(self.caterer_user.id),
            additional_claims={"role": "caterer"}
        )

        self.customer1_headers = {
            "Authorization": f"Bearer {self.customer1_token}"
        }

        self.customer2_headers = {
            "Authorization": f"Bearer {self.customer2_token}"
        }

        self.caterer_headers = {
            "Authorization": f"Bearer {self.caterer_token}"
        }

        self.completed_booking = self.create_booking(
            customer=self.customer1,
            status="completed"
        )

        self.pending_booking = self.create_booking(
            customer=self.customer1,
            status="pending"
        )

        self.other_customer_booking = self.create_booking(
            customer=self.customer2,
            status="completed"
        )

    def create_booking(self, customer, status):

        booking = Booking(
            customer_id=customer.id,
            caterer_id=self.caterer.id,
            event_date=date(2026, 12, 15),
            event_type="Food",
            event_location="Nairobi",
            guest_count=20,
            estimated_total=Decimal("10000.00"),
            status=status
        )

        db.session.add(booking)
        db.session.commit()

        return booking

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --------------------------------------------------
    # CREATE REVIEWS
    # --------------------------------------------------

    def test_customer_can_review_completed_booking(self):

        response = self.client.post(
            "/api/reviews",
            json={
                "booking_id": self.completed_booking.id,
                "rating": 5,
                "comment": "Excellent catering service!"
            },
            headers=self.customer1_headers
        )

        self.assertEqual(response.status_code, 201)

        data = response.get_json()["data"]

        self.assertEqual(data["rating"], 5)
        self.assertEqual(
            data["booking_id"],
            self.completed_booking.id
        )
        self.assertEqual(
            data["caterer_id"],
            self.caterer.id
        )

        review = Review.query.filter_by(
            booking_id=self.completed_booking.id
        ).first()

        self.assertIsNotNone(review)

    def test_customer_can_submit_review_without_comment(self):

        response = self.client.post(
            "/api/reviews",
            json={
                "booking_id": self.completed_booking.id,
                "rating": 4
            },
            headers=self.customer1_headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.get_json()["data"]["comment"])

    def test_customer_cannot_review_another_customers_booking(self):

        response = self.client.post(
            "/api/reviews",
            json={
                "booking_id": self.other_customer_booking.id,
                "rating": 5,
                "comment": "Great service"
            },
            headers=self.customer1_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_customer_cannot_review_incomplete_booking(self):

        response = self.client.post(
            "/api/reviews",
            json={
                "booking_id": self.pending_booking.id,
                "rating": 5
            },
            headers=self.customer1_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_caterer_cannot_submit_review(self):

        response = self.client.post(
            "/api/reviews",
            json={
                "booking_id": self.completed_booking.id,
                "rating": 5
            },
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_review_requires_authentication(self):

        response = self.client.post(
            "/api/reviews",
            json={
                "booking_id": self.completed_booking.id,
                "rating": 5
            }
        )

        self.assertEqual(response.status_code, 401)

    def test_review_rejects_invalid_rating(self):

        for rating in [0, 6, -1, True, "5", 4.5]:

            with self.subTest(rating=rating):

                response = self.client.post(
                    "/api/reviews",
                    json={
                        "booking_id": self.completed_booking.id,
                        "rating": rating
                    },
                    headers=self.customer1_headers
                )

                self.assertEqual(response.status_code, 400)

    def test_review_rejects_invalid_booking_id(self):

        for booking_id in [0, -1, True, "1", 1.5]:

            with self.subTest(booking_id=booking_id):

                response = self.client.post(
                    "/api/reviews",
                    json={
                        "booking_id": booking_id,
                        "rating": 5
                    },
                    headers=self.customer1_headers
                )

                self.assertEqual(response.status_code, 400)

    def test_review_rejects_invalid_comment(self):

        response = self.client.post(
            "/api/reviews",
            json={
                "booking_id": self.completed_booking.id,
                "rating": 5,
                "comment": 123
            },
            headers=self.customer1_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_review_rejects_client_supplied_caterer_id(self):

        response = self.client.post(
            "/api/reviews",
            json={
                "booking_id": self.completed_booking.id,
                "rating": 5,
                "caterer_id": self.caterer.id
            },
            headers=self.customer1_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_customer_cannot_review_same_booking_twice(self):

        payload = {
            "booking_id": self.completed_booking.id,
            "rating": 5,
            "comment": "Excellent"
        }

        first_response = self.client.post(
            "/api/reviews",
            json=payload,
            headers=self.customer1_headers
        )

        second_response = self.client.post(
            "/api/reviews",
            json=payload,
            headers=self.customer1_headers
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 409)

        self.assertEqual(
            Review.query.filter_by(
                booking_id=self.completed_booking.id
            ).count(),
            1
        )

    def test_nonexistent_booking_returns_404(self):

        response = self.client.post(
            "/api/reviews",
            json={
                "booking_id": 9999,
                "rating": 5
            },
            headers=self.customer1_headers
        )

        self.assertEqual(response.status_code, 404)

    # --------------------------------------------------
    # GET CATERER REVIEWS
    # --------------------------------------------------

    def test_public_can_get_caterer_reviews(self):

        db.session.add(
            Review(
                customer_id=self.customer1.id,
                caterer_id=self.caterer.id,
                booking_id=self.completed_booking.id,
                rating=5,
                comment="Excellent service"
            )
        )

        db.session.commit()

        response = self.client.get(
            f"/api/caterers/{self.caterer.id}/reviews"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["total_reviews"], 1)
        self.assertEqual(data["data"][0]["rating"], 5)

    def test_caterer_with_no_reviews_returns_empty_list(self):

        response = self.client.get(
            f"/api/caterers/{self.caterer.id}/reviews"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["total_reviews"], 0)
        self.assertEqual(response.get_json()["data"], [])

    def test_nonexistent_caterer_reviews_returns_404(self):

        response = self.client.get(
            "/api/caterers/9999/reviews"
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
