from flask import Flask, jsonify
import os

from extensions import db
import models

from routes.caterer_routes import caterer_bp
from routes.menu_routes import menu_bp
from routes.package_routes import package_bp
from routes.booking_routes import booking_bp


def create_app(test_config=None):
    app = Flask(__name__)

    os.makedirs(app.instance_path, exist_ok=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sokocater.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Allow test settings to override the default configuration
    if test_config:
        app.config.update(test_config)

    # Initialize SQLAlchemy
    db.init_app(app)

    # Register all route blueprints
    app.register_blueprint(caterer_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(package_bp)
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