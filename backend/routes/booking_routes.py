
from decimal import Decimal

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import Booking, BookingItem, User, Caterer, Package
from schemas.booking_schema import BookingSchema


booking_bp = Blueprint("bookings", __name__)

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)


# --------------------------------------------------
# BOOKING STATUS TRANSITIONS
# --------------------------------------------------

ALLOWED_STATUS_TRANSITIONS = {
    "pending": ["accepted", "rejected", "cancelled"],
    "accepted": ["confirmed", "cancelled"],
    "confirmed": ["completed", "cancelled"],
    "rejected": [],
    "cancelled": [],
    "completed": []
}


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_current_user():
    """Return the currently authenticated user."""

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return None

    return db.session.get(User, user_id)


def get_booking_total(booking_id):
    """Calculate the total from all booking items."""

    items = BookingItem.query.filter_by(
        booking_id=booking_id
    ).all()

    total = Decimal("0.00")

    for item in items:
        total += (
            Decimal(str(item.unit_price))
            * Decimal(str(item.quantity))
        )

    return total


def validate_package(package_id, caterer_id, guest_count):
    """Validate package existence, ownership and guest limits."""

    package = db.session.get(Package, package_id)

    if not package:
        return None, "Package not found."

    if package.caterer_id != caterer_id:
        return None, (
            "This package does not belong to the selected caterer."
        )

    if guest_count < package.minimum_guests:
        return None, (
            f"This package requires at least "
            f"{package.minimum_guests} guests."
        )

    if (
        package.maximum_guests is not None
        and guest_count > package.maximum_guests
    ):
        return None, (
            f"This package allows a maximum of "
            f"{package.maximum_guests} guests."
        )

    return package, None


def get_booking_package_item(booking_id):
    """Find the package item belonging to a booking."""

    return BookingItem.query.filter(
        BookingItem.booking_id == booking_id,
        BookingItem.package_id.isnot(None)
    ).first()


# --------------------------------------------------
# GET ALL BOOKINGS
# --------------------------------------------------

@booking_bp.route("/api/bookings", methods=["GET"])
@jwt_required()
def get_bookings():

    user = get_current_user()

    if not user:
        return jsonify({
            "error": "User not found."
        }), 404

    role = get_jwt().get("role")

    if role == "customer":

        bookings = Booking.query.filter_by(
            customer_id=user.id
        ).all()

    elif role == "caterer":

        caterer = Caterer.query.filter_by(
            user_id=user.id
        ).first()

        if not caterer:
            return jsonify({
                "error": "Caterer profile not found."
            }), 404

        bookings = Booking.query.filter_by(
            caterer_id=caterer.id
        ).all()

    else:
        return jsonify({
            "error": "You are not authorized to view bookings."
        }), 403

    return jsonify({
        "data": bookings_schema.dump(bookings)
    }), 200


# --------------------------------------------------
# GET ONE BOOKING
# --------------------------------------------------

@booking_bp.route("/api/bookings/<int:booking_id>", methods=["GET"])
@jwt_required()
def get_booking(booking_id):

    user = get_current_user()

    if not user:
        return jsonify({
            "error": "User not found."
        }), 404

    role = get_jwt().get("role")

    booking = db.session.get(Booking, booking_id)

    if not booking:
        return jsonify({
            "error": "Booking not found."
        }), 404

    if role == "customer":

        if booking.customer_id != user.id:
            return jsonify({
                "error": "You are not authorized to view this booking."
            }), 403

    elif role == "caterer":

        caterer = Caterer.query.filter_by(
            user_id=user.id
        ).first()

        if not caterer:
            return jsonify({
                "error": "Caterer profile not found."
            }), 404

        if booking.caterer_id != caterer.id:
            return jsonify({
                "error": "You are not authorized to view this booking."
            }), 403

    else:
        return jsonify({
            "error": "You are not authorized to view bookings."
        }), 403

    return jsonify({
        "data": booking_schema.dump(booking)
    }), 200


