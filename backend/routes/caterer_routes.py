from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import User, CatererProfile
from schemas.caterer_schema import CatererSchema

caterer_bp = Blueprint("caterers", __name__)

caterer_schema = CatererSchema()
caterers_schema = CatererSchema(many=True)


@caterer_bp.route("/api/caterers", methods=["GET"])
def get_caterers():
    caterers = CatererProfile.query.all()

    return jsonify({
        "message": "Caterers retrieved successfully",
        "data": caterers_schema.dump(caterers)
    }), 200


@caterer_bp.route("/api/caterers/<int:caterer_id>", methods=["GET"])
def get_caterer(caterer_id):
    caterer = db.session.get(CatererProfile, caterer_id)

    if not caterer:
        return jsonify({"error": "Caterer not found"}), 404

    return jsonify({"data": caterer_schema.dump(caterer)}), 200


@caterer_bp.route("/api/caterers", methods=["POST"])
def create_caterer():
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        validated_data = caterer_schema.load(data)
        user = db.session.get(User, validated_data["user_id"])

        if not user:
            return jsonify({"error": "User not found"}), 404

        caterer = CatererProfile(
            **validated_data,
            verification_status="pending"
        )

        db.session.add(caterer)
        db.session.commit()

        return jsonify({
            "message": "Caterer created successfully",
            "data": caterer_schema.dump(caterer)
        }), 201

    except ValidationError as error:
        return jsonify({"error": error.messages}), 400

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "A caterer profile already exists for this user"
        }), 409


@caterer_bp.route("/api/caterers/<int:caterer_id>", methods=["PATCH"])
def update_caterer(caterer_id):
    caterer = db.session.get(CatererProfile, caterer_id)

    if not caterer:
        return jsonify({"error": "Caterer not found"}), 404

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        validated_data = caterer_schema.load(data, partial=True)

        if "user_id" in validated_data:
            user = db.session.get(User, validated_data["user_id"])

            if not user:
                return jsonify({"error": "User not found"}), 404

        for field, value in validated_data.items():
            setattr(caterer, field, value)

        db.session.commit()

        return jsonify({
            "message": "Caterer updated successfully",
            "data": caterer_schema.dump(caterer)
        }), 200

    except ValidationError as error:
        return jsonify({"error": error.messages}), 400

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database conflict"}), 409


@caterer_bp.route("/api/caterers/<int:caterer_id>", methods=["DELETE"])
def delete_caterer(caterer_id):
    caterer = db.session.get(CatererProfile, caterer_id)

    if not caterer:
        return jsonify({"error": "Caterer not found"}), 404

    try:
        db.session.delete(caterer)
        db.session.commit()

        return jsonify({
            "message": "Caterer deleted successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Cannot delete caterer because related records exist"
        }), 409