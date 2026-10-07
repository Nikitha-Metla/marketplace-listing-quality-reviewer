from extensions import db


class Finding(db.Model):

    __tablename__ = "findings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    review_id = db.Column(
        db.Integer,
        db.ForeignKey("reviews.id"),
        nullable=False
    )

    field = db.Column(
        db.String(100),
        nullable=False
    )

    issue = db.Column(
        db.Text,
        nullable=False
    )

    severity = db.Column(
        db.String(30),
        nullable=False
    )

    explanation = db.Column(
        db.Text,
        nullable=False
    )

    policy_section = db.Column(
        db.String(100),
        nullable=True
    )

    suggestion = db.Column(
        db.Text,
        nullable=True
    )

    action = db.Column(
        db.String(30),
        default="Pending"
    )