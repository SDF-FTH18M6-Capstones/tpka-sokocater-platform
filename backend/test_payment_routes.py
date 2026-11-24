
import unittest
from datetime import date
from decimal import Decimal

from app import create_app
from extensions import db
from models import User, Caterer, Package, Booking, Payment
from flask_jwt_extended import create_access_token


class TestPaymentRoutes(unittest.TestCase):

    def setUp(self):

        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "JWT_SECRET_KEY": "sokocater-payment-test-secret-2026"
        })

        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create users.
        self.customer = User(
            full_name="Test Customer",
            email="customer@test.com",
            password_hash="hashedpassword",
            role="customer"
        )

        self.other_customer = User(
            full_name="Other Customer",
            email="othercustomer@test.com",
            password_hash="hashedpassword",
            role="customer"
        )

        self.caterer_user = User(
            full_name="Test Caterer",
            email="caterer@test.com",
            password_hash="hashedpassword",
            role="caterer"
        )

        db.session.add_all([
            self.customer,
            self.other_customer,
            self.caterer_user
        ])
        db.session.commit()

        # Create caterer profile.
        self.caterer = Caterer(
            user_id=self.caterer_user.id,
            business_name="Test Catering",
            location="Nairobi",
            verification_status="pending"
        )

        db.session.add(self.caterer)
        db.session.commit()

        # Create package.
        self.package = Package(
            caterer_id=self.caterer.id,
            package_name="Wedding Package",
            description="Wedding catering package",
            price_per_guest=Decimal("1500.00"),
            minimum_guests=20,
            maximum_guests=200
        )

        db.session.add(self.package)
        db.session.commit()

        # Create an accepted booking so payment is allowed.
        self.booking = Booking(
            customer_id=self.customer.id,
            caterer_id=self.caterer.id,
            event_date=date(2027, 6, 15),
            event_type="Wedding",
            event_location="Nairobi",
            guest_count=50,
            estimated_total=Decimal("75000.00"),
            status="accepted"
        )

        db.session.add(self.booking)
        db.session.commit()

        # Create authentication tokens.
        self.customer_token = create_access_token(
            identity=str(self.customer.id),
            additional_claims={"role": "customer"}
        )

        self.other_customer_token = create_access_token(
            identity=str(self.other_customer.id),
            additional_claims={"role": "customer"}
        )

        self.caterer_token = create_access_token(
            identity=str(self.caterer_user.id),
            additional_claims={"role": "caterer"}
        )

        self.customer_headers = {
            "Authorization": f"Bearer {self.customer_token}"
        }

        self.other_customer_headers = {
            "Authorization": f"Bearer {self.other_customer_token}"
        }

        self.caterer_headers = {
            "Authorization": f"Bearer {self.caterer_token}"
        }

        self.valid_payment_data = {
            "booking_id": self.booking.id,
            "payment_method": "M-Pesa"
        }

    def tearDown(self):

        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    def create_payment(self, status="pending"):

        payment = Payment(
            booking_id=self.booking.id,
            amount=Decimal("75000.00"),
            payment_method="M-Pesa",
            payment_status=status
        )

        db.session.add(payment)
        db.session.commit()

        return payment

    # ==================================================
    # CREATE PAYMENT
    # ==================================================

    def test_customer_can_create_payment(self):

        response = self.client.post(
            "/api/payments",
            json=self.valid_payment_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["data"]["amount"], "75000.00")
        self.assertEqual(response.json["data"]["payment_method"], "M-Pesa")
        self.assertEqual(response.json["data"]["payment_status"], "pending")

    def test_payment_amount_cannot_be_supplied_by_customer(self):

        data = {
            **self.valid_payment_data,
            "amount": 1
        }

        response = self.client.post(
            "/api/payments",
            json=data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_pending_booking_cannot_be_paid(self):

        self.booking.status = "pending"
        db.session.commit()

        response = self.client.post(
            "/api/payments",
            json=self.valid_payment_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_other_customer_cannot_pay_for_booking(self):

        response = self.client.post(
            "/api/payments",
            json=self.valid_payment_data,
            headers=self.other_customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_create_payment(self):

        response = self.client.post(
            "/api/payments",
            json=self.valid_payment_data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_payment_requires_authentication(self):

        response = self.client.post(
            "/api/payments",
            json=self.valid_payment_data
        )

        self.assertEqual(response.status_code, 401)

    def test_invalid_payment_method_is_rejected(self):

        data = {
            "booking_id": self.booking.id,
            "payment_method": "Bitcoin"
        }

        response = self.client.post(
            "/api/payments",
            json=data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_duplicate_pending_payment_is_rejected(self):

        self.create_payment("pending")

        response = self.client.post(
            "/api/payments",
            json=self.valid_payment_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 409)

    def test_duplicate_successful_payment_is_rejected(self):

        self.create_payment("successful")

        response = self.client.post(
            "/api/payments",
            json=self.valid_payment_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 409)

    # ==================================================
    # VIEW PAYMENTS
    # ==================================================

    def test_customer_can_view_own_payments(self):

        self.create_payment()

        response = self.client.get(
            "/api/payments",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["data"]), 1)

    def test_customer_can_view_one_payment(self):

        payment = self.create_payment()

        response = self.client.get(
            f"/api/payments/{payment.id}",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["id"], payment.id)

    def test_other_customer_cannot_view_payment(self):

        payment = self.create_payment()

        response = self.client.get(
            f"/api/payments/{payment.id}",
            headers=self.other_customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_view_payments(self):

        response = self.client.get(
            "/api/payments",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_missing_payment_returns_404(self):

        response = self.client.get(
            "/api/payments/999",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 404)

    # ==================================================
    # SIMULATE PAYMENT
    # ==================================================

    def test_customer_can_simulate_successful_payment(self):

        payment = self.create_payment()

        response = self.client.post(
            f"/api/payments/{payment.id}/simulate",
            json={"result": "successful"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["data"]["payment_status"],
            "successful"
        )
        self.assertIsNotNone(
            response.json["data"]["transaction_reference"]
        )
        self.assertIsNotNone(
            response.json["data"]["paid_at"]
        )

    def test_customer_can_simulate_failed_payment(self):

        payment = self.create_payment()

        response = self.client.post(
            f"/api/payments/{payment.id}/simulate",
            json={"result": "failed"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["data"]["payment_status"],
            "failed"
        )
        self.assertIsNone(
            response.json["data"]["paid_at"]
        )

    def test_failed_payment_can_be_retried(self):

        payment = self.create_payment()

        self.client.post(
            f"/api/payments/{payment.id}/simulate",
            json={"result": "failed"},
            headers=self.customer_headers
        )

        response = self.client.post(
            "/api/payments",
            json=self.valid_payment_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 201)

    def test_completed_payment_cannot_be_simulated_again(self):

        payment = self.create_payment()

        self.client.post(
            f"/api/payments/{payment.id}/simulate",
            json={"result": "successful"},
            headers=self.customer_headers
        )

        response = self.client.post(
            f"/api/payments/{payment.id}/simulate",
            json={"result": "failed"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_simulation_result_is_rejected(self):

        payment = self.create_payment()

        response = self.client.post(
            f"/api/payments/{payment.id}/simulate",
            json={"result": "maybe"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_other_customer_cannot_simulate_payment(self):

        payment = self.create_payment()

        response = self.client.post(
            f"/api/payments/{payment.id}/simulate",
            json={"result": "successful"},
            headers=self.other_customer_headers
        )

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
