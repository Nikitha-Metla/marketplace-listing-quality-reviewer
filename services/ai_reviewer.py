import os
import json
import re

from openai import OpenAI
from services.policy_retriever import retrieve_relevant_policies


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

PROMPT_FILE = os.path.join(
    BASE_DIR,
    "prompts",
    "listing_review_prompt.txt"
)


def load_review_prompt():
    if not os.path.exists(PROMPT_FILE):
        return ""

    with open(PROMPT_FILE, "r", encoding="utf-8") as file:
        return file.read()


# --------------------------------------------------
# Local fallback reviewer
# --------------------------------------------------

def local_review(listing):

    findings = []

    title = str(
        listing.get("title", "")
    )

    description = str(
        listing.get("description", "")
    )

    combined_text = (
        title + " " + description
    )

    # ----------------------------------------------
    # Unsupported guarantee claims
    # ----------------------------------------------

    guarantee_patterns = [
        "100% guaranteed",
        "guaranteed results",
        "works for everyone",
        "guaranteed to make you rich",
        "guaranteed",
        "never fails",
        "works instantly"
    ]

    for phrase in guarantee_patterns:

        if phrase.lower() in combined_text.lower():

            findings.append({
                "field": "description",
                "issue": "Unsupported guarantee claim",
                "severity": "High",
                "explanation": (
                    f"The listing contains the claim "
                    f"'{phrase}', which is not supported "
                    "by evidence."
                ),
                "policy_section": "POLICY-03",
                "suggestion": (
                    "Remove the guarantee and describe "
                    "the product features using "
                    "verifiable information."
                )
            })

            break

    # ----------------------------------------------
    # Promotional claims
    # ----------------------------------------------

    promotional_phrases = [
        "best in the world",
        "#1 product",
        "number one product",
        "life changing",
        "change your life"
    ]

    for phrase in promotional_phrases:

        if phrase.lower() in combined_text.lower():

            findings.append({
                "field": "description",
                "issue": "Unsupported promotional claim",
                "severity": "Medium",
                "explanation": (
                    f"The listing contains the "
                    f"unsupported promotional claim "
                    f"'{phrase}'."
                ),
                "policy_section": "BRAND-03",
                "suggestion": (
                    "Replace the promotional claim "
                    "with specific, verifiable "
                    "product information."
                )
            })

            break

    # ----------------------------------------------
    # Excessive punctuation
    # ----------------------------------------------

    if "!!!" in combined_text or "???" in combined_text:

        findings.append({
            "field": "description",
            "issue": "Excessive punctuation",
            "severity": "Low",
            "explanation": (
                "The listing uses repeated punctuation "
                "that may reduce professional readability."
            ),
            "policy_section": "BRAND-02",
            "suggestion": (
                "Use normal punctuation and remove "
                "repeated exclamation or question marks."
            )
        })

    # ----------------------------------------------
    # Excessive capitalization
    # ----------------------------------------------

    letters = [
        character
        for character in combined_text
        if character.isalpha()
    ]

    if letters:

        uppercase_count = sum(
            1
            for character in letters
            if character.isupper()
        )

        uppercase_ratio = (
            uppercase_count /
            len(letters)
        )

        if uppercase_ratio > 0.70 and len(letters) > 10:

            findings.append({
                "field": "title",
                "issue": "Excessive capitalization",
                "severity": "Medium",
                "explanation": (
                    "The listing uses excessive "
                    "capitalization."
                ),
                "policy_section": "BRAND-02",
                "suggestion": (
                    "Use normal capitalization to "
                    "improve readability."
                )
            })

    # ----------------------------------------------
    # Empty description
    # ----------------------------------------------

    if not description.strip():

        findings.append({
            "field": "description",
            "issue": "Incomplete description",
            "severity": "High",
            "explanation": (
                "The listing does not provide "
                "a product or service description."
            ),
            "policy_section": "POLICY-01",
            "suggestion": (
                "Add a clear description including "
                "important product or service details."
            )
        })

    # ----------------------------------------------
    # Determine status
    # ----------------------------------------------

    if any(
        item["severity"] in ["High", "Critical"]
        for item in findings
    ):
        status = "Reject"

    elif findings:
        status = "Needs Revision"

    else:
        status = "Pass"

    return {
        "ai_available": True,
        "ai_mode": "local_fallback",
        "overall_status": status,
        "summary": (
            "Local policy-based AI fallback review "
            "completed."
        ),
        "findings": findings
    }


# --------------------------------------------------
# OpenAI reviewer
# --------------------------------------------------

def openai_review(listing):

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key or api_key == "your-openai-api-key":
        return None

    try:

        client = OpenAI(
            api_key=api_key
        )

        policy = retrieve_relevant_policies(
            listing
        )

        base_prompt = load_review_prompt()

        prompt = f"""
{base_prompt}

IMPORTANT:

Review the listing using ONLY the supplied
marketplace policy and brand-content guide.

Return valid JSON only.

Required JSON structure:

{{
  "overall_status": "Pass | Needs Revision | Reject",
  "summary": "Short summary",
  "findings": [
    {{
      "field": "field name",
      "issue": "issue",
      "severity": "Low | Medium | High | Critical",
      "explanation": "explanation",
      "policy_section": "POLICY-XX or BRAND-XX",
      "suggestion": "improved wording"
    }}
  ]
}}

LISTING:

{json.dumps(
    listing,
    indent=2,
    ensure_ascii=False
)}

POLICY AND BRAND GUIDE:

{policy}
"""

        response = client.responses.create(
            model=os.getenv(
                "OPENAI_MODEL",
                "gpt-5-mini"
            ),
            input=prompt
        )

        text = response.output_text.strip()

        result = json.loads(text)

        result["ai_available"] = True
        result["ai_mode"] = "openai"

        if "findings" not in result:
            result["findings"] = []

        if "summary" not in result:
            result["summary"] = (
                "AI review completed."
            )

        return result

    except Exception as error:

        print(
            f"OpenAI unavailable: {error}"
        )

        return None


# --------------------------------------------------
# Main reviewer
# --------------------------------------------------

def review_with_ai(listing):

    # Try OpenAI first
    result = openai_review(listing)

    if result is not None:
        return result

    # Fall back to local reviewer
    return local_review(listing)