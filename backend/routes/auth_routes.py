from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from extensions import db, bcrypt
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# REGISTER
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "customer")

    if not name or not email or not password:
        return jsonify({"message": "Name, email and password are required"}), 400

    if role not in ["customer", "caterer"]:
        return jsonify({"message": "Invalid role"}), 400

    if len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters"}), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"message": "Email is already registered"}), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(
        full_name=name,
        email=email,
        password_hash=password_hash,
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful",
        "user": {
            "id": new_user.id,
            "name": new_user.full_name,
            "email": new_user.email,
            "role": new_user.role
        }
    }), 201


# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }), 200