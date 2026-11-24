from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import AddOn, Caterer
from auth_utils import get_authenticated_user
from schemas.addon_schema import (
    AddOnSchema,
    ALLOWED_ADDON_TYPES
)


addon_bp = Blueprint("addons", __name__)

addon_schema = AddOnSchema()
addons_schema = AddOnSchema(many=True)


# ==================================================
# CATEGORY AND COMPONENT RULES
# ==================================================

ALLOWED_ADDON_TYPES_BY_CATEGORY = {
    "Food": set(),
    "Wedding": {
        "venue",
        "chairs",
        "tables",
        "materials"
    },
    "Corporate": {
        "chairs",
        "tables"
    }
}


def validate_addon_type_for_category(addon_type, category):

    # Untyped add-ons remain supported for existing standalone
    # services such as juice service and waiter service.
    if addon_type is None:
        return None

    if addon_type not in ALLOWED_ADDON_TYPES:
        return "Invalid add-on type."

    # Older test records and legacy caterer profiles may not
    # have a category assigned yet. The type itself is still
    # checked above.
    if category is None:
        return None

    if category not in ALLOWED_ADDON_TYPES_BY_CATEGORY:
        return "Caterer has an invalid category."

    allowed_types = ALLOWED_ADDON_TYPES_BY_CATEGORY[category]

    if addon_type not in allowed_types:
        if category == "Food":
            return "Food caterers cannot create non-food package components."

        if category == "Corporate":
            return "Corporate caterers can only offer chairs and tables as components."

        return "This add-on type is not allowed for this caterer category."

    return None


# ==================================================
# HELPER FUNCTION
# ==================================================

def get_current_caterer():

    user = get_authenticated_user()

    if user is None or user.role != "caterer":
        return None

    return Caterer.query.filter_by(
        user_id=user.id
    ).first()


# ==================================================
# GET ALL ADD-ONS - PUBLIC
# ==================================================

@addon_bp.route("/api/addons", methods=["GET"])
def get_addons():

    addons = AddOn.query.all()

    return jsonify({
        "message": "Add-ons retrieved successfully",
        "data": addons_schema.dump(addons)
    }), 200


# ==================================================
# GET SINGLE ADD-ON - PUBLIC
# ==================================================

@addon_bp.route("/api/addons/<int:addon_id>", methods=["GET"])
def get_addon(addon_id):

    addon = db.session.get(AddOn, addon_id)

    if not addon:
        return jsonify({
            "error": "Add-on not found"
        }), 404

    return jsonify({
        "data": addon_schema.dump(addon)
    }), 200


# ==================================================
# CREATE ADD-ON - CATERER ONLY
# ==================================================

@addon_bp.route("/api/addons", methods=["POST"])
@jwt_required()
def create_addon():

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can create add-ons"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        validated_data = addon_schema.load(data)

        if validated_data["caterer_id"] != current_caterer.id:
            return jsonify({
                "error": "You can only create add-ons for your own profile"
            }), 403

        addon_type_error = validate_addon_type_for_category(
            validated_data.get("addon_type"),
            current_caterer.category
        )

        if addon_type_error:
            return jsonify({
                "error": addon_type_error
            }), 400

        addon = AddOn(**validated_data)

        db.session.add(addon)
        db.session.commit()

        return jsonify({
            "message": "Add-on created successfully",
            "data": addon_schema.dump(addon)
        }), 201

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to create add-on"
        }), 409


# ==================================================
# UPDATE ADD-ON - OWNER ONLY
# ==================================================

@addon_bp.route("/api/addons/<int:addon_id>", methods=["PUT"])
@jwt_required()
def update_addon(addon_id):

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can update add-ons"
        }), 403

    addon = db.session.get(AddOn, addon_id)

    if not addon:
        return jsonify({
            "error": "Add-on not found"
        }), 404

    if addon.caterer_id != current_caterer.id:
        return jsonify({
            "error": "You can only update your own add-ons"
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
        validated_data = addon_schema.load(
            data,
            partial=True
        )

        if (
            "caterer_id" in validated_data
            and validated_data["caterer_id"] != current_caterer.id
        ):
            return jsonify({
                "error": "You cannot transfer an add-on to another caterer"
            }), 403

        # Validate the final type, not only the fields in this request.
        # This also protects updates to existing typed add-ons.
        final_addon_type = validated_data.get(
            "addon_type",
            addon.addon_type
        )

        addon_type_error = validate_addon_type_for_category(
            final_addon_type,
            current_caterer.category
        )

        if addon_type_error:
            return jsonify({
                "error": addon_type_error
            }), 400

        for field, value in validated_data.items():
            setattr(addon, field, value)

        db.session.commit()

        return jsonify({
            "message": "Add-on updated successfully",
            "data": addon_schema.dump(addon)
        }), 200

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to update add-on"
        }), 409


# ==================================================
# DELETE ADD-ON - OWNER ONLY
# ==================================================

@addon_bp.route("/api/addons/<int:addon_id>", methods=["DELETE"])
@jwt_required()
def delete_addon(addon_id):

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can delete add-ons"
        }), 403

    addon = db.session.get(AddOn, addon_id)

    if not addon:
        return jsonify({
            "error": "Add-on not found"
        }), 404

    if addon.caterer_id != current_caterer.id:
        return jsonify({
            "error": "You can only delete your own add-ons"
        }), 403

    try:
        db.session.delete(addon)
        db.session.commit()

        return jsonify({
            "message": "Add-on deleted successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Cannot delete add-on because related records exist"
        }), 409