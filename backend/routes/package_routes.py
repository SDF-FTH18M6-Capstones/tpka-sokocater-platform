from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import Package, CatererProfile
from schemas.package_schema import PackageSchema

package_bp = Blueprint("packages", __name__)

package_schema = PackageSchema()
packages_schema = PackageSchema(many=True)


@package_bp.route("/api/packages", methods=["GET"])
def get_packages():
    packages = Package.query.all()

    return jsonify({
        "message": "Packages retrieved successfully",
        "data": packages_schema.dump(packages)
    }), 200


@package_bp.route("/api/packages/<int:package_id>", methods=["GET"])
def get_package(package_id):
    package = db.session.get(Package, package_id)

    if not package:
        return jsonify({"error": "Package not found"}), 404

    return jsonify({"data": package_schema.dump(package)}), 200


@package_bp.route("/api/packages", methods=["POST"])
def create_package():
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        validated_data = package_schema.load(data)

        caterer = db.session.get(
            CatererProfile, validated_data["caterer_id"]
        )

        if not caterer:
            return jsonify({"error": "Caterer not found"}), 404

        package = Package(**validated_data)

        db.session.add(package)
        db.session.commit()

        return jsonify({
            "message": "Package created successfully",
            "data": package_schema.dump(package)
        }), 201

    except ValidationError as error:
        return jsonify({"error": error.messages}), 400

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Unable to create package"}), 409


@package_bp.route("/api/packages/<int:package_id>", methods=["PUT"])
def update_package(package_id):
    package = db.session.get(Package, package_id)

    if not package:
        return jsonify({"error": "Package not found"}), 404

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        validated_data = package_schema.load(data, partial=True)

        if "caterer_id" in validated_data:
            caterer = db.session.get(
                CatererProfile, validated_data["caterer_id"]
            )

        if not caterer:
            return jsonify({"error": "Caterer not found"}), 404

        minimum = validated_data.get(
            "minimum_guests", package.minimum_guests
        )

        maximum = validated_data.get(
            "maximum_guests", package.maximum_guests
        )

        if maximum is not None and maximum < minimum:
            return jsonify({
                "error": "Maximum guests cannot be less than minimum guests"
            }), 400

        for field, value in validated_data.items():
            setattr(package, field, value)

        db.session.commit()

        return jsonify({
            "message": "Package updated successfully",
            "data": package_schema.dump(package)
        }), 200

    except ValidationError as error:
        return jsonify({"error": error.messages}), 400

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Unable to update package"}), 409


@package_bp.route("/api/packages/<int:package_id>", methods=["DELETE"])
def delete_package(package_id):
    package = db.session.get(Package, package_id)

    if not package:
        return jsonify({"error": "Package not found"}), 404

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