# --------------------------------------------------
# CREATE BOOKING
# --------------------------------------------------

@booking_bp.route("/api/bookings", methods=["POST"])
@jwt_required()
def create_booking():

    user = get_current_user()

    if not user:
        return jsonify({
            "error": "User not found."
        }), 404

    role = get_jwt().get("role")

    if role != "customer":
        return jsonify({
            "error": "Only customers can create bookings."
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required."
        }), 400

    try:

        booking_data = booking_schema.load(data)

        caterer = db.session.get(
            Caterer,
            booking_data["caterer_id"]
        )

        if not caterer:
            return jsonify({
                "error": "Caterer not found."
            }), 404

        package, error = validate_package(
            booking_data["package_id"],
            caterer.id,
            booking_data["guest_count"]
        )

        if error:
            return jsonify({
                "error": error
            }), 400

        estimated_total = (
            Decimal(str(package.price_per_guest))
            * Decimal(str(booking_data["guest_count"]))
        )

        booking = Booking(
            customer_id=user.id,
            caterer_id=caterer.id,
            event_type=booking_data["event_type"],
            event_date=booking_data["event_date"],
            event_location=booking_data["event_location"],
            guest_count=booking_data["guest_count"],
            estimated_total=estimated_total,
            status="pending"
        )

        db.session.add(booking)
        db.session.flush()

        package_item = BookingItem(
            booking_id=booking.id,
            package_id=package.id,
            quantity=booking.guest_count,
            unit_price=package.price_per_guest
        )

        db.session.add(package_item)
        db.session.commit()

        return jsonify({
            "message": "Booking created successfully.",
            "data": booking_schema.dump(booking)
        }), 201

    except ValidationError as error:

        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:

        db.session.rollback()

        return jsonify({
            "error": (
                "Unable to create booking because of a database conflict."
            )
        }), 409

    except Exception:

        db.session.rollback()
        raise


# --------------------------------------------------
# UPDATE BOOKING
# --------------------------------------------------

