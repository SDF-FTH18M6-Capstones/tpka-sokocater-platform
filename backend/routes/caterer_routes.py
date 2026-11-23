from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import User, Caterer, Package
from schemas.caterer_schema import CatererSchema

caterer_bp = Blueprint("caterers", __name__)

caterer_schema = CatererSchema()
caterers_schema = CatererSchema(many=True)


# ============================================================
# GET ALL CATERERS
# PUBLIC - supports ?min_price=&max_price=
# ============================================================

@caterer_bp.route("/api/caterers", methods=["GET"])
def get_caterers():
    # #4: Filter caterers by package price_per_guest
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")

    try:
        min_price = float(min_price) if min_price is not None else None
        max_price = float(max_price) if max_price is not None else None
    except ValueError:
        return jsonify({
            "error": "min_price and max_price must be numbers"
        }), 400

    if min_price is not None and min_price < 0:
        return jsonify({"error": "min_price cannot be negative"}), 400
    if max_price is not None and max_price < 0:
        return jsonify({"error": "max_price cannot be negative"}), 400
    if min_price is not None and max_price is not None and min_price > max_price:
        return jsonify({"error": "min_price cannot be greater than max_price"}), 400

    query = Caterer.query

    if min_price is not None or max_price is not None:
        query = query.join(Package, Package.caterer_id == Caterer.id)
        if min_price is not None:
            query = query.filter(Package.price_per_guest >= min_price)
        if max_price is not None:
            query = query.filter(Package.price_per_guest <= max_price)
        query = query.distinct()

    caterers = query.all()

    return jsonify({
        "message": "Caterers retrieved successfully",
        "data": caterers_schema.dump(caterers)
    }), 200
# ============================================================
# GET ONE CATERER
# PUBLIC
# ============================================================

@caterer_bp.route("/api/caterers/<int:caterer_id>", methods=["GET"])
def get_caterer(caterer_id):

    caterer = db.session.get(Caterer, caterer_id)

    if not caterer:
        return jsonify({
            "error": "Caterer not found"
        }), 404

        # #5: Include packages with their menu items
    data = caterer_schema.dump(caterer)

    packages_data = []
    for package in caterer.packages:
        menu_items = []
        for item in package.package_items:
            mi = item.menu_item
            if mi:
                menu_items.append({
                    "id": mi.id,
                    "item_name": mi.item_name,
                    "description": mi.description,
                    "price": float(mi.price) if mi.price is not None else None,
                    "image_url": mi.image_url,
                })

        packages_data.append({
            "id": package.id,
            "package_name": package.package_name,
            "description": package.description,
            "price_per_guest": float(package.price_per_guest) if package.price_per_guest is not None else None,
            "minimum_guests": package.minimum_guests,
            "maximum_guests": package.maximum_guests,
            "menu_items": menu_items,
            # alias for frontend that expects "menus"
            "menus": menu_items,
        })

    data["packages"] = packages_data

    return jsonify({
        "data": data
    }), 200

# ============================================================
# CREATE CATERER PROFILE
# CATERER ONLY
# ============================================================

@caterer_bp.route("/api/caterers", methods=["POST"])
@jwt_required()
def create_caterer():

    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")

    if current_role != "caterer":
        return jsonify({
            "error": "Only caterers can create caterer profiles"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        validated_data = caterer_schema.load(data)

        # FIX 1: Remove verification_status if schema sent it, to avoid duplicate kwarg crash
        validated_data.pop("verification_status", None)

        if validated_data.get("user_id") != current_user_id:
            return jsonify({
                "error": "You can only create a profile for yourself"
            }), 403

        user = db.session.get(User, current_user_id)

        if not user:
            return jsonify({
                "error": "User not found"
            }), 404

        if user.role != "caterer":
            return jsonify({
                "error": "User must have a caterer role"
            }), 403

        existing_caterer = Caterer.query.filter_by(
            user_id=current_user_id
        ).first()

        if existing_caterer:
            return jsonify({
                "error": "You already have a caterer profile"
            }), 409

        # New profiles must start with pending verification.
        # The client cannot choose its own verification status.
        caterer = Caterer(
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
        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "A caterer profile already exists for this user"
        }), 409

# ============================================================
# UPDATE CATERER PROFILE
# CATERER ONLY - OWN PROFILE
# ============================================================

@caterer_bp.route("/api/caterers/<int:caterer_id>", methods=["PUT"])
@jwt_required()
def update_caterer(caterer_id):

    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")

    if current_role != "caterer":
        return jsonify({
            "error": "Only caterers can update caterer profiles"
        }), 403

    caterer = db.session.get(Caterer, caterer_id)

    if not caterer:
        return jsonify({
            "error": "Caterer not found"
        }), 404

    if caterer.user_id != current_user_id:
        return jsonify({
            "error": "You are not authorized to update this profile"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        if "user_id" in data:
            return jsonify({
                "error": "You cannot change profile ownership"
            }), 403

        # FIX 2: Block self-verification on update
        if "verification_status" in data:
            return jsonify({
                "error": "You cannot change verification status"
            }), 403

        validated_data = caterer_schema.load(
            data,
            partial=True
        )

        # Extra safety: never allow it even if schema passes it
        validated_data.pop("verification_status", None)
        validated_data.pop("user_id", None)

        for field, value in validated_data.items():
            setattr(caterer, field, value)

        db.session.commit()

        return jsonify({
            "message": "Caterer updated successfully",
            "data": caterer_schema.dump(caterer)
        }), 200

    except ValidationError as error:
        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Database conflict"
        }), 409

# ============================================================
# DELETE CATERER PROFILE
# CATERER ONLY - OWN PROFILE
# ============================================================

@caterer_bp.route("/api/caterers/<int:caterer_id>", methods=["DELETE"])
@jwt_required()
def delete_caterer(caterer_id):

    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")

    if current_role != "caterer":
        return jsonify({
            "error": "Only caterers can delete caterer profiles"
        }), 403

    caterer = db.session.get(Caterer, caterer_id)

    if not caterer:
        return jsonify({
            "error": "Caterer not found"
        }), 404

    if caterer.user_id != current_user_id:
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