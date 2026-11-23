
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import Cuisine, CatererCuisine, Caterer
from auth_utils import get_authenticated_user
from schemas.cuisine_schema import CuisineSchema
from schemas.caterer_cuisine_schema import CatererCuisineSchema


cuisine_bp = Blueprint("cuisines", __name__)
caterer_cuisine_bp = Blueprint("caterer_cuisines", __name__)

cuisine_schema = CuisineSchema()
cuisines_schema = CuisineSchema(many=True)

caterer_cuisine_schema = CatererCuisineSchema()
caterer_cuisines_schema = CatererCuisineSchema(many=True)


# ============================================================
# AUTHENTICATION HELPERS
# ============================================================

def get_current_admin():

    user = get_authenticated_user()

    if user is None or user.role != "admin":
        return None

    return user


def get_current_caterer():

    user = get_authenticated_user()

    if user is None or user.role != "caterer":
        return None

    return Caterer.query.filter_by(user_id=user.id).first()


# ============================================================
# CUISINE CATALOGUE
# ============================================================

@cuisine_bp.route("/api/cuisines", methods=["GET"])
def get_cuisines():

    cuisines = Cuisine.query.order_by(
        Cuisine.cuisine_name
    ).all()

    return jsonify(cuisines_schema.dump(cuisines)), 200


@cuisine_bp.route("/api/cuisines", methods=["POST"])
@jwt_required()
def create_cuisine():

    if get_current_admin() is None:
        return jsonify({
            "error": "Admin access required"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        validated_data = cuisine_schema.load(data)

        cuisine_name = validated_data["cuisine_name"].strip()

        existing = Cuisine.query.filter_by(
            cuisine_name=cuisine_name
        ).first()

        if existing:
            return jsonify({
                "error": "Cuisine already exists"
            }), 409

        cuisine = Cuisine(
            cuisine_name=cuisine_name
        )

        db.session.add(cuisine)
        db.session.commit()

        return jsonify({
            "message": "Cuisine created successfully",
            "cuisine": cuisine_schema.dump(cuisine)
        }), 201

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Cuisine already exists"
        }), 409


@cuisine_bp.route(
    "/api/cuisines/<int:cuisine_id>",
    methods=["PUT"]
)
@jwt_required()
def update_cuisine(cuisine_id):

    if get_current_admin() is None:
        return jsonify({
            "error": "Admin access required"
        }), 403

    cuisine = db.session.get(Cuisine, cuisine_id)

    if cuisine is None:
        return jsonify({
            "error": "Cuisine not found"
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "Invalid or empty JSON body"
        }), 400

    try:
        validated_data = cuisine_schema.load(
            data,
            partial=True
        )

        if "cuisine_name" in validated_data:

            cuisine_name = validated_data[
                "cuisine_name"
            ].strip()

            existing = Cuisine.query.filter(
                Cuisine.cuisine_name == cuisine_name,
                Cuisine.id != cuisine_id
            ).first()

            if existing:
                return jsonify({
                    "error": "Cuisine already exists"
                }), 409

            cuisine.cuisine_name = cuisine_name

        db.session.commit()

        return jsonify({
            "message": "Cuisine updated successfully",
            "cuisine": cuisine_schema.dump(cuisine)
        }), 200

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Cuisine already exists"
        }), 409


@cuisine_bp.route(
    "/api/cuisines/<int:cuisine_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_cuisine(cuisine_id):

    if get_current_admin() is None:
        return jsonify({
            "error": "Admin access required"
        }), 403

    cuisine = db.session.get(Cuisine, cuisine_id)

    if cuisine is None:
        return jsonify({
            "error": "Cuisine not found"
        }), 404

    assignment = CatererCuisine.query.filter_by(
        cuisine_id=cuisine_id
    ).first()

    if assignment:
        return jsonify({
            "error": "Cannot delete a cuisine assigned to a caterer"
        }), 409

    try:
        db.session.delete(cuisine)
        db.session.commit()

        return jsonify({
            "message": "Cuisine deleted successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Cannot delete a cuisine that is in use"
        }), 409


# ============================================================
# CATERER CUISINE ASSIGNMENTS
# ============================================================

@caterer_cuisine_bp.route(
    "/api/caterer-cuisines",
    methods=["GET"]
)
def get_caterer_cuisines():

    query = CatererCuisine.query

    caterer_id = request.args.get("caterer_id")

    if caterer_id is not None:

        try:
            caterer_id = int(caterer_id)

            if caterer_id < 1:
                raise ValueError

        except ValueError:
            return jsonify({
                "error": "Invalid caterer_id"
            }), 400

        query = query.filter_by(
            caterer_id=caterer_id
        )

    assignments = query.order_by(
        CatererCuisine.id
    ).all()

    return jsonify(
        caterer_cuisines_schema.dump(assignments)
    ), 200


@caterer_cuisine_bp.route(
    "/api/caterer-cuisines",
    methods=["POST"]
)
@jwt_required()
def assign_cuisine():

    caterer = get_current_caterer()

    if caterer is None:
        return jsonify({
            "error": "Caterer access required"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        validated_data = caterer_cuisine_schema.load(data)

        if validated_data["caterer_id"] != caterer.id:
            return jsonify({
                "error": "You can only assign cuisines to your own profile"
            }), 403

        cuisine = db.session.get(
            Cuisine,
            validated_data["cuisine_id"]
        )

        if cuisine is None:
            return jsonify({
                "error": "Cuisine not found"
            }), 404

        assignment = CatererCuisine(
            caterer_id=caterer.id,
            cuisine_id=cuisine.id
        )

        db.session.add(assignment)
        db.session.commit()

        return jsonify({
            "message": "Cuisine assigned successfully",
            "assignment": caterer_cuisine_schema.dump(
                assignment
            )
        }), 201

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "This cuisine is already assigned to your profile"
        }), 409


@caterer_cuisine_bp.route(
    "/api/caterer-cuisines/<int:assignment_id>",
    methods=["DELETE"]
)
@jwt_required()
def remove_cuisine_assignment(assignment_id):

    caterer = get_current_caterer()

    if caterer is None:
        return jsonify({
            "error": "Caterer access required"
        }), 403

    assignment = db.session.get(
        CatererCuisine,
        assignment_id
    )

    if assignment is None:
        return jsonify({
            "error": "Cuisine assignment not found"
        }), 404

    if assignment.caterer_id != caterer.id:
        return jsonify({
            "error": "You can only remove cuisines from your own profile"
        }), 403

    db.session.delete(assignment)
    db.session.commit()

    return jsonify({
        "message": "Cuisine assignment removed successfully"
    }), 200
