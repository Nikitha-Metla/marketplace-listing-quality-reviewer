SUPPORTED_CATEGORIES = {
    "Electronics",
    "Home",
    "Clothing",
    "Books",
    "Beauty",
    "Services",
    "Sports",
    "Accessories"
}


def validate_listing(data):

    findings = []

    # Required fields
    required_fields = [
        "title",
        "description",
        "category",
        "price",
        "seller"
    ]

    for field in required_fields:

        value = data.get(field)

        if value is None or str(value).strip() == "":
            findings.append({
                "field": field,
                "issue": "Missing required field",
                "severity": "High",
                "explanation": f"{field} is required.",
                "policy_section": "POLICY-01",
                "suggestion": f"Provide a valid {field}."
            })

    # Price validation
    price = data.get("price")

    try:

        price_value = float(price)

        if price_value <= 0:
            findings.append({
                "field": "price",
                "issue": "Invalid price",
                "severity": "High",
                "explanation": "Price must be greater than zero.",
                "policy_section": "POLICY-07",
                "suggestion": "Enter a positive price."
            })

    except (ValueError, TypeError):

        findings.append({
            "field": "price",
            "issue": "Invalid price format",
            "severity": "High",
            "explanation": "Price must be numeric.",
            "policy_section": "POLICY-07",
            "suggestion": "Enter a numeric price."
        })

    # Title length
    title = data.get("title") or ""
    title = str(title)

    if len(title) > 120:
        findings.append({
            "field": "title",
            "issue": "Title too long",
            "severity": "Medium",
            "explanation": "Title exceeds 120 characters.",
            "policy_section": "POLICY-05",
            "suggestion": "Shorten the title to 120 characters or fewer."
        })

    # Description length
    description = data.get("description") or ""
    description = str(description)

    if len(description) > 5000:
        findings.append({
            "field": "description",
            "issue": "Description too long",
            "severity": "Medium",
            "explanation": "Description exceeds 5000 characters.",
            "policy_section": "POLICY-06",
            "suggestion": (
                "Shorten the description to 5000 characters or fewer."
            )
        })

    # Category validation
    category = data.get("category")

    if category and category not in SUPPORTED_CATEGORIES:
        findings.append({
            "field": "category",
            "issue": "Unsupported category",
            "severity": "High",
            "explanation": (
                f"{category} is not a supported category."
            ),
            "policy_section": "POLICY-08",
            "suggestion": (
                "Select one of the supported categories."
            )
        })

    return findings