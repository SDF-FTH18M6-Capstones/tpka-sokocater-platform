from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Availability, Booking, Caterer
from auth_utils import get_authenticated_user
from schemas.availability_schema import AvailabilitySchema


availability_bp = Blueprint("availability", __name__)

availability_schema = AvailabilitySchema()
availabilities_schema = AvailabilitySchema(many=True)

ACTIVE_BOOKING_STATUSES = ["pending", "accepted", "confirmed"]


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def get_current_caterer():
    """Return the caterer profile of the authenticated caterer."""

    user = get_authenticated_user()

    if user is None or user.role != "caterer":
        return None

    return Caterer.query.filter_by(user_id=user.id).first()


def find_overlapping_slot(
    caterer_id,
    available_date,
    start_time,
    end_time,
    exclude_slot_id=None
):
    """
    Find any slot belonging to the same caterer and date
    that overlaps the proposed time range.

    Adjacent slots are allowed.
    """

    query = Availability.query.filter(
        Availability.caterer_id == caterer_id,
        Availability.available_date == available_date,
        Availability.start_time < end_time,
        Availability.end_time > start_time
    )

    if exclude_slot_id is not None:
        query = query.filter(Availability.id != exclude_slot_id)

    return query.first()


def find_active_booking(caterer_id, event_date, start_time, end_time):
    """
    Find an active booking that conflicts with a time range.

    Historical bookings with NULL event times are treated
    as occupying the entire event date.
    """

    return Booking.query.filter(
        Booking.caterer_id == caterer_id,
        Booking.event_date == event_date,
        Booking.status.in_(ACTIVE_BOOKING_STATUSES),
        or_(
            and_(
                Booking.event_start_time.is_(None),
                Booking.event_end_time.is_(None)
            ),
            and_(
                Booking.event_start_time < end_time,
                Booking.event_end_time > start_time
            )
        )
    ).first()


def slot_has_active_booking(slot):
    """Check whether an active booking overlaps an existing slot."""

    return find_active_booking(
        slot.caterer_id,
        slot.available_date,
        slot.start_time,
        slot.end_time
    ) is not None


# ==================================================
# GET ALL AVAILABILITY - PUBLIC
# ==================================================

@availability_bp.route("/api/availability", methods=["GET"])
def get_availability():

    query = Availability.query

    caterer_id = request.args.get("caterer_id")
    available_date = request.args.get("available_date")

    if caterer_id is not None:
        try:
            caterer_id = int(caterer_id)

            if caterer_id < 1:
                raise ValueError

        except ValueError:
            return jsonify({
                "error": "caterer_id must be a positive integer"
            }), 400

        query = query.filter(
            Availability.caterer_id == caterer_id
        )

    if available_date is not None:
        try:
            available_date = date.fromisoformat(available_date)

        except ValueError:
            return jsonify({
                "error": "available_date must use YYYY-MM-DD format"
            }), 400

        query = query.filter(
            Availability.available_date == available_date
        )

    slots = query.order_by(
        Availability.available_date,
        Availability.start_time
    ).all()

    return jsonify({
        "message": "Availability retrieved successfully",
        "data": availabilities_schema.dump(slots)
    }), 200


# ==================================================
# GET SINGLE AVAILABILITY SLOT - PUBLIC
# ==================================================

@availability_bp.route(
    "/api/availability/<int:availability_id>",
    methods=["GET"]
)
def get_availability_slot(availability_id):

    slot = db.session.get(Availability, availability_id)

    if slot is None:
        return jsonify({
            "error": "Availability slot not found"
        }), 404

    return jsonify({
        "data": availability_schema.dump(slot)
    }), 200


# ==================================================
# CREATE AVAILABILITY SLOT - CATERER ONLY
# ==================================================

