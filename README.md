# Marketplace Listing Quality Reviewer

A Flask-based application that reviews marketplace product and service listings against predefined marketplace policies and brand-content guidelines.

The application combines deterministic validation, duplicate detection, policy-based AI review, reviewer actions, batch processing, and audit history.

---

## 1. Project Overview

The Marketplace Listing Quality Reviewer helps marketplace reviewers identify issues in product and service listings before approval.

A listing can be checked for:

- Missing required information
- Invalid price
- Unsupported categories
- Excessively long titles
- Excessively long descriptions
- Duplicate listings
- Misleading claims
- Unsupported guarantees
- Unsupported promotional claims
- Excessive capitalization
- Excessive punctuation
- Incomplete descriptions
- Other policy-related issues defined in the supplied policy documents

Each finding includes:

- Affected field
- Issue
- Severity
- Explanation
- Policy section
- Suggested improvement

---

## 2. Key Features

### Single Listing Review

Review one marketplace listing at a time.

Supported fields:

- Title
- Description
- Category
- Price
- Attributes
- Seller
- Tags

---

### Deterministic Validation

The application performs rule-based checks for:

- Required fields
- Numeric and positive price
- Title length
- Description length
- Supported categories
- Duplicate normalized titles

These checks provide predictable validation without relying on AI.

---

### Policy-Based AI Review

The application supports AI-assisted listing review using the supplied marketplace policy and brand-content guide.

The AI review workflow is designed to identify:

- Unclear content
- Misleading claims
- Prohibited or suspicious content
- Incomplete information
- Assumptions
- Unverifiable claims
- Promotional claims

Every finding can reference a policy or brand-content section.

---

### Local Fallback Review

The application also includes a local policy-based fallback reviewer.

This allows the application to continue working when an external AI API is unavailable.

The local reviewer detects common issues such as:

- Guarantee claims
- Unsupported promotional claims
- Excessive punctuation
- Excessive capitalization
- Missing descriptions

This makes the application usable without depending entirely on an external API.

---

### Severity Classification

Findings can be classified as:

- Low
- Medium
- High
- Critical

Overall review status is calculated from the findings.

Possible statuses include:

- Pass
- Needs Revision
- Reject
- AI Unavailable

---

## 3. Reviewer Workflow

The reviewer can take action on individual findings.

### Approve

Approves the suggested revision and applies the suggestion to the listing.

### Edit

Allows the reviewer to provide their own revised value.

### Reject

Rejects the suggested change without modifying the listing.

Every reviewer action is stored in the audit history.

---

## 4. Audit History

The application maintains a review history containing:

- Listing ID
- Field
- Original value
- Revised value
- Action
- Reviewer
- Timestamp

This provides traceability for reviewer decisions.

Supported actions:

- Approve
- Edit
- Reject

---

## 5. Batch Review

The application supports reviewing multiple listings in one request.

Batch processing supports:

- Up to 10 listings
- Individual validation
- Individual policy review
- Individual status
- Individual findings
- Success/failure tracking

The batch API returns a summary containing:

- Total listings
- Successful reviews
- Failed reviews
- Results for each listing

---

## 6. Project Architecture

```text
marketplace_listing_reviewer/
│
├── database/
│   └── marketplace.db
│
├── models/
│   ├── __init__.py
│   ├── listing.py
│   ├── review.py
│   ├── finding.py
│   └── history.py
│
├── policies/
│   ├── marketplace_policy.md
│   └── brand_content_guide.md
│
├── prompts/
│   └── listing_review_prompt.txt
│
├── routes/
│   ├── listings.py
│   └── reviews.py
│
├── services/
│   ├── ai_reviewer.py
│   ├── duplicate_detector.py
│   ├── policy_retriever.py
│   └── validator.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── templates/
│   ├── base.html
│   ├── index.html
│   └── history.html
│
├── .env
├── .gitignore
├── app.py
├── extensions.py
├── requirements.txt
└── README.md