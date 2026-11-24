from datetime import UTC, datetime
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from auth_utils import get_authenticated_user
from extensions import db
from models import Booking, Payment


payment_bp = Blueprint("payments", __name__)

ALLOWED_PAYMENT_METHODS = {
    "m-pesa": "M-Pesa",
    "card": "Card"
}

PAYABLE_BOOKING_STATUSES = {"accepted", "confirmed"}


def serialize_payment(payment):
    """Return a safe, consistent payment response."""

    return {
        "id": payment.id,
        "booking_id": payment.booking_id,
        "amount": f"{payment.amount:.2f}",
        "payment_method": payment.payment_method,
        "transaction_reference": payment.transaction_reference,
        "payment_status": payment.payment_status,
        "paid_at": (
            payment.paid_at.isoformat()
            if payment.paid_at else None
        )
    }


def get_current_customer():
    """Return the authenticated customer."""

    user = get_authenticated_user()

    if user is None:
        return None, (
            jsonify({"error": "User not found or authentication is invalid."}),
            404
        )

    if user.role != "customer":
        return None, (
            jsonify({"error": "Only customers can access payments."}),
            403
        )

    return user, None


# ============================================================
# CREATE PAYMENT
# ============================================================

@payment_bp.route("/api/payments", methods=["POST"])
@jwt_required()
def create_payment():

    customer, error_response = get_current_customer()

    if error_response:
        return error_response

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required."
        }), 400

    if set(data.keys()) != {"booking_id", "payment_method"}:
        return jsonify({
            "error": (
                "Only booking_id and payment_method are accepted."
            )
        }), 400

    booking_id = data.get("booking_id")
    payment_method = data.get("payment_method")

    if (
        isinstance(booking_id, bool)
        or not isinstance(booking_id, int)
        or booking_id < 1
    ):
        return jsonify({
            "error": "A valid booking_id is required."
        }), 400

    if not isinstance(payment_method, str):
        return jsonify({
            "error": "A valid payment method is required."
        }), 400

    normalized_method = payment_method.strip().lower()
    payment_method = ALLOWED_PAYMENT_METHODS.get(normalized_method)

    if not payment_method:
        return jsonify({
            "error": "Payment method must be M-Pesa or Card."
        }), 400

    booking = db.session.get(Booking, booking_id)

    if not booking:
        return jsonify({
            "error": "Booking not found."
        }), 404

    if booking.customer_id != customer.id:
        return jsonify({
            "error": "You are not authorized to pay for this booking."
        }), 403

    if booking.status not in PAYABLE_BOOKING_STATUSES:
        return jsonify({
            "error": (
                "Payment is only allowed for accepted or confirmed bookings."
            )
        }), 400

    # Do not create another payment if one is already successful
    # or awaiting simulation.
    existing_payment = Payment.query.filter(
        Payment.booking_id == booking.id,
        Payment.payment_status.in_(["pending", "successful"])
    ).first()

    if existing_payment:
        return jsonify({
            "error": "A pending or successful payment already exists.",
            "payment": serialize_payment(existing_payment)
        }), 409

    try:
        # The amount is taken from the database, never from the request.
        payment = Payment(
            booking_id=booking.id,
            amount=booking.estimated_total,
            payment_method=payment_method,
            payment_status="pending"
        )

        db.session.add(payment)
        db.session.commit()

        return jsonify({
            "message": "Payment created successfully.",
            "data": serialize_payment(payment)
        }), 201

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to create payment because of a database conflict."
        }), 409


# ============================================================
# GET CUSTOMER PAYMENTS
# ============================================================

@payment_bp.route("/api/payments", methods=["GET"])
@jwt_required()
def get_payments():

    customer, error_response = get_current_customer()

    if error_response:
        return error_response

    payments = (
        Payment.query
        .join(Booking, Payment.booking_id == Booking.id)
        .filter(Booking.customer_id == customer.id)
        .order_by(Payment.id.desc())
        .all()
    )

    return jsonify({
        "data": [serialize_payment(payment) for payment in payments]
    }), 200


# ============================================================
# GET ONE PAYMENT
# ============================================================

@payment_bp.route("/api/payments/<int:payment_id>", methods=["GET"])
@jwt_required()
def get_payment(payment_id):

    customer, error_response = get_current_customer()

    if error_response:
        return error_response

    payment = db.session.get(Payment, payment_id)

    if not payment:
        return jsonify({
            "error": "Payment not found."
        }), 404

    if payment.booking.customer_id != customer.id:
        return jsonify({
            "error": "You are not authorized to view this payment."
        }), 403

    return jsonify({
        "data": serialize_payment(payment)
    }), 200


# ============================================================
# SIMULATE PAYMENT RESULT
# DEVELOPMENT AND TESTING ONLY
# ============================================================

@payment_bp.route(
    "/api/payments/<int:payment_id>/simulate",
    methods=["POST"]
)
@jwt_required()
def simulate_payment(payment_id):

    if not current_app.config.get("PAYMENTS_SIMULATION_ENABLED", False):
        return jsonify({
            "error": "Payment simulation is disabled."
        }), 403

    customer, error_response = get_current_customer()

    if error_response:
        return error_response

    payment = db.session.get(Payment, payment_id)

    if not payment:
        return jsonify({
            "error": "Payment not found."
        }), 404

    if payment.booking.customer_id != customer.id:
        return jsonify({
            "error": "You are not authorized to update this payment."
        }), 403

    if payment.payment_status != "pending":
        return jsonify({
            "error": "Only pending payments can be simulated."
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or set(data.keys()) != {"result"}:
        return jsonify({
            "error": "Provide a result of successful or failed."
        }), 400

    result = data.get("result")

    if result not in {"successful", "failed"}:
        return jsonify({
            "error": "Result must be successful or failed."
        }), 400

    try:
        payment.payment_status = result

        if result == "successful":
            payment.paid_at = datetime.now(UTC)
            payment.transaction_reference = (
                f"SIM-{uuid4().hex[:12].upper()}"
            )

        db.session.commit()

        return jsonify({
            "message": f"Simulated payment {result}.",
            "data": serialize_payment(payment)
        }), 200

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to update payment because of a database conflict."
        }), 409
