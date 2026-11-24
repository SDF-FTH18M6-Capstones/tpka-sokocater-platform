
from extensions import db
from models import Notification


def add_notification(user_id, message, notification_type):
    """
    Add a notification to the current database transaction.

    The calling route is responsible for committing or
    rolling back the transaction.
    """
    notification = Notification(
        user_id=user_id,
        message=message,
        notification_type=notification_type,
        is_read=False
    )

    db.session.add(notification)

    return notification
