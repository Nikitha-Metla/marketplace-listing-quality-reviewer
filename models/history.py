from extensions import db
from datetime import datetime


class ReviewHistory(db.Model):

    __tablename__ = "review_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    listing_id = db.Column(
        db.Integer,
        nullable=False
    )

    field = db.Column(
        db.String(100),
        nullable=False
    )

    original_value = db.Column(
        db.Text,
        nullable=True
    )

    revised_value = db.Column(
        db.Text,
        nullable=True
    )

    action = db.Column(
        db.String(30),
        nullable=False
    )

    reviewer = db.Column(
        db.String(150),
        default="Reviewer"
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )