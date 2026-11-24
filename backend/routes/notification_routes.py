from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from extensions import db
from models import Notification
from auth_utils import get_authenticated_user


notification_bp = Blueprint("notifications", __name__)


def serialize_notification(notification):
    """Convert a notification into JSON-friendly data."""
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat()
        if notification.created_at else None
    }


def get_current_user():
    """Return the authenticated user with a verified database role."""
    return get_authenticated_user()


# --------------------------------------------------
# GET ALL NOTIFICATIONS
# ONLY THE LOGGED-IN USER'S NOTIFICATIONS
# --------------------------------------------------

@notification_bp.route("/api/notifications", methods=["GET"])
@jwt_required()
def get_notifications():

    user = get_current_user()

    if not user:
        return jsonify({"error": "User not found."}), 404

    notifications = Notification.query.filter_by(
        user_id=user.id
    ).order_by(
        Notification.created_at.desc(),
        Notification.id.desc()
    ).all()

    return jsonify({
        "data": [
            serialize_notification(notification)
            for notification in notifications
        ]
    }), 200


# --------------------------------------------------
# GET ONE NOTIFICATION
# --------------------------------------------------

@notification_bp.route(
    "/api/notifications/<int:notification_id>",
    methods=["GET"]
)
@jwt_required()
def get_notification(notification_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "User not found."}), 404

    notification = db.session.get(
        Notification,
        notification_id
    )

    if not notification:
        return jsonify({"error": "Notification not found."}), 404

    if notification.user_id != user.id:
        return jsonify({
            "error": "You are not authorized to view this notification."
        }), 403

    return jsonify({
        "data": serialize_notification(notification)
    }), 200


# --------------------------------------------------
# MARK ONE NOTIFICATION AS READ
# --------------------------------------------------

@notification_bp.route(
    "/api/notifications/<int:notification_id>/read",
    methods=["PATCH"]
)
@jwt_required()
def mark_notification_as_read(notification_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "User not found."}), 404

    notification = db.session.get(
        Notification,
        notification_id
    )

    if not notification:
        return jsonify({"error": "Notification not found."}), 404

    if notification.user_id != user.id:
        return jsonify({
            "error": "You are not authorized to update this notification."
        }), 403

    try:
        notification.is_read = True
        db.session.commit()

        return jsonify({
            "message": "Notification marked as read.",
            "data": serialize_notification(notification)
        }), 200

    except Exception:
        db.session.rollback()
        raise


# --------------------------------------------------
# MARK ALL NOTIFICATIONS AS READ
# ONLY THE LOGGED-IN USER'S NOTIFICATIONS
# --------------------------------------------------

@notification_bp.route(
    "/api/notifications/read-all",
    methods=["PATCH"]
)
@jwt_required()
def mark_all_notifications_as_read():

    user = get_current_user()

    if not user:
        return jsonify({"error": "User not found."}), 404

    try:
        Notification.query.filter_by(
            user_id=user.id,
            is_read=False
        ).update(
            {"is_read": True},
            synchronize_session=False
        )

        db.session.commit()

        return jsonify({
            "message": "All notifications marked as read."
        }), 200

    except Exception:
        db.session.rollback()
        raise