@availability_bp.route("/api/availability", methods=["POST"])
@jwt_required()
def create_availability():

    current_caterer = get_current_caterer()

    if current_caterer is None:
        return jsonify({
            "error": "Only registered caterers can create availability"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        validated_data = availability_schema.load(data)

        if validated_data["caterer_id"] != current_caterer.id:
            return jsonify({
                "error": "You can only create availability for your own profile"
            }), 403

        # Prevent overlapping slots, regardless of their status.
        overlapping_slot = find_overlapping_slot(
            current_caterer.id,
            validated_data["available_date"],
            validated_data["start_time"],
            validated_data["end_time"]
        )

        if overlapping_slot is not None:
            return jsonify({
                "error": "This time slot overlaps an existing availability slot"
            }), 409

        # Do not create availability over an active booking.
        active_booking = find_active_booking(
            current_caterer.id,
            validated_data["available_date"],
            validated_data["start_time"],
            validated_data["end_time"]
        )

        if active_booking is not None:
            return jsonify({
                "error": "This time slot conflicts with an active booking"
            }), 409

        slot = Availability(**validated_data)

        db.session.add(slot)
        db.session.commit()

        return jsonify({
            "message": "Availability created successfully",
            "data": availability_schema.dump(slot)
        }), 201

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to create availability slot"
        }), 409


# ==================================================
# UPDATE AVAILABILITY SLOT - OWNER ONLY
# ==================================================

@availability_bp.route(
    "/api/availability/<int:availability_id>",
    methods=["PUT"]
)
@jwt_required()
def update_availability(availability_id):

    current_caterer = get_current_caterer()

    if current_caterer is None:
        return jsonify({
            "error": "Only registered caterers can update availability"
        }), 403

    slot = db.session.get(Availability, availability_id)

    if slot is None:
        return jsonify({
            "error": "Availability slot not found"
        }), 404

    if slot.caterer_id != current_caterer.id:
        return jsonify({
            "error": "You can only update your own availability"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    if not data:
        return jsonify({
            "error": "No fields provided for update"
        }), 400

    try:
        validated_data = availability_schema.load(
            data,
            partial=True
        )

        if (
            "caterer_id" in validated_data
            and validated_data["caterer_id"] != current_caterer.id
        ):
            return jsonify({
                "error": "You cannot transfer availability to another caterer"
            }), 403

        # A slot with an active booking cannot be changed.
        if slot_has_active_booking(slot):
            return jsonify({
                "error": "This slot cannot be changed because it overlaps an active booking"
            }), 409

        # Validate the combined values, including unchanged fields.
        new_date = validated_data.get(
            "available_date",
            slot.available_date
        )

        new_start_time = validated_data.get(
            "start_time",
            slot.start_time
        )

        new_end_time = validated_data.get(
            "end_time",
            slot.end_time
        )

        if new_start_time >= new_end_time:
            return jsonify({
                "error": {
                    "end_time": [
                        "End time must be later than start time."
                    ]
                }
            }), 400

        overlapping_slot = find_overlapping_slot(
            current_caterer.id,
            new_date,
            new_start_time,
            new_end_time,
            exclude_slot_id=slot.id
        )

        if overlapping_slot is not None:
            return jsonify({
                "error": "This time slot overlaps another availability slot"
            }), 409

        active_booking = find_active_booking(
            current_caterer.id,
            new_date,
            new_start_time,
            new_end_time
        )

        if active_booking is not None:
            return jsonify({
                "error": "This time slot conflicts with an active booking"
            }), 409

        for field, value in validated_data.items():
            setattr(slot, field, value)

        db.session.commit()

        return jsonify({
            "message": "Availability updated successfully",
            "data": availability_schema.dump(slot)
        }), 200

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to update availability slot"
        }), 409


# ==================================================
# DELETE AVAILABILITY SLOT - OWNER ONLY
# ==================================================

@availability_bp.route(
    "/api/availability/<int:availability_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_availability(availability_id):

    current_caterer = get_current_caterer()

    if current_caterer is None:
        return jsonify({
            "error": "Only registered caterers can delete availability"
        }), 403

    slot = db.session.get(Availability, availability_id)

    if slot is None:
        return jsonify({
            "error": "Availability slot not found"
        }), 404

    if slot.caterer_id != current_caterer.id:
        return jsonify({
            "error": "You can only delete your own availability"
        }), 403

    if slot_has_active_booking(slot):
        return jsonify({
            "error": "This slot cannot be deleted because it overlaps an active booking"
        }), 409

    try:
        db.session.delete(slot)
        db.session.commit()

        return jsonify({
            "message": "Availability deleted successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to delete availability slot"
        }), 409