@booking_bp.route("/api/bookings/<int:booking_id>", methods=["PUT"])
@jwt_required()
def update_booking(booking_id):

    user = get_current_user()

    if not user:
        return jsonify({
            "error": "User not found."
        }), 404

    role = get_jwt().get("role")

    booking = db.session.get(Booking, booking_id)

    if not booking:
        return jsonify({
            "error": "Booking not found."
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "A valid, non-empty JSON object is required."
        }), 400

    # ----------------------------------------------
    # CATERER: UPDATE BOOKING STATUS
    # ----------------------------------------------

    if role == "caterer":

        caterer = Caterer.query.filter_by(
            user_id=user.id
        ).first()

        if not caterer:
            return jsonify({
                "error": "Caterer profile not found."
            }), 404

        if booking.caterer_id != caterer.id:
            return jsonify({
                "error": "You are not authorized to update this booking."
            }), 403

        # Caterers can only update the status.
        if set(data.keys()) != {"status"}:
            return jsonify({
                "error": "Caterers can only update booking status."
            }), 400

        new_status = data.get("status")

        if not isinstance(new_status, str):
            return jsonify({
                "error": "A valid booking status is required."
            }), 400

        new_status = new_status.strip().lower()

        current_status = booking.status

        allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(
            current_status,
            []
        )

        if new_status not in allowed_statuses:
            return jsonify({
                "error": (
                    f"Cannot change booking status from "
                    f"'{current_status}' to '{new_status}'."
                )
            }), 400

        booking.status = new_status

        try:

            db.session.commit()

            return jsonify({
                "message": "Booking status updated successfully.",
                "data": booking_schema.dump(booking)
            }), 200

        except IntegrityError:

            db.session.rollback()

            return jsonify({
                "error": "Unable to update booking status."
            }), 409

    # ----------------------------------------------
    # CUSTOMER: UPDATE BOOKING DETAILS
    # ----------------------------------------------

    elif role == "customer":

        if booking.customer_id != user.id:
            return jsonify({
                "error": "You are not authorized to update this booking."
            }), 403

        if booking.status != "pending":
            return jsonify({
                "error": "Only pending bookings can be edited."
            }), 400

        # Customers cannot modify server-controlled fields.
        forbidden_fields = {
            "status",
            "customer_id",
            "estimated_total",
            "created_at",
            "id"
        }

        if forbidden_fields.intersection(data.keys()):
            return jsonify({
                "error": (
                    "You are not authorized to update these fields."
                )
            }), 403

        allowed_fields = {
            "caterer_id",
            "package_id",
            "event_type",
            "event_date",
            "event_location",
            "guest_count"
        }

        if not set(data.keys()).issubset(allowed_fields):
            return jsonify({
                "error": "One or more fields cannot be updated."
            }), 400

        try:

            booking_data = booking_schema.load(
                data,
                partial=True
            )

            new_caterer_id = booking_data.get(
                "caterer_id",
                booking.caterer_id
            )

            new_guest_count = booking_data.get(
                "guest_count",
                booking.guest_count
            )

            package_item = get_booking_package_item(
                booking.id
            )

            if not package_item:
                return jsonify({
                    "error": "Booking package information is missing."
                }), 400

            new_package_id = booking_data.get(
                "package_id",
                package_item.package_id
            )

            caterer = db.session.get(
                Caterer,
                new_caterer_id
            )

            if not caterer:
                return jsonify({
                    "error": "Caterer not found."
                }), 404

            package, error = validate_package(
                new_package_id,
                new_caterer_id,
                new_guest_count
            )

            if error:
                return jsonify({
                    "error": error
                }), 400

            booking.caterer_id = new_caterer_id

            if "event_type" in booking_data:
                booking.event_type = booking_data["event_type"]

            if "event_date" in booking_data:
                booking.event_date = booking_data["event_date"]

            if "event_location" in booking_data:
                booking.event_location = booking_data["event_location"]

            booking.guest_count = new_guest_count

            package_item.package_id = package.id
            package_item.quantity = new_guest_count
            package_item.unit_price = package.price_per_guest

            db.session.flush()

            booking.estimated_total = get_booking_total(
                booking.id
            )

            db.session.commit()

            return jsonify({
                "message": "Booking updated successfully.",
                "data": booking_schema.dump(booking)
            }), 200

        except ValidationError as error:

            db.session.rollback()

            return jsonify({
                "error": error.messages
            }), 400

        except IntegrityError:

            db.session.rollback()

            return jsonify({
                "error": (
                    "Unable to update booking because of a database conflict."
                )
            }), 409

        except Exception:

            db.session.rollback()
            raise

    return jsonify({
        "error": "You are not authorized to update bookings."
    }), 403


# --------------------------------------------------
# DELETE BOOKING
# --------------------------------------------------

@booking_bp.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
@jwt_required()
def delete_booking(booking_id):

    user = get_current_user()

    if not user:
        return jsonify({
            "error": "User not found."
        }), 404

    role = get_jwt().get("role")

    if role != "customer":
        return jsonify({
            "error": "Only customers can delete their bookings."
        }), 403

    booking = db.session.get(Booking, booking_id)

    if not booking:
        return jsonify({
            "error": "Booking not found."
        }), 404

    if booking.customer_id != user.id:
        return jsonify({
            "error": "You are not authorized to delete this booking."
        }), 403

    if booking.status != "pending":
        return jsonify({
            "error": "Only pending bookings can be deleted."
        }), 400

    try:

        BookingItem.query.filter_by(
            booking_id=booking.id
        ).delete(synchronize_session=False)

        db.session.delete(booking)
        db.session.commit()

        return jsonify({
            "message": "Booking deleted successfully."
        }), 200

    except IntegrityError:

        db.session.rollback()

        return jsonify({
            "error": (
                "This booking cannot be deleted because it has "
                "related payment or review records."
            )
        }), 409

    except Exception:

        db.session.rollback()
        raise
