from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import Menu, CatererProfile
from schemas.menu_schema import MenuSchema

menu_bp = Blueprint("menus", __name__)

menu_schema = MenuSchema()
menus_schema = MenuSchema(many=True)


@menu_bp.route("/api/menus", methods=["GET"])
def get_menus():
    menus = Menu.query.all()
    return jsonify({
        "message": "Menus retrieved successfully",
        "data": menus_schema.dump(menus)
    }), 200


@menu_bp.route("/api/menus/<int:menu_id>", methods=["GET"])
def get_menu(menu_id):
    menu = db.session.get(Menu, menu_id)

    if not menu:
        return jsonify({"error": "Menu not found"}), 404

    return jsonify({"data": menu_schema.dump(menu)}), 200


@menu_bp.route("/api/menus", methods=["POST"])
def create_menu():
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        validated_data = menu_schema.load(data)

        caterer = db.session.get(
            CatererProfile, validated_data["caterer_id"]
        )

        if not caterer:
            return jsonify({"error": "Caterer not found"}), 404

        menu = Menu(**validated_data)
        db.session.add(menu)
        db.session.commit()

        return jsonify({
            "message": "Menu created successfully",
            "data": menu_schema.dump(menu)
        }), 201

    except ValidationError as error:
        return jsonify({"error": error.messages}), 400

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Unable to create menu"}), 409


@menu_bp.route("/api/menus/<int:menu_id>", methods=["PUT"])
def update_menu(menu_id):
    menu = db.session.get(Menu, menu_id)

    if not menu:
        return jsonify({"error": "Menu not found"}), 404

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        validated_data = menu_schema.load(data, partial=True)

        if "caterer_id" in validated_data:
            caterer = db.session.get(
                CatererProfile, validated_data["caterer_id"]
            )

            if not caterer:
                return jsonify({"error": "Caterer not found"}), 404

        for field, value in validated_data.items():
            setattr(menu, field, value)

        db.session.commit()

        return jsonify({
            "message": "Menu updated successfully",
            "data": menu_schema.dump(menu)
        }), 200

    except ValidationError as error:
        return jsonify({"error": error.messages}), 400

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Unable to update menu"}), 409


@menu_bp.route("/api/menus/<int:menu_id>", methods=["DELETE"])
def delete_menu(menu_id):
    menu = db.session.get(Menu, menu_id)

    if not menu:
        return jsonify({"error": "Menu not found"}), 404

    try:
        db.session.delete(menu)
        db.session.commit()

        return jsonify({"message": "Menu deleted successfully"}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Cannot delete menu because related records exist"
        }), 409
