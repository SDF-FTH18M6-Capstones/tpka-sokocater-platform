from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import User, Caterer
from schemas.caterer_schema import CatererSchema


caterer_bp = Blueprint("caterers", __name__)

caterer_schema = CatererSchema()
caterers_schema = CatererSchema(many=True)


def get_current_user_id():
    """Safely convert the JWT identity into an integer user ID."""
    identity = get_jwt_identity()

    try:
        return int(identity)
    except (TypeError, ValueError):
        return None


# ============================================================
# GET ALL CATERERS
# PUBLIC
# ============================================================

@caterer_bp.route("/api/caterers", methods=["GET"])
def get_caterers():
    caterers = Caterer.query.all()

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

    return jsonify({
        "data": caterer_schema.dump(caterer)
    }), 200


# ============================================================
# CREATE CATERER PROFILE
# CATERER ONLY
# ============================================================

@caterer_bp.route("/api/caterers", methods=["POST"])
@jwt_required()
def create_caterer():
    current_user_id = get_current_user_id()
    current_role = get_jwt().get("role")

    if current_user_id is None:
        return jsonify({
            "error": "Invalid user identity"
        }), 401

    if current_role != "caterer":
        return jsonify({
            "error": "Only caterers can create caterer profiles"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    # Caterers cannot choose their own verification status.
    if "verification_status" in data:
        return jsonify({
            "error": "You cannot set your own verification status"
        }), 403

    try:
        validated_data = caterer_schema.load(data)

        if validated_data["user_id"] != current_user_id:
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

        # Every new caterer profile starts as pending.
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
        db.session.rollback()

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
    current_user_id = get_current_user_id()
    current_role = get_jwt().get("role")

    if current_user_id is None:
        return jsonify({
            "error": "Invalid user identity"
        }), 401

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

    if not data:
        return jsonify({
            "error": "No update data provided"
        }), 400

    if "user_id" in data:
        return jsonify({
            "error": "You cannot change profile ownership"
        }), 403

    # Caterers cannot approve or reject their own profiles.
    if "verification_status" in data:
        return jsonify({
            "error": "You cannot change verification status"
        }), 403

    try:
        validated_data = caterer_schema.load(
            data,
            partial=True
        )

        # Extra protection against changing ownership or verification.
        validated_data.pop("user_id", None)
        validated_data.pop("verification_status", None)

        for field, value in validated_data.items():
            setattr(caterer, field, value)

        db.session.commit()

        return jsonify({
            "message": "Caterer updated successfully",
            "data": caterer_schema.dump(caterer)
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


# ============================================================
# DELETE CATERER PROFILE
# CATERER ONLY - OWN PROFILE
# ============================================================

@caterer_bp.route("/api/caterers/<int:caterer_id>", methods=["DELETE"])
@jwt_required()
def delete_caterer(caterer_id):
    current_user_id = get_current_user_id()
    current_role = get_jwt().get("role")

    if current_user_id is None:
        return jsonify({
            "error": "Invalid user identity"
        }), 401

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

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import User, Caterer
from schemas.caterer_schema import CatererSchema
from schemas.package_schema import PackageSchema


caterer_bp = Blueprint("caterers", __name__)

caterer_schema = CatererSchema()
caterers_schema = CatererSchema(many=True)
package_schema = PackageSchema()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_current_user_id():
    """Safely convert the JWT identity into an integer user ID."""
    identity = get_jwt_identity()

    try:
        return int(identity)
    except (TypeError, ValueError):
        return None


def serialize_package(package):
    """Return package information together with its menu items."""

    package_data = package_schema.dump(package)

    menu_items = []

    for package_item in package.package_items:
        menu_item = package_item.menu_item

        if menu_item:
            menu_items.append({
                "id": menu_item.id,
                "item_name": menu_item.item_name,
                "description": menu_item.description,
                "price": format(menu_item.price, ".2f"),
                "image_url": menu_item.image_url
            })

    package_data["menu_items"] = menu_items

    return package_data


def get_caterer_price_range(packages):
    """Calculate minimum and maximum package prices."""

    if not packages:
        return {
            "min_price": None,
            "max_price": None
        }

    prices = [
        package.price_per_guest
        for package in packages
    ]

    return {
        "min_price": format(min(prices), ".2f"),
        "max_price": format(max(prices), ".2f")
    }


# ============================================================
# GET ALL CATERERS
# PUBLIC
# ============================================================

@caterer_bp.route("/api/caterers", methods=["GET"])
def get_caterers():

    caterers = Caterer.query.all()

    return jsonify({
        "message": "Caterers retrieved successfully",
        "data": caterers_schema.dump(caterers)
    }), 200


# ============================================================
# GET ONE CATERER
# PUBLIC
# Includes packages, menu items and price range
# ============================================================

@caterer_bp.route("/api/caterers/<int:caterer_id>", methods=["GET"])
def get_caterer(caterer_id):

    caterer = db.session.get(Caterer, caterer_id)

    if not caterer:
        return jsonify({
            "error": "Caterer not found"
        }), 404

    packages = caterer.packages

    package_data = [
        serialize_package(package)
        for package in packages
    ]

    price_range = get_caterer_price_range(packages)

    data = caterer_schema.dump(caterer)

    data["packages"] = package_data
    data["price_range"] = price_range

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

    current_user_id = get_current_user_id()
    current_role = get_jwt().get("role")

    if current_user_id is None:
        return jsonify({
            "error": "Invalid user identity"
        }), 401

    if current_role != "caterer":
        return jsonify({
            "error": "Only caterers can create caterer profiles"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    # Caterers cannot choose their own verification status.
    if "verification_status" in data:
        return jsonify({
            "error": "You cannot set your own verification status"
        }), 400

    try:
        validated_data = caterer_schema.load(data)

        if validated_data["user_id"] != current_user_id:
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

        # Every new caterer profile starts as pending.
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
        db.session.rollback()

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

    current_user_id = get_current_user_id()
    current_role = get_jwt().get("role")

    if current_user_id is None:
        return jsonify({
            "error": "Invalid user identity"
        }), 401

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

    if not data:
        return jsonify({
            "error": "No update data provided"
        }), 400

    if "user_id" in data:
        return jsonify({
            "error": "You cannot change profile ownership"
        }), 403

    # Caterers cannot approve or reject their own profiles.
    if "verification_status" in data:
        return jsonify({
            "error": "You cannot change verification status"
        }), 400

    try:
        validated_data = caterer_schema.load(
            data,
            partial=True
        )

        # Extra protection against changing ownership or verification.
        validated_data.pop("user_id", None)
        validated_data.pop("verification_status", None)

        for field, value in validated_data.items():
            setattr(caterer, field, value)

        db.session.commit()

        return jsonify({
            "message": "Caterer updated successfully",
            "data": caterer_schema.dump(caterer)
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


# ============================================================
# DELETE CATERER PROFILE
# CATERER ONLY - OWN PROFILE
# ============================================================

@caterer_bp.route("/api/caterers/<int:caterer_id>", methods=["DELETE"])
@jwt_required()
def delete_caterer(caterer_id):

    current_user_id = get_current_user_id()
    current_role = get_jwt().get("role")

    if current_user_id is None:
        return jsonify({
            "error": "Invalid user identity"
        }), 401

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
