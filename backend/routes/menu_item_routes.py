
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import MenuItem, Menu, Caterer
from auth_utils import get_authenticated_user
from schemas.menu_item_schema import MenuItemSchema


menu_item_bp = Blueprint("menu_items", __name__)

menu_item_schema = MenuItemSchema()
menu_items_schema = MenuItemSchema(many=True)


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
# GET ALL MENU ITEMS - PUBLIC
# ==================================================

@menu_item_bp.route("/api/menu-items", methods=["GET"])
def get_menu_items():

    menu_items = MenuItem.query.all()

    return jsonify({
        "message": "Menu items retrieved successfully",
        "data": menu_items_schema.dump(menu_items)
    }), 200


# ==================================================
# GET SINGLE MENU ITEM - PUBLIC
# ==================================================

@menu_item_bp.route("/api/menu-items/<int:item_id>", methods=["GET"])
def get_menu_item(item_id):

    menu_item = db.session.get(MenuItem, item_id)

    if not menu_item:
        return jsonify({
            "error": "Menu item not found"
        }), 404

    return jsonify({
        "data": menu_item_schema.dump(menu_item)
    }), 200


# ==================================================
# CREATE MENU ITEM - CATERER ONLY
# ==================================================

@menu_item_bp.route("/api/menu-items", methods=["POST"])
@jwt_required()
def create_menu_item():

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can create menu items"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        validated_data = menu_item_schema.load(data)

        menu = db.session.get(
            Menu,
            validated_data["menu_id"]
        )

        if not menu:
            return jsonify({
                "error": "Menu not found"
            }), 404

        if menu.caterer_id != current_caterer.id:
            return jsonify({
                "error": "You can only add items to your own menus"
            }), 403

        menu_item = MenuItem(**validated_data)

        db.session.add(menu_item)
        db.session.commit()

        return jsonify({
            "message": "Menu item created successfully",
            "data": menu_item_schema.dump(menu_item)
        }), 201

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to create menu item"
        }), 409


# ==================================================
# UPDATE MENU ITEM - OWNER ONLY
# ==================================================

@menu_item_bp.route("/api/menu-items/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_menu_item(item_id):

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can update menu items"
        }), 403

    menu_item = db.session.get(MenuItem, item_id)

    if not menu_item:
        return jsonify({
            "error": "Menu item not found"
        }), 404

    if menu_item.menu.caterer_id != current_caterer.id:
        return jsonify({
            "error": "You can only update your own menu items"
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
        validated_data = menu_item_schema.load(
            data,
            partial=True
        )

        # Menu items cannot be transferred to another menu.
        if (
            "menu_id" in validated_data
            and validated_data["menu_id"] != menu_item.menu_id
        ):
            return jsonify({
                "error": "You cannot transfer a menu item to another menu"
            }), 403

        for field, value in validated_data.items():
            setattr(menu_item, field, value)

        db.session.commit()

        return jsonify({
            "message": "Menu item updated successfully",
            "data": menu_item_schema.dump(menu_item)
        }), 200

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to update menu item"
        }), 409


# ==================================================
# DELETE MENU ITEM - OWNER ONLY
# ==================================================

@menu_item_bp.route("/api/menu-items/<int:item_id>", methods=["DELETE"])
@jwt_required()
def delete_menu_item(item_id):

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can delete menu items"
        }), 403

    menu_item = db.session.get(MenuItem, item_id)

    if not menu_item:
        return jsonify({
            "error": "Menu item not found"
        }), 404

    if menu_item.menu.caterer_id != current_caterer.id:
        return jsonify({
            "error": "You can only delete your own menu items"
        }), 403

    try:
        db.session.delete(menu_item)
        db.session.commit()

        return jsonify({
            "message": "Menu item deleted successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Cannot delete menu item because related records exist"
        }), 409
