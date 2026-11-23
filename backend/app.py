import os

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


def create_app(test_config=None):
    app = Flask(__name__)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173"
                ]
            }
        },
        supports_credentials=True
    )

    os.makedirs(app.instance_path, exist_ok=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sokocater.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "JWT_SECRET_KEY",
        "sokocater-development-secret-key"
    )

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

    if test_config:
        app.config.update(test_config)

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

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "message": "SokoCater backend is running"
        }), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
