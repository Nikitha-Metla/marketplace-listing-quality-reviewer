import os


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)


POLICY_FILES = [
    os.path.join(
        BASE_DIR,
        "policies",
        "marketplace_policy.md"
    ),
    os.path.join(
        BASE_DIR,
        "policies",
        "brand_content_guide.md"
    )
]


def load_policies():

    content = ""

    for file_path in POLICY_FILES:

        if os.path.exists(file_path):

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                content += "\n\n" + file.read()

    return content.strip()


def retrieve_relevant_policies(listing):

    policies = load_policies()

    text = (
        str(listing.get("title", "")) + " " +
        str(listing.get("description", "")) + " " +
        str(listing.get("category", ""))
    ).lower()

    relevant = []

    keywords = {
        "guarantee": [
            "POLICY-03",
            "BRAND-03"
        ],
        "guaranteed": [
            "POLICY-03",
            "BRAND-03"
        ],
        "price": [
            "POLICY-07"
        ],
        "category": [
            "POLICY-08"
        ],
        "title": [
            "POLICY-05"
        ]
    }

    for keyword, sections in keywords.items():

        if keyword in text:

            relevant.extend(sections)

    # Remove duplicate section IDs
    relevant = list(set(relevant))

    # Currently provide the complete policy context
    # so the AI has access to all marketplace rules.
    return policies