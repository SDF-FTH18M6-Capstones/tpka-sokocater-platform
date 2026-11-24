from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import (
    Package,
    Caterer,
    Menu,
    MenuItem,
    PackageItem,
    AddOn,
    PackageAddOn
)
from auth_utils import get_authenticated_user
from schemas.package_schema import PackageSchema


package_bp = Blueprint("packages", __name__)

package_schema = PackageSchema()
packages_schema = PackageSchema(many=True)


# --------------------------------------------------
# CATEGORY RULES
# --------------------------------------------------

ALLOWED_CATEGORIES = {"Food", "Wedding", "Corporate"}

ALLOWED_ADDON_TYPES = {
    "Food": set(),
    "Wedding": {"venue", "chairs", "tables", "materials"},
    "Corporate": {"chairs", "tables"}
}


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_current_caterer():
    """Get the caterer profile belonging to the authenticated user."""

    user = get_authenticated_user()

    if user is None or user.role != "caterer":
        return None

    return Caterer.query.filter_by(
        user_id=user.id
    ).first()


def serialize_package(package):
    """Serialize a package, including its food items and add-ons."""

    package_data = package_schema.dump(package)

    package_data["menu_items"] = [
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

    package_data["addons"] = [
        {
            "id": package_addon.addon.id,
            "addon_name": package_addon.addon.addon_name,
            "description": package_addon.addon.description,
            "price": str(package_addon.addon.price),
            "addon_type": package_addon.addon.addon_type
        }
        for package_addon in package.package_addons
        if package_addon.addon is not None
    ]

    package_data["addon_ids"] = [
        package_addon.addon_id
        for package_addon in package.package_addons
    ]

    return package_data


def validate_caterer_category(caterer):
    """Ensure the caterer has one of the supported categories."""

    if caterer.category not in ALLOWED_CATEGORIES:
        raise ValidationError({
            "category": [
                "Your catering profile must have a valid category "
                "before you can manage packages."
            ]
        })


def validate_menu_item_ids(menu_item_ids, caterer_id):
    """
    Validate that menu item IDs are unique positive integers
    and that every selected menu item belongs to this caterer.
    """

    if not isinstance(menu_item_ids, list):
        raise ValidationError({
            "menu_item_ids": ["Must be a list of menu item IDs."]
        })

    if any(
        isinstance(item_id, bool)
        or not isinstance(item_id, int)
        or item_id < 1
        for item_id in menu_item_ids
    ):
        raise ValidationError({
            "menu_item_ids": [
                "Every menu item ID must be a positive integer."
            ]
        })

    if len(menu_item_ids) != len(set(menu_item_ids)):
        raise ValidationError({
            "menu_item_ids": [
                "Duplicate menu item IDs are not allowed."
            ]
        })

    if not menu_item_ids:
        return []

    menu_items = (
        MenuItem.query
        .join(Menu, MenuItem.menu_id == Menu.id)
        .filter(
            MenuItem.id.in_(menu_item_ids),
            Menu.caterer_id == caterer_id
        )
        .all()
    )

    if len(menu_items) != len(menu_item_ids):
        raise ValidationError({
            "menu_item_ids": [
                "One or more menu items do not exist or do not belong "
                "to your catering profile."
            ]
        })

    return menu_items


def validate_addon_ids(addon_ids, caterer):
    """
    Validate add-on IDs and enforce the caterer's category rules.

    Every selected add-on must:
    - Have a unique positive integer ID.
    - Belong to the authenticated caterer.
    - Have a component type allowed for that caterer's category.
    """

    if not isinstance(addon_ids, list):
        raise ValidationError({
            "addon_ids": ["Must be a list of add-on IDs."]
        })

    if any(
        isinstance(addon_id, bool)
        or not isinstance(addon_id, int)
        or addon_id < 1
        for addon_id in addon_ids
    ):
        raise ValidationError({
            "addon_ids": [
                "Every add-on ID must be a positive integer."
            ]
        })

    if len(addon_ids) != len(set(addon_ids)):
        raise ValidationError({
            "addon_ids": [
                "Duplicate add-on IDs are not allowed."
            ]
        })

    validate_caterer_category(caterer)

    if not addon_ids:
        return []

    allowed_types = ALLOWED_ADDON_TYPES[caterer.category]

    if not allowed_types:
        raise ValidationError({
            "addon_ids": [
                "Food caterers can only include food/menu items "
                "in their packages."
            ]
        })

    addons = AddOn.query.filter(
        AddOn.id.in_(addon_ids),
        AddOn.caterer_id == caterer.id
    ).all()

    if len(addons) != len(addon_ids):
        raise ValidationError({
            "addon_ids": [
                "One or more add-ons do not exist or do not belong "
                "to your catering profile."
            ]
        })

    invalid_addons = [
        addon.addon_name
        for addon in addons
        if addon.addon_type not in allowed_types
    ]

    if invalid_addons:
        raise ValidationError({
            "addon_ids": [
                f"These add-ons are not allowed for the "
                f"{caterer.category} category: "
                f"{', '.join(invalid_addons)}."
            ]
        })

    return addons


def replace_package_menu_items(package, menu_items):
    """Replace the menu item associations for a package."""

    PackageItem.query.filter_by(
        package_id=package.id
    ).delete(synchronize_session=False)

    for menu_item in menu_items:
        db.session.add(
            PackageItem(
                package_id=package.id,
                menu_item_id=menu_item.id
            )
        )


def replace_package_addons(package, addons):
    """Replace the add-on associations for a package."""

    PackageAddOn.query.filter_by(
        package_id=package.id
    ).delete(synchronize_session=False)

    for addon in addons:
        db.session.add(
            PackageAddOn(
                package_id=package.id,
                addon_id=addon.id
            )
        )


# --------------------------------------------------
# GET ALL PACKAGES - PUBLIC
# --------------------------------------------------

@package_bp.route("/api/packages", methods=["GET"])
def get_packages():

    packages = Package.query.all()

    return jsonify({
        "message": "Packages retrieved successfully",
        "data": [
            serialize_package(package)
            for package in packages
        ]
    }), 200


# --------------------------------------------------
# GET SINGLE PACKAGE - PUBLIC
# --------------------------------------------------

@package_bp.route("/api/packages/<int:package_id>", methods=["GET"])
def get_package(package_id):

    package = db.session.get(Package, package_id)

    if not package:
        return jsonify({
            "error": "Package not found"
        }), 404

    return jsonify({
        "data": serialize_package(package)
    }), 200


# --------------------------------------------------
# CREATE PACKAGE - CATERER ONLY
# --------------------------------------------------

@package_bp.route("/api/packages", methods=["POST"])
@jwt_required()
def create_package():

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can create packages"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    data = dict(data)

    if (
        "caterer_id" in data
        and data["caterer_id"] != current_caterer.id
    ):
        return jsonify({
            "error": "You can only create packages for your own profile"
        }), 403

    try:
        menu_item_ids = data.pop("menu_item_ids", [])
        addon_ids = data.pop("addon_ids", [])

        validate_caterer_category(current_caterer)

        data["caterer_id"] = current_caterer.id

        validated_data = package_schema.load(data)

        validated_data.pop("caterer_id", None)

        menu_items = validate_menu_item_ids(
            menu_item_ids,
            current_caterer.id
        )

        addons = validate_addon_ids(
            addon_ids,
            current_caterer
        )

        package = Package(
            **validated_data,
            caterer_id=current_caterer.id
        )

        db.session.add(package)
        db.session.flush()

        replace_package_menu_items(package, menu_items)
        replace_package_addons(package, addons)

        db.session.commit()

        return jsonify({
            "message": "Package created successfully",
            "data": serialize_package(package)
        }), 201

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to create package"
        }), 409


