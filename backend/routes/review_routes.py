from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Review, Booking, CatererProfile
from auth_utils import get_authenticated_user


review_bp = Blueprint("reviews", __name__)


def serialize_review(review):
    return {
        "id": review.id,
        "customer_id": review.customer_id,
        "caterer_id": review.caterer_id,
        "booking_id": review.booking_id,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": (
            review.created_at.isoformat()
            if review.created_at else None
        )
    }


# --------------------------------------------------
# CREATE A REVIEW
# Only the customer who owns a completed booking
# can review it.
# --------------------------------------------------

@review_bp.route("/api/reviews", methods=["POST"])
@jwt_required()
def create_review():

    user = get_authenticated_user()

    if not user:
        return jsonify({"error": "User not found."}), 404

    if user.role != "customer":
        return jsonify({
            "error": "Only customers can submit reviews."
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A valid JSON object is required."}), 400

    allowed_fields = {"booking_id", "rating", "comment"}

    if set(data.keys()) - allowed_fields:
        return jsonify({
            "error": "Only booking_id, rating and comment are allowed."
        }), 400

    booking_id = data.get("booking_id")
    rating = data.get("rating")
    comment = data.get("comment")

    if (
        isinstance(booking_id, bool)
        or not isinstance(booking_id, int)
        or booking_id <= 0
    ):
        return jsonify({
            "error": "A valid positive booking_id is required."
        }), 400

    if (
        isinstance(rating, bool)
        or not isinstance(rating, int)
        or rating < 1
        or rating > 5
    ):
        return jsonify({
            "error": "Rating must be an integer between 1 and 5."
        }), 400

    if comment is not None and not isinstance(comment, str):
        return jsonify({
            "error": "Comment must be a string or null."
        }), 400

    booking = db.session.get(Booking, booking_id)

    if not booking:
        return jsonify({"error": "Booking not found."}), 404

    if booking.customer_id != user.id:
        return jsonify({
            "error": "You can only review your own bookings."
        }), 403

    if booking.status != "completed":
        return jsonify({
            "error": "You can only review completed bookings."
        }), 400

    existing_review = Review.query.filter_by(
        booking_id=booking.id
    ).first()

    if existing_review:
        return jsonify({
            "error": "This booking has already been reviewed."
        }), 409

    review = Review(
        customer_id=user.id,
        caterer_id=booking.caterer_id,
        booking_id=booking.id,
        rating=rating,
        comment=comment.strip() or None if comment else None
    )

    try:
        db.session.add(review)
        db.session.commit()

        return jsonify({
            "message": "Review submitted successfully.",
            "data": serialize_review(review)
        }), 201

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "A review already exists for this booking."
        }), 409


# --------------------------------------------------
# GET ALL REVIEWS FOR A CATERER
# Public endpoint.
# --------------------------------------------------

@review_bp.route(
    "/api/caterers/<int:caterer_id>/reviews",
    methods=["GET"]
)
def get_caterer_reviews(caterer_id):

    caterer = db.session.get(CatererProfile, caterer_id)

    if not caterer:
        return jsonify({"error": "Caterer not found."}), 404

    reviews = Review.query.filter_by(
        caterer_id=caterer_id
    ).order_by(
        Review.created_at.desc(),
        Review.id.desc()
    ).all()

    return jsonify({
        "caterer_id": caterer_id,
        "total_reviews": len(reviews),
        "data": [
            serialize_review(review)
            for review in reviews
        ]
    }), 200
