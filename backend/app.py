
from flask import Flask, jsonify
import os

from extensions import db


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

    # Import models so SQLAlchemy knows about all database tables
    import models

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
