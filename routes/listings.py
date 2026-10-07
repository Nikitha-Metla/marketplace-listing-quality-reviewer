from flask import Blueprint, request, jsonify

from extensions import db
from models.listing import Listing
from models.review import Review
from models.finding import Finding

from services.validator import validate_listing
from services.duplicate_detector import find_duplicates
from services.ai_reviewer import review_with_ai


listings_bp = Blueprint(
    "listings",
    __name__,
    url_prefix="/api/listings"
)


def review_single_listing(data):
    """
    Review one listing.

    This function contains the complete review workflow
    so it can be reused by both single and batch review.
    """

    # ---------------------------------------------
    # 1. Deterministic validation
    # ---------------------------------------------

    validation_findings = validate_listing(data)

    # ---------------------------------------------
    # 2. Duplicate detection
    # ---------------------------------------------

    duplicates = find_duplicates(
        data.get("title", "")
    )

    if duplicates:
        validation_findings.append({
            "field": "title",
            "issue": "Duplicate listing",
            "severity": "High",
            "explanation": (
                "A listing with the same normalized "
                "title already exists."
            ),
            "policy_section": "POLICY-09",
            "suggestion": (
                "Check whether this listing is a duplicate "
                "and update the listing if necessary."
            )
        })

    # ---------------------------------------------
    # 3. AI / local fallback review
    # ---------------------------------------------

    ai_result = review_with_ai(data)

    ai_findings = ai_result.get(
        "findings",
        []
    )

    # ---------------------------------------------
    # 4. Combine findings
    # ---------------------------------------------

    all_findings = (
        validation_findings +
        ai_findings
    )

    # ---------------------------------------------
    # 5. Determine status
    # ---------------------------------------------

    if any(
        finding.get("severity")
        in ["High", "Critical"]
        for finding in all_findings
    ):
        status = "Reject"

    elif all_findings:
        status = "Needs Revision"

    elif not ai_result.get(
        "ai_available",
        False
    ):
        status = "AI Unavailable"

    else:
        status = "Pass"

    # ---------------------------------------------
    # 6. Create listing
    # ---------------------------------------------

    try:
        price_value = float(
            data.get("price", 0)
        )

    except (TypeError, ValueError):
        price_value = 0

    listing = Listing(
        title=data.get(
            "title",
            ""
        ),
        description=data.get(
            "description",
            ""
        ),
        category=data.get(
            "category",
            ""
        ),
        price=price_value,
        attributes=data.get(
            "attributes",
            ""
        ),
        seller=data.get(
            "seller",
            ""
        ),
        tags=data.get(
            "tags",
            ""
        )
    )

    db.session.add(listing)
    db.session.flush()

    # ---------------------------------------------
    # 7. Create review
    # ---------------------------------------------

    review = Review(
        listing_id=listing.id,
        overall_status=status,
        reviewer="System"
    )

    db.session.add(review)
    db.session.flush()

    # ---------------------------------------------
    # 8. Save findings
    # ---------------------------------------------

    saved_findings = []

    for item in all_findings:

        finding = Finding(
            review_id=review.id,
            field=item.get(
                "field",
                ""
            ),
            issue=item.get(
                "issue",
                ""
            ),
            severity=item.get(
                "severity",
                "Medium"
            ),
            explanation=item.get(
                "explanation",
                ""
            ),
            policy_section=item.get(
                "policy_section",
                ""
            ),
            suggestion=item.get(
                "suggestion",
                ""
            )
        )

        db.session.add(finding)
        db.session.flush()

        saved_findings.append({
            "id": finding.id,
            "field": finding.field,
            "issue": finding.issue,
            "severity": finding.severity,
            "explanation": finding.explanation,
            "policy_section": finding.policy_section,
            "suggestion": finding.suggestion
        })

    return {
        "listing_id": listing.id,
        "review_id": review.id,
        "status": status,
        "summary": ai_result.get(
            "summary",
            "Review completed."
        ),
        "findings": saved_findings
    }


@listings_bp.route(
    "/review",
    methods=["POST"]
)
def review_listing():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "No listing data provided."
        }), 400

    try:

        result = review_single_listing(
            data
        )

        db.session.commit()

        return jsonify({
            "success": True,
            **result
        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@listings_bp.route(
    "/review-batch",
    methods=["POST"]
)
def review_batch():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "No batch data provided."
        }), 400

    listings = data.get(
        "listings"
    )

    if not isinstance(
        listings,
        list
    ):

        return jsonify({
            "success": False,
            "error": (
                "'listings' must be "
                "a list."
            )
        }), 400

    if len(listings) == 0:

        return jsonify({
            "success": False,
            "error": (
                "At least one listing "
                "is required."
            )
        }), 400

    # Keep batch processing small.
    if len(listings) > 10:

        return jsonify({
            "success": False,
            "error": (
                "Batch size cannot exceed "
                "10 listings."
            )
        }), 400

    results = []

    try:

        for index, listing_data in enumerate(
            listings,
            start=1
        ):

            if not isinstance(
                listing_data,
                dict
            ):

                results.append({
                    "batch_index": index,
                    "success": False,
                    "error": (
                        "Listing must be "
                        "a JSON object."
                    )
                })

                continue

            try:

                result = review_single_listing(
                    listing_data
                )

                results.append({
                    "batch_index": index,
                    "success": True,
                    **result
                })

            except Exception as error:

                results.append({
                    "batch_index": index,
                    "success": False,
                    "error": str(error)
                })

        db.session.commit()

        successful = sum(
            1
            for result in results
            if result.get("success")
        )

        failed = len(results) - successful

        return jsonify({
            "success": True,
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500