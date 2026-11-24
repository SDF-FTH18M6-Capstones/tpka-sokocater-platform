import unittest

from app import create_app
from extensions import db
from models import User, Notification
from flask_jwt_extended import create_access_token


class TestNotificationRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "JWT_SECRET_KEY": "sokocater-notification-test-secret-2026"
        })

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create two separate users.
        self.user1 = User(
            full_name="Customer One",
            email="customer1@example.com",
            password_hash="test-password-hash",
            role="customer"
        )

        self.user2 = User(
            full_name="Customer Two",
            email="customer2@example.com",
            password_hash="test-password-hash",
            role="customer"
        )

        db.session.add_all([self.user1, self.user2])
        db.session.commit()

        # Generate JWT tokens for both users.
        self.token1 = create_access_token(
            identity=str(self.user1.id),
            additional_claims={"role": self.user1.role}
        )

        self.token2 = create_access_token(
            identity=str(self.user2.id),
            additional_claims={"role": self.user2.role}
        )

        self.headers1 = {
            "Authorization": f"Bearer {self.token1}"
        }

        self.headers2 = {
            "Authorization": f"Bearer {self.token2}"
        }

        # Create notifications belonging to different users.
        self.notification1 = Notification(
            user_id=self.user1.id,
            message="Your booking request has been received.",
            notification_type="booking_created",
            is_read=False
        )

        self.notification2 = Notification(
            user_id=self.user1.id,
            message="Your booking has been accepted.",
            notification_type="booking_status",
            is_read=False
        )

        self.notification3 = Notification(
            user_id=self.user2.id,
            message="You have a new booking request.",
            notification_type="booking_created",
            is_read=False
        )

        db.session.add_all([
            self.notification1,
            self.notification2,
            self.notification3
        ])

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --------------------------------------------------
    # GET ALL NOTIFICATIONS
    # --------------------------------------------------

    def test_user_can_get_their_notifications(self):
        response = self.client.get(
            "/api/notifications",
            headers=self.headers1
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()["data"]

        self.assertEqual(len(data), 2)

        notification_ids = {
            notification["id"] for notification in data
        }

        self.assertEqual(
            notification_ids,
            {
                self.notification1.id,
                self.notification2.id
            }
        )

    def test_user_cannot_see_another_users_notifications(self):
        response = self.client.get(
            "/api/notifications",
            headers=self.headers2
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()["data"]

        self.assertEqual(len(data), 1)

        self.assertEqual(
            data[0]["id"],
            self.notification3.id
        )

    def test_get_notifications_requires_authentication(self):
        response = self.client.get("/api/notifications")

        self.assertEqual(response.status_code, 401)

    # --------------------------------------------------
    # GET ONE NOTIFICATION
    # --------------------------------------------------

    def test_user_can_get_their_own_notification(self):
        response = self.client.get(
            f"/api/notifications/{self.notification1.id}",
            headers=self.headers1
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()["data"]

        self.assertEqual(
            data["id"],
            self.notification1.id
        )

        self.assertEqual(
            data["message"],
            "Your booking request has been received."
        )

    def test_user_cannot_get_another_users_notification(self):
        response = self.client.get(
            f"/api/notifications/{self.notification1.id}",
            headers=self.headers2
        )

        self.assertEqual(response.status_code, 403)

    def test_get_nonexistent_notification_returns_404(self):
        response = self.client.get(
            "/api/notifications/9999",
            headers=self.headers1
        )

        self.assertEqual(response.status_code, 404)

    # --------------------------------------------------
    # MARK ONE NOTIFICATION AS READ
    # --------------------------------------------------

    def test_user_can_mark_their_notification_as_read(self):
        response = self.client.patch(
            f"/api/notifications/{self.notification1.id}/read",
            headers=self.headers1
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            response.get_json()["data"]["is_read"]
        )

        notification = db.session.get(
            Notification,
            self.notification1.id
        )

        self.assertTrue(notification.is_read)

    def test_user_cannot_mark_another_users_notification_as_read(self):
        response = self.client.patch(
            f"/api/notifications/{self.notification1.id}/read",
            headers=self.headers2
        )

        self.assertEqual(response.status_code, 403)

        notification = db.session.get(
            Notification,
            self.notification1.id
        )

        self.assertFalse(notification.is_read)

    def test_mark_nonexistent_notification_as_read_returns_404(self):
        response = self.client.patch(
            "/api/notifications/9999/read",
            headers=self.headers1
        )

        self.assertEqual(response.status_code, 404)

    # --------------------------------------------------
    # MARK ALL NOTIFICATIONS AS READ
    # --------------------------------------------------

    def test_user_can_mark_all_their_notifications_as_read(self):
        response = self.client.patch(
            "/api/notifications/read-all",
            headers=self.headers1
        )

        self.assertEqual(response.status_code, 200)

        notifications = Notification.query.filter_by(
            user_id=self.user1.id
        ).all()

        self.assertEqual(len(notifications), 2)

        for notification in notifications:
            self.assertTrue(notification.is_read)

    def test_mark_all_does_not_change_another_users_notifications(self):
        response = self.client.patch(
            "/api/notifications/read-all",
            headers=self.headers1
        )

        self.assertEqual(response.status_code, 200)

        other_notification = db.session.get(
            Notification,
            self.notification3.id
        )

        self.assertFalse(other_notification.is_read)

    def test_mark_all_notifications_requires_authentication(self):
        response = self.client.patch(
            "/api/notifications/read-all"
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
