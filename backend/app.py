
import os
import secrets

from flask import Flask, jsonify
from flask_cors import CORS

from extensions import db, jwt
import models

from routes.auth_routes import auth_bp
from routes.caterer_routes import caterer_bp
from routes.menu_routes import menu_bp
from routes.menu_item_routes import menu_item_bp
from routes.addon_routes import addon_bp
from routes.cuisine_routes import cuisine_bp, caterer_cuisine_bp
from routes.package_routes import package_bp
from routes.availability_routes import availability_bp
from routes.booking_routes import booking_bp
from routes.payment_routes import payment_bp
from routes.notification_routes import notification_bp
from routes.review_routes import review_bp


def create_app(test_config=None):
    app = Flask(__name__)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                    "http://localhost:5174",
                    "http://127.0.0.1:5174",
                    "http://localhost:5175",
                    "http://127.0.0.1:5175",
                    "http://localhost:5176",
                    "http://127.0.0.1:5176",
                    "http://localhost:5177",
                    "http://127.0.0.1:5177",
                    "http://localhost:5178",
                    "http://127.0.0.1:5178",
                ]
            }
        },
        supports_credentials=True,
    )

    os.makedirs(app.instance_path, exist_ok=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sokocater.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Never use a predictable hardcoded JWT secret.
    app_environment = os.environ.get(
        "APP_ENV", "development"
    ).strip().lower()

    jwt_secret = os.environ.get("JWT_SECRET_KEY", "").strip()

    # Production must provide its own secret.
    if app_environment == "production" and not jwt_secret:
        raise RuntimeError(
            "JWT_SECRET_KEY must be configured in production."
        )

    # Local development gets a temporary random secret.
    # Tokens become invalid when the application restarts.
    app.config["JWT_SECRET_KEY"] = (
        jwt_secret if jwt_secret else secrets.token_hex(32)
    )

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

    app.config["PAYMENTS_SIMULATION_ENABLED"] = (
        os.environ.get(
            "PAYMENTS_SIMULATION_ENABLED", "false"
        ).strip().lower() == "true"
    )

    if test_config:
        app.config.update(test_config)

    # Enable simulated payments automatically in tests.
    if app.config.get("TESTING"):
        app.config["PAYMENTS_SIMULATION_ENABLED"] = True

    db.init_app(app)
    jwt.init_app(app)

    # Register API blueprints.
    app.register_blueprint(auth_bp)
    app.register_blueprint(caterer_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(menu_item_bp)
    app.register_blueprint(addon_bp)
    app.register_blueprint(cuisine_bp)
    app.register_blueprint(caterer_cuisine_bp)
    app.register_blueprint(package_bp)
    app.register_blueprint(availability_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(review_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "message": "SokoCater backend is running",
        }), 200

    return app


app = create_app()


if __name__ == "__main__":
    debug_enabled = (
        os.environ.get("FLASK_DEBUG", "false").strip().lower()
        in {"1", "true", "yes"}
        and os.environ.get("APP_ENV", "development").strip().lower()
        != "production"
    )

    app.run(debug=debug_enabled)
