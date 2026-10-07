from extensions import db
from datetime import datetime


class Listing(db.Model):

    __tablename__ = "listings"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    attributes = db.Column(
        db.Text,
        nullable=True
    )

    seller = db.Column(
        db.String(150),
        nullable=False
    )

    tags = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    reviews = db.relationship(
        "Review",
        backref="listing",
        lazy=True,
        cascade="all, delete-orphan"
    )