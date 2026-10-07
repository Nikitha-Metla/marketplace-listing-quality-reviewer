# Agent Usage

## Overview

This project was developed with assistance from AI coding tools to accelerate implementation, debugging, documentation, and review.

The final application was manually tested by the candidate, and important implementation decisions were reviewed before submission.

## AI Tools Used

### ChatGPT

Used for:

- Understanding the assessment requirements.
- Breaking the project into smaller implementation tasks.
- Designing the Flask application structure.
- Generating and improving Python, Flask, HTML, CSS, and JavaScript code.
- Debugging backend and frontend issues.
- Designing the validation and policy-review workflow.
- Designing the human review workflow with approve, edit, and reject actions.
- Creating batch-review functionality.
- Reviewing API responses and error handling.
- Preparing deployment configuration for Render.
- Creating documentation and submission materials.

### Other Coding Assistance

AI-assisted coding was used where appropriate for implementation and debugging. Generated code was reviewed, integrated, executed, and tested in the local development environment before being included in the final project.

## Representative Prompts

Examples of prompts used during development included:

1. "Build a Flask marketplace listing reviewer with deterministic validation and AI-assisted policy review."

2. "Create a beginner-friendly Flask project structure with models, routes, services, templates, static files, and SQLite persistence."

3. "Implement validation for required fields, price format, supported categories, title length, and description length."

4. "Add duplicate listing detection using normalized titles."

5. "Create an AI review workflow that identifies unclear, misleading, prohibited, incomplete, and unverifiable content and cites the relevant policy section."

6. "Add human review actions so a reviewer can approve, edit, or reject an AI finding."

7. "Create an audit history that records the original value, revised value, action, reviewer, and timestamp."

8. "Add batch review support for multiple marketplace listings."

9. "Debug the Flask application and resolve circular-import and database issues."

10. "Prepare the Flask application for deployment on Render using Gunicorn."

## Delegated Work

AI assistance was used for implementation support in the following areas:

- Initial application architecture.
- Flask route and model scaffolding.
- Validation logic.
- Duplicate detection logic.
- Policy retrieval structure.
- AI review prompt design.
- Local policy-based fallback review.
- Frontend form and result rendering.
- Reviewer action workflow.
- Audit history page.
- Batch review UI and API.
- CSS and UI improvements.
- README and deployment documentation.
- Debugging runtime and database issues.

The candidate remained responsible for integrating the generated code, understanding the workflow, testing the application, and making the final submission decision.

## Important Agent Mistakes and Rejected Suggestions

During development, AI-generated suggestions were reviewed rather than accepted blindly.

### 1. Circular import issue

An initial application structure caused circular imports between the Flask application and database models.

This was rejected and replaced with a dedicated `extensions.py` module containing the SQLAlchemy instance. Models and the application then import the database extension independently.

### 2. Database testing contamination

During development, test data accumulated in the local SQLite database and affected duplicate-listing tests.

The database was reset after stopping running Python processes, and the important workflows were tested again using clean data.

### 3. Duplicate-title testing

Early batch tests used identical listing titles, which correctly triggered the duplicate detection rule but made the batch result look unexpected.

The test data was changed to unique titles when testing successful batch processing.

### 4. AI API availability

The application initially supported an OpenAI API workflow. The API could not be relied upon because the available account did not have sufficient API quota.

Instead of making the application fail, the implementation was changed to use a local policy-based fallback reviewer when the OpenAI API is unavailable.

This keeps the core review workflow operational and ensures that the application does not depend entirely on an unavailable external API.

### 5. History recording

The audit history implementation was tested carefully to ensure that the value existing before an approve, edit, or reject action is recorded as the original value.

The final implementation records:

- Listing ID
- Field
- Original value
- Revised value
- Action
- Reviewer
- Timestamp

## Verification Performed

The candidate verified the final application through local and deployed testing.

### Local verification

The following workflows were tested:

- Flask application startup.
- Listing creation.
- Required-field validation.
- Price validation.
- Supported-category validation.
- Title and description length validation.
- Duplicate listing detection.
- Policy-based content findings.
- Severity classification.
- Suggested revisions.
- Approve action.
- Edit action.
- Reject action.
- Audit history.
- Batch review.
- Empty/error states.
- Database persistence.

### Deployed verification

The application was deployed to Render using Gunicorn.

The deployed application was opened and tested through the public URL.

The following were verified on the deployed application:

- Frontend loads successfully.
- Review form is accessible.
- Batch review interface is accessible.
- History page is accessible.
- Backend API responds correctly.
- Review results are displayed.
- Human review actions can be performed.
- Audit history is displayed after review actions.

## Final Responsibility

AI tools were used as development assistants, not as a replacement for verification.

The candidate reviewed the generated implementation, ran the application, tested important behaviours, fixed integration issues, and verified the deployed workflow before submission.

The final submitted repository and deployment represent the implementation being submitted for review.