# --------------------------------------------------
# UPDATE PACKAGE - OWNER ONLY
# --------------------------------------------------

@package_bp.route("/api/packages/<int:package_id>", methods=["PUT"])
@jwt_required()
def update_package(package_id):

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can update packages"
        }), 403

    package = db.session.get(Package, package_id)

    if not package:
        return jsonify({
            "error": "Package not found"
        }), 404

    if package.caterer_id != current_caterer.id:
        return jsonify({
            "error": "You can only update your own packages"
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

    data = dict(data)

    if "caterer_id" in data:
        return jsonify({
            "error": "You cannot transfer a package to another caterer"
        }), 403

    try:
        menu_items_provided = "menu_item_ids" in data
        menu_item_ids = data.pop("menu_item_ids", None)

        addons_provided = "addon_ids" in data
        addon_ids = data.pop("addon_ids", None)

        validated_data = package_schema.load(
            data,
            partial=True
        )

        validated_data.pop("caterer_id", None)

        new_minimum_guests = validated_data.get(
            "minimum_guests",
            package.minimum_guests
        )

        new_maximum_guests = validated_data.get(
            "maximum_guests",
            package.maximum_guests
        )

        if (
            new_maximum_guests is not None
            and new_maximum_guests < new_minimum_guests
        ):
            return jsonify({
                "error": {
                    "maximum_guests": [
                        "Maximum guests must be greater than or equal "
                        "to minimum guests."
                    ]
                }
            }), 400

        menu_items = None
        addons = None

        if menu_items_provided:
            menu_items = validate_menu_item_ids(
                menu_item_ids,
                current_caterer.id
            )

        if addons_provided:
            addons = validate_addon_ids(
                addon_ids,
                current_caterer
            )

        for field, value in validated_data.items():
            setattr(package, field, value)

        if menu_items_provided:
            replace_package_menu_items(package, menu_items)

        if addons_provided:
            replace_package_addons(package, addons)

        db.session.commit()

        return jsonify({
            "message": "Package updated successfully",
            "data": serialize_package(package)
        }), 200

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to update package"
        }), 409


# --------------------------------------------------
# DELETE PACKAGE - OWNER ONLY
# --------------------------------------------------

@package_bp.route("/api/packages/<int:package_id>", methods=["DELETE"])
@jwt_required()
def delete_package(package_id):

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can delete packages"
        }), 403

    package = db.session.get(Package, package_id)

    if not package:
        return jsonify({
            "error": "Package not found"
        }), 404

    if package.caterer_id != current_caterer.id:
        return jsonify({
            "error": "You can only delete your own packages"
        }), 403

    try:
        db.session.delete(package)
        db.session.commit()

        return jsonify({
            "message": "Package deleted successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Cannot delete package because related records exist"
        }), 409