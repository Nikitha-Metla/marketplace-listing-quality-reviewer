from flask import Blueprint, jsonify, request, render_template

from extensions import db
from models.finding import Finding
from models.history import ReviewHistory


reviews_bp = Blueprint(
    "reviews",
    __name__,
    url_prefix="/api/reviews"
)


# =========================================================
# LISTING FIELD HELPERS
# =========================================================

def get_listing_value(listing, field):

    if field == "title":
        return listing.title

    if field == "description":
        return listing.description

    if field == "category":
        return listing.category

    if field == "price":
        return str(listing.price)

    if field == "attributes":
        return listing.attributes or ""

    if field == "seller":
        return listing.seller

    if field == "tags":
        return listing.tags or ""

    return ""


def update_listing_field(listing, field, value):

    if field == "title":
        listing.title = value

    elif field == "description":
        listing.description = value

    elif field == "category":
        listing.category = value

    elif field == "price":
        try:
            listing.price = float(value)
        except (TypeError, ValueError):
            return False

    elif field == "attributes":
        listing.attributes = value

    elif field == "seller":
        listing.seller = value

    elif field == "tags":
        listing.tags = value

    else:
        return False

    return True


# =========================================================
# FINDING ACTION
# =========================================================

@reviews_bp.route(
    "/<int:finding_id>/action",
    methods=["POST"]
)
def finding_action(finding_id):

    data = request.get_json() or {}

    action = data.get("action")

    if action not in {
        "approve",
        "reject",
        "edit"
    }:
        return jsonify({
            "success": False,
            "error": (
                "Invalid action. "
                "Use approve, reject, or edit."
            )
        }), 400


    finding = Finding.query.get_or_404(
        finding_id
    )

    listing = finding.review.listing

    field = finding.field

    # -----------------------------------------------------
    # IMPORTANT:
    # Always capture the actual value BEFORE changing it.
    # This value is stored as the original value for this
    # specific review action.
    # -----------------------------------------------------

    original_value = get_listing_value(
        listing,
        field
    )


    # -----------------------------------------------------
    # REJECT
    # -----------------------------------------------------

    if action == "reject":

        finding.action = "reject"

        revised_value = original_value

        should_update_listing = False


    # -----------------------------------------------------
    # APPROVE
    # -----------------------------------------------------

    elif action == "approve":

        finding.action = "approve"

        revised_value = (
            finding.suggestion
            or original_value
        )

        # Duplicate findings should not automatically
        # change the listing.
        if finding.issue == "Duplicate listing":

            revised_value = original_value

            should_update_listing = False

        else:

            should_update_listing = True


    # -----------------------------------------------------
    # EDIT
    # -----------------------------------------------------

    else:

        revised_value = data.get(
            "revised_value"
        )

        if revised_value is None:

            return jsonify({
                "success": False,
                "error": (
                    "revised_value is required "
                    "when using edit."
                )
            }), 400


        revised_value = str(
            revised_value
        ).strip()


        if not revised_value:

            return jsonify({
                "success": False,
                "error": (
                    "revised_value cannot be empty."
                )
            }), 400


        finding.action = "edit"

        should_update_listing = True


    # -----------------------------------------------------
    # UPDATE LISTING
    # -----------------------------------------------------

    if should_update_listing:

        success = update_listing_field(
            listing,
            field,
            revised_value
        )

        if not success:

            return jsonify({
                "success": False,
                "error": (
                    f"Invalid value for "
                    f"the {field} field."
                )
            }), 400


    # =====================================================
    # SAVE AUDIT HISTORY
    # =====================================================

    history_record = ReviewHistory(

        listing_id=listing.id,

        field=field,

        original_value=original_value,

        revised_value=revised_value,

        action=action,

        reviewer=data.get(
            "reviewer",
            "Reviewer"
        )
    )

    db.session.add(
        history_record
    )

    db.session.commit()


    # =====================================================
    # RESPONSE
    # =====================================================

    return jsonify({

        "success": True,

        "finding_id":
            finding_id,

        "action":
            action,

        "field":
            field,

        "original_value":
            original_value,

        "revised_value":
            revised_value,

        "current_value":
            get_listing_value(
                listing,
                field
            ),

        "message":
            f"Finding {action}d successfully."

    }), 200


# =========================================================
# HISTORY PAGE
# =========================================================

@reviews_bp.route(
    "/history",
    methods=["GET"]
)
def history():

    return render_template(
        "history.html"
    )


# =========================================================
# HISTORY DATA API
# =========================================================

@reviews_bp.route(
    "/history-data",
    methods=["GET"]
)
def history_data():

    records = (
        ReviewHistory.query
        .order_by(
            ReviewHistory.timestamp.desc(),
            ReviewHistory.id.desc()
        )
        .all()
    )


    return jsonify([

        {
            "id":
                record.id,

            "listing_id":
                record.listing_id,

            "field":
                record.field,

            "original_value":
                record.original_value,

            "revised_value":
                record.revised_value,

            "action":
                record.action,

            "reviewer":
                record.reviewer,

            "timestamp":
                (
                    record.timestamp.isoformat()
                    if record.timestamp
                    else None
                )
        }

        for record in records

    ]), 200