from extensions import db
from datetime import datetime


class Review(db.Model):

    __tablename__ = "reviews"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    listing_id = db.Column(
        db.Integer,
        db.ForeignKey("listings.id"),
        nullable=False
    )

    overall_status = db.Column(
        db.String(50),
        default="Pending"
    )

    reviewer = db.Column(
        db.String(150),
        default="System"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    findings = db.relationship(
        "Finding",
        backref="review",
        lazy=True,
        cascade="all, delete-orphan"
    )