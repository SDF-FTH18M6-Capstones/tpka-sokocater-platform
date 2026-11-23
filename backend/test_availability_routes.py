import unittest
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from flask_jwt_extended import create_access_token

from app import create_app
from extensions import db
from models import User, Caterer, Availability, Booking


class TestAvailabilityRoutes(unittest.TestCase):

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

        db.session.add_all([
            self.customer,
            self.caterer_user,
            self.other_caterer_user
        ])
        db.session.commit()

        self.caterer = Caterer(
            user_id=self.caterer_user.id,
            business_name="Test Catering",
            location="Nairobi",
            verification_status="pending"
        )

        self.other_caterer = Caterer(
            user_id=self.other_caterer_user.id,
            business_name="Other Catering",
            location="Nairobi",
            verification_status="pending"
        )

        db.session.add_all([
            self.caterer,
            self.other_caterer
        ])
        db.session.commit()

        self.caterer_token = create_access_token(
            identity=str(self.caterer_user.id),
            additional_claims={"role": "caterer"}
        )

        self.other_caterer_token = create_access_token(
            identity=str(self.other_caterer_user.id),
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

        self.customer_headers = {
            "Authorization": f"Bearer {self.customer_token}"
        }

        self.future_date = date.today() + timedelta(days=30)

        self.valid_availability_data = {
            "caterer_id": self.caterer.id,
            "available_date": self.future_date.isoformat(),
            "start_time": "09:00:00",
            "end_time": "12:00:00",
            "status": "available"
        }

    def tearDown(self):

        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    # ==========================================
    # HELPER FUNCTIONS
    # ==========================================

    def create_slot(
        self,
        caterer_id=None,
        available_date=None,
        start_time=time(9, 0),
        end_time=time(12, 0),
        status="available"
    ):

        slot = Availability(
            caterer_id=caterer_id or self.caterer.id,
            available_date=available_date or self.future_date,
            start_time=start_time,
            end_time=end_time,
            status=status
        )

        db.session.add(slot)
        db.session.commit()

        return slot

    def create_booking(
        self,
        event_date=None,
        start_time=time(10, 0),
        end_time=time(11, 0),
        status="pending"
    ):

        booking = Booking(
            customer_id=self.customer.id,
            caterer_id=self.caterer.id,
            event_date=event_date or self.future_date,
            event_start_time=start_time,
            event_end_time=end_time,
            event_type="Birthday",
            event_location="Nairobi",
            guest_count=30,
            estimated_total=Decimal("45000.00"),
            status=status
        )

        db.session.add(booking)
        db.session.commit()

        return booking

    # ==========================================
    # GET ALL AVAILABILITY
    # ==========================================

    def test_get_all_availability(self):

        self.create_slot()

        response = self.client.get("/api/availability")

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json)
        self.assertEqual(len(response.json["data"]), 1)

    def test_get_availability_by_caterer(self):

        self.create_slot()

        self.create_slot(
            caterer_id=self.other_caterer.id
        )

        response = self.client.get(
            f"/api/availability?caterer_id={self.caterer.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["data"]), 1)

    def test_get_availability_by_date(self):

        self.create_slot()

        response = self.client.get(
            f"/api/availability?available_date={self.future_date.isoformat()}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["data"]), 1)

    def test_get_availability_invalid_caterer_id(self):

        response = self.client.get(
            "/api/availability?caterer_id=invalid"
        )

        self.assertEqual(response.status_code, 400)

    def test_get_availability_invalid_date(self):

        response = self.client.get(
            "/api/availability?available_date=invalid-date"
        )

        self.assertEqual(response.status_code, 400)

    # ==========================================
    # GET SINGLE AVAILABILITY SLOT
    # ==========================================

    def test_get_single_availability_slot(self):

        slot = self.create_slot()

        response = self.client.get(
            f"/api/availability/{slot.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["data"]["caterer_id"],
            self.caterer.id
        )

    def test_get_nonexistent_availability_slot(self):

        response = self.client.get("/api/availability/999")

        self.assertEqual(response.status_code, 404)

    # ==========================================
    # CREATE AVAILABILITY
    # ==========================================

    def test_caterer_can_create_availability(self):

        response = self.client.post(
            "/api/availability",
            json=self.valid_availability_data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json["data"]["status"],
            "available"
        )

    def test_customer_cannot_create_availability(self):

        response = self.client.post(
            "/api/availability",
            json=self.valid_availability_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_other_caterer_cannot_create_availability_for_another_profile(self):

        data = self.valid_availability_data.copy()

        response = self.client.post(
            "/api/availability",
            json=data,
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_missing_token_cannot_create_availability(self):

        response = self.client.post(
            "/api/availability",
            json=self.valid_availability_data
        )

        self.assertEqual(response.status_code, 401)

    def test_create_availability_with_invalid_time_range(self):

        data = self.valid_availability_data.copy()
        data["start_time"] = "14:00:00"
        data["end_time"] = "09:00:00"

        response = self.client.post(
            "/api/availability",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_availability_with_past_date(self):

        data = self.valid_availability_data.copy()
        data["available_date"] = (
            date.today() - timedelta(days=1)
        ).isoformat()

        response = self.client.post(
            "/api/availability",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_availability_rejects_invalid_status(self):

        data = self.valid_availability_data.copy()
        data["status"] = "booked"

        response = self.client.post(
            "/api/availability",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_availability_rejects_invalid_json(self):

        response = self.client.post(
            "/api/availability",
            data="invalid json",
            content_type="application/json",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    # ==========================================
    # MULTIPLE SLOTS AND OVERLAPPING SLOTS
    # ==========================================

    def test_multiple_non_overlapping_slots_allowed_on_same_date(self):

        self.create_slot(
            start_time=time(9, 0),
            end_time=time(12, 0)
        )

        data = self.valid_availability_data.copy()
        data["start_time"] = "14:00:00"
        data["end_time"] = "17:00:00"

        response = self.client.post(
            "/api/availability",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            Availability.query.filter_by(
                caterer_id=self.caterer.id,
                available_date=self.future_date
            ).count(),
            2
        )

    def test_adjacent_slots_are_allowed(self):

        self.create_slot(
            start_time=time(9, 0),
            end_time=time(12, 0)
        )

        data = self.valid_availability_data.copy()
        data["start_time"] = "12:00:00"
        data["end_time"] = "15:00:00"

        response = self.client.post(
            "/api/availability",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 201)

    def test_overlapping_slots_are_rejected(self):

        self.create_slot(
            start_time=time(9, 0),
            end_time=time(12, 0)
        )

        data = self.valid_availability_data.copy()
        data["start_time"] = "11:00:00"
        data["end_time"] = "14:00:00"

        response = self.client.post(
            "/api/availability",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 409)

    def test_duplicate_slots_are_rejected(self):

        self.create_slot()

        response = self.client.post(
            "/api/availability",
            json=self.valid_availability_data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 409)

    def test_unavailable_slot_also_prevents_overlapping_slot(self):

        self.create_slot(status="unavailable")

        response = self.client.post(
            "/api/availability",
            json=self.valid_availability_data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 409)

    # ==========================================
    # ACTIVE BOOKING PROTECTION
    # ==========================================

    def test_create_slot_rejects_conflict_with_active_booking(self):

        self.create_booking()

        data = self.valid_availability_data.copy()
        data["start_time"] = "09:30:00"
        data["end_time"] = "11:30:00"

        response = self.client.post(
            "/api/availability",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 409)

    def test_create_slot_rejects_legacy_booking_without_times(self):

        self.create_booking(
            start_time=None,
            end_time=None
        )

        response = self.client.post(
            "/api/availability",
            json=self.valid_availability_data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 409)

    def test_cancelled_booking_does_not_block_availability(self):

        self.create_booking(status="cancelled")

        response = self.client.post(
            "/api/availability",
            json=self.valid_availability_data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 201)

    # ==========================================
    # UPDATE AVAILABILITY
    # ==========================================

    def test_caterer_can_update_own_availability(self):

        slot = self.create_slot()

        response = self.client.put(
            f"/api/availability/{slot.id}",
            json={"status": "unavailable"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["data"]["status"],
            "unavailable"
        )

    def test_other_caterer_cannot_update_availability(self):

        slot = self.create_slot()

        response = self.client.put(
            f"/api/availability/{slot.id}",
            json={"status": "unavailable"},
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_customer_cannot_update_availability(self):

        slot = self.create_slot()

        response = self.client.put(
            f"/api/availability/{slot.id}",
            json={"status": "unavailable"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_update_nonexistent_availability(self):

        response = self.client.put(
            "/api/availability/999",
            json={"status": "unavailable"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 404)

    def test_update_availability_rejects_overlapping_slot(self):

        first_slot = self.create_slot(
            start_time=time(9, 0),
            end_time=time(12, 0)
        )

        second_slot = self.create_slot(
            start_time=time(14, 0),
            end_time=time(17, 0)
        )

        response = self.client.put(
            f"/api/availability/{second_slot.id}",
            json={
                "start_time": "11:00:00",
                "end_time": "15:00:00"
            },
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 409)

    def test_update_availability_rejects_invalid_combined_time_range(self):

        slot = self.create_slot()

        response = self.client.put(
            f"/api/availability/{slot.id}",
            json={"start_time": "13:00:00"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_update_availability_rejects_empty_body(self):

        slot = self.create_slot()

        response = self.client.put(
            f"/api/availability/{slot.id}",
            json={},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_update_availability_cannot_transfer_ownership(self):

        slot = self.create_slot()

        response = self.client.put(
            f"/api/availability/{slot.id}",
            json={"caterer_id": self.other_caterer.id},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_active_booking_prevents_slot_update(self):

        slot = self.create_slot()
        self.create_booking()

        response = self.client.put(
            f"/api/availability/{slot.id}",
            json={"status": "unavailable"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 409)

    # ==========================================
    # DELETE AVAILABILITY
    # ==========================================

    def test_caterer_can_delete_own_availability(self):

        slot = self.create_slot()

        response = self.client.delete(
            f"/api/availability/{slot.id}",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(
            db.session.get(Availability, slot.id)
        )

    def test_other_caterer_cannot_delete_availability(self):

        slot = self.create_slot()

        response = self.client.delete(
            f"/api/availability/{slot.id}",
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_customer_cannot_delete_availability(self):

        slot = self.create_slot()

        response = self.client.delete(
            f"/api/availability/{slot.id}",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_nonexistent_availability(self):

        response = self.client.delete(
            "/api/availability/999",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 404)

    def test_active_booking_prevents_slot_deletion(self):

        slot = self.create_slot()
        self.create_booking()

        response = self.client.delete(
            f"/api/availability/{slot.id}",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 409)

        self.assertIsNotNone(
            db.session.get(Availability, slot.id)
        )


if __name__ == "__main__":
    unittest.main()
