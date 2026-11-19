from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import Booking, User, CatererProfile
from schemas.booking_schema import BookingSchema

booking_bp = Blueprint("bookings", __name__)

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

# GET all bookings
@booking_bp.route("/api/bookings", methods=["GET"])
def get_bookings():
    bookings = Booking.query.all()

    return jsonify({
        "message": "Bookings retrieved successfully",
        "data": bookings_schema.dump(bookings)
    }), 200

# GET one booking
@booking_bp.route("/api/bookings/<int:booking_id>", methods=["GET"])
def get_booking(booking_id):
    booking = db.session.get(Booking, booking_id)

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    return jsonify({
        "data": booking_schema.dump(booking)
    }), 200

# CREATE a booking
@booking_bp.route("/api/bookings", methods=["POST"])
def create_booking():
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        validated_data = booking_schema.load(data)

        customer = db.session.get(
            User, validated_data["customer_id"]
        )

        caterer = db.session.get(
            CatererProfile, validated_data["caterer_id"]
        )

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        if customer.role != "customer":
             return jsonify({"error": "User must have a customer role"}), 400

        if not caterer:
            return jsonify({"error": "Caterer not found"}), 404

        booking = Booking(**validated_data)

        db.session.add(booking)
        db.session.commit()

        return jsonify({
            "message": "Booking created successfully",
            "data": booking_schema.dump(booking)
        }), 201

    except ValidationError as error:
        return jsonify({"error": error.messages}), 400

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Unable to create booking"}), 409


# UPDATE a booking
@booking_bp.route("/api/bookings/<int:booking_id>", methods=["PUT"])
def update_booking(booking_id):
    booking = db.session.get(Booking, booking_id)

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        validated_data = booking_schema.load(
            data, partial=True
        )

        if "customer_id" in validated_data:
            customer = db.session.get(
                User, validated_data["customer_id"]
            )

            if not customer:
                return jsonify({"error": "Customer not found"}), 404

            if customer.role != "customer":
                return jsonify({"error": "User must have a customer role"}), 400

        if "caterer_id" in validated_data:
            caterer = db.session.get(
                CatererProfile, validated_data["caterer_id"]
            )

            if not caterer:
                return jsonify({"error": "Caterer not found"}), 404

        for field, value in validated_data.items():
            setattr(booking, field, value)

        db.session.commit()

        return jsonify({
            "message": "Booking updated successfully",
            "data": booking_schema.dump(booking)
        }), 200

    except ValidationError as error:
        return jsonify({"error": error.messages}), 400

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Unable to update booking"}), 409

# DELETE a booking
@booking_bp.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
def delete_booking(booking_id):
    booking = db.session.get(Booking, booking_id)

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    try:
        db.session.delete(booking)
        db.session.commit()

        return jsonify({
            "message": "Booking deleted successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Cannot delete booking because related records exist"
        }), 409