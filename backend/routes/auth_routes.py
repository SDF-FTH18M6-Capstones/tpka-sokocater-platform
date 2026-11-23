from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User
from schemas.auth_schema import RegisterSchema, LoginSchema


auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()


def _flat_error(err_messages):
    """Convert Marshmallow validation errors into readable text."""
    parts = []

    for field, messages in err_messages.items():
        if isinstance(messages, list):
            parts.append(
                f"{field}: {', '.join(str(message) for message in messages)}"
            )
        else:
            parts.append(f"{field}: {messages}")

    return " | ".join(parts) if parts else "Validation failed"


# ============================================================
# REGISTER
# ============================================================

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    # Support both full_name and name from frontend requests.
    data = data.copy()

    if "full_name" not in data and "name" in data:
        data["full_name"] = data["name"]

    try:
        validated_data = register_schema.load(data)

        email = validated_data["email"]

        # Check whether the email is already registered.
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return jsonify({
                "error": "Email already registered"
            }), 409

        # Hash the password before storing it.
        hashed_password = generate_password_hash(
            validated_data["password"]
        )

        # Create the new user.
        user = User(
            full_name=validated_data["full_name"],
            email=email,
            password_hash=hashed_password,
            phone_number=validated_data.get("phone_number"),
            role=validated_data["role"]
        )

        db.session.add(user)
        db.session.commit()

        # Generate JWT access token.
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role
            }
        )

        return jsonify({
            "message": "User registered successfully",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role
            }
        }), 201

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": _flat_error(error.messages)
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Email already registered"
        }), 409


# ============================================================
# LOGIN
# ============================================================

@auth_bp.route("/api/auth/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        validated_data = login_schema.load(data)

        email = validated_data["email"]
        password = validated_data["password"]

        # Find user using normalized email.
        user = User.query.filter_by(email=email).first()

        # Verify user and password.
        if not user or not check_password_hash(
            user.password_hash,
            password
        ):
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        # Generate JWT access token.
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role
            }
        )

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role
            }
        }), 200

    except ValidationError as error:
        return jsonify({
            "error": _flat_error(error.messages)
        }), 400
