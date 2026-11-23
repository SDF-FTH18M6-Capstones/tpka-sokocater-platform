from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import Caterer
from auth_utils import get_authenticated_user
from schemas.caterer_schema import CatererSchema


caterer_bp = Blueprint("caterers", __name__)

caterer_schema = CatererSchema()
caterers_schema = CatererSchema(many=True)


# --------------------------------------------------
# SERIALIZATION HELPERS
# --------------------------------------------------

def serialize_package(package):
    """Return package information together with its selected menu items."""

    return {
        "id": package.id,
        "caterer_id": package.caterer_id,
        "package_name": package.package_name,
        "description": package.description,
        "price_per_guest": str(package.price_per_guest),
        "minimum_guests": package.minimum_guests,
        "maximum_guests": package.maximum_guests,
        "menu_items": [
            {
                "id": package_item.menu_item.id,
                "menu_id": package_item.menu_item.menu_id,
                "item_name": package_item.menu_item.item_name,
                "description": package_item.menu_item.description,
                "price": str(package_item.menu_item.price),
                "image_url": package_item.menu_item.image_url
            }
            for package_item in package.package_items
            if package_item.menu_item is not None
        ]
    }


def serialize_caterer(caterer, include_packages=False):
    """Serialize a caterer with its package price range."""

    caterer_data = caterer_schema.dump(caterer)

    # Include category when the model has that field.
    if hasattr(caterer, "category"):
        caterer_data["category"] = caterer.category

    packages = caterer.packages

    if packages:
        prices = [
            package.price_per_guest
            for package in packages
        ]

        caterer_data["price_range"] = {
            "min_price": str(min(prices)),
            "max_price": str(max(prices))
        }
    else:
        caterer_data["price_range"] = {
            "min_price": None,
            "max_price": None
        }

    if include_packages:
        caterer_data["packages"] = [
            serialize_package(package)
            for package in packages
        ]

    return caterer_data


# --------------------------------------------------
# GET ALL CATERERS - PUBLIC
# --------------------------------------------------

@caterer_bp.route("/api/caterers", methods=["GET"])
def get_caterers():

    query = Caterer.query

    category = request.args.get("category")

    if category is not None:
        category = category.strip()

        if not category:
            return jsonify({
                "error": "Category cannot be empty"
            }), 400

        if not hasattr(Caterer, "category"):
            return jsonify({
                "error": (
                    "Category filtering is not available yet. "
                    "The caterer category field must first be added "
                    "to the database model."
                )
            }), 501

        query = query.filter(
            db.func.lower(Caterer.category) == category.lower()
        )

    caterers = query.all()

    return jsonify({
        "message": "Caterers retrieved successfully",
        "data": [
            serialize_caterer(caterer)
            for caterer in caterers
        ]
    }), 200


# --------------------------------------------------
# GET ONE CATERER - PUBLIC
# --------------------------------------------------

@caterer_bp.route("/api/caterers/<int:caterer_id>", methods=["GET"])
def get_caterer(caterer_id):

    caterer = db.session.get(Caterer, caterer_id)

    if not caterer:
        return jsonify({
            "error": "Caterer not found"
        }), 404

    return jsonify({
        "data": serialize_caterer(
            caterer,
            include_packages=True
        )
    }), 200


# --------------------------------------------------
# CREATE CATERER PROFILE
# --------------------------------------------------

@caterer_bp.route("/api/caterers", methods=["POST"])
@jwt_required()
def create_caterer():

    user = get_authenticated_user()

    if user is None:
        return jsonify({
            "error": "Invalid or outdated user identity"
        }), 401

    if user.role != "caterer":
        return jsonify({
            "error": "Only caterers can create caterer profiles"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    if "verification_status" in data:
        return jsonify({
            "error": "You cannot set your own verification status"
        }), 400

    try:
        validated_data = caterer_schema.load(data)

        if validated_data["user_id"] != user.id:
            return jsonify({
                "error": "You can only create a profile for yourself"
            }), 403

        existing_caterer = Caterer.query.filter_by(
            user_id=user.id
        ).first()

        if existing_caterer:
            return jsonify({
                "error": "You already have a caterer profile"
            }), 409

        validated_data.pop("verification_status", None)

        caterer = Caterer(
            **validated_data,
            verification_status="pending"
        )

        db.session.add(caterer)
        db.session.commit()

        return jsonify({
            "message": "Caterer created successfully",
            "data": serialize_caterer(caterer)
        }), 201

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "A caterer profile already exists for this user"
        }), 409


# --------------------------------------------------
# UPDATE CATERER PROFILE - OWNER ONLY
# --------------------------------------------------

@caterer_bp.route("/api/caterers/<int:caterer_id>", methods=["PUT"])
@jwt_required()
def update_caterer(caterer_id):

    user = get_authenticated_user()

    if user is None:
        return jsonify({
            "error": "Invalid or outdated user identity"
        }), 401

    if user.role != "caterer":
        return jsonify({
            "error": "Only caterers can update caterer profiles"
        }), 403

    caterer = db.session.get(Caterer, caterer_id)

    if not caterer:
        return jsonify({
            "error": "Caterer not found"
        }), 404

    if caterer.user_id != user.id:
        return jsonify({
            "error": "You are not authorized to update this profile"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    if not data:
        return jsonify({
            "error": "No update data provided"
        }), 400

    if "user_id" in data:
        return jsonify({
            "error": "You cannot change profile ownership"
        }), 403

    if "verification_status" in data:
        return jsonify({
            "error": "You cannot change verification status"
        }), 400

    try:
        validated_data = caterer_schema.load(
            data,
            partial=True
        )

        validated_data.pop("user_id", None)
        validated_data.pop("verification_status", None)

        for field, value in validated_data.items():
            setattr(caterer, field, value)

        db.session.commit()

        return jsonify({
            "message": "Caterer updated successfully",
            "data": serialize_caterer(caterer)
        }), 200

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Database conflict"
        }), 409


# --------------------------------------------------
# DELETE CATERER PROFILE - OWNER ONLY
# --------------------------------------------------

@caterer_bp.route("/api/caterers/<int:caterer_id>", methods=["DELETE"])
@jwt_required()
def delete_caterer(caterer_id):

    user = get_authenticated_user()

    if user is None:
        return jsonify({
            "error": "Invalid or outdated user identity"
        }), 401

    if user.role != "caterer":
        return jsonify({
            "error": "Only caterers can delete caterer profiles"
        }), 403

    caterer = db.session.get(Caterer, caterer_id)

    if not caterer:
        return jsonify({
            "error": "Caterer not found"
        }), 404

    if caterer.user_id != user.id:
        return jsonify({
            "error": "You are not authorized to delete this profile"
        }), 403

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
