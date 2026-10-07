from flask import Flask, render_template
from dotenv import load_dotenv
import os

from extensions import db


load_dotenv()


def create_app():

    app = Flask(__name__)

    # Secret key
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "development-secret"
    )

    # Database path
    BASE_DIR = os.path.abspath(
        os.path.dirname(__file__)
    )

    DATABASE_DIR = os.path.join(
        BASE_DIR,
        "database"
    )

    os.makedirs(
        DATABASE_DIR,
        exist_ok=True
    )

    DATABASE_PATH = os.path.join(
        DATABASE_DIR,
        "marketplace.db"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + DATABASE_PATH
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database
    db.init_app(app)

    # Import models
    from models import (
        Listing,
        Review,
        Finding,
        ReviewHistory
    )

    # Import routes
    from routes.listings import listings_bp
    from routes.reviews import reviews_bp

    # Register routes
    app.register_blueprint(listings_bp)
    app.register_blueprint(reviews_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=True
    )