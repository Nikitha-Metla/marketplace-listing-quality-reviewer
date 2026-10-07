document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // SINGLE LISTING REVIEW
    // =========================================================

    const reviewForm = document.getElementById("reviewForm");
    const loading = document.getElementById("loading");
    const result = document.getElementById("result");

    if (reviewForm) {
        reviewForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const title = document.getElementById("title").value.trim();
            const description = document.getElementById("description").value.trim();
            const category = document.getElementById("category").value.trim();
            const price = document.getElementById("price").value.trim();
            const attributes = document.getElementById("attributes").value.trim();
            const seller = document.getElementById("seller").value.trim();
            const tags = document.getElementById("tags").value.trim();

            if (
                title === "" ||
                description === "" ||
                category === "" ||
                price === "" ||
                seller === ""
            ) {
                alert(
                    "Please fill Title, Description, Category, Price and Seller."
                );
                return;
            }

            const listing = {
                title: title,
                description: description,
                category: category,
                price: Number(price),
                attributes: attributes,
                seller: seller,
                tags: tags
            };

            loading.classList.remove("hidden");
            result.innerHTML = "";

            try {
                const response = await fetch("/api/listings/review", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(listing)
                });

                const data = await response.json();

                loading.classList.add("hidden");

                if (!response.ok || !data.success) {
                    result.innerHTML = `
                        <div class="result-card error-card">
                            <h2>Review Failed</h2>
                            <p>${escapeHtml(
                                data.error || "Something went wrong."
                            )}</p>
                        </div>
                    `;
                    return;
                }

                displaySingleResult(data);

            } catch (error) {
                loading.classList.add("hidden");

                result.innerHTML = `
                    <div class="result-card error-card">
                        <h2>Connection Error</h2>
                        <p>Could not connect to the review server.</p>
                        <p>${escapeHtml(error.message)}</p>
                    </div>
                `;
            }
        });
    }


    // =========================================================
    // DISPLAY SINGLE REVIEW RESULT
    // =========================================================

    function displaySingleResult(data) {
        let findingsHtml = "";

        if (data.findings && data.findings.length > 0) {

            findingsHtml = `
                <h3>Findings</h3>
            `;

            data.findings.forEach(function (finding) {

                const severityClass =
                    String(finding.severity || "")
                        .toLowerCase()
                        .replace(/\s+/g, "-");

                findingsHtml += `
                    <div class="finding ${severityClass}">
                        <h3>
                            ${escapeHtml(finding.issue)}
                        </h3>

                        <p>
                            <strong>Field:</strong>
                            ${escapeHtml(finding.field)}
                        </p>

                        <p class="severity">
                            <strong>Severity:</strong>
                            ${escapeHtml(finding.severity)}
                        </p>

                        <p>
                            <strong>Explanation:</strong>
                            ${escapeHtml(finding.explanation)}
                        </p>

                        <p class="policy">
                            Policy:
                            ${escapeHtml(
                                finding.policy_section || "Not specified"
                            )}
                        </p>

                        ${
                            finding.suggestion
                                ? `
                                <div class="suggestion-box">
                                    <strong>Suggested Revision:</strong>
                                    <p>
                                        ${escapeHtml(finding.suggestion)}
                                    </p>
                                </div>
                                `
                                : ""
                        }

                        <div class="action-buttons">
                            <button
                                type="button"
                                onclick="approveFinding(${finding.id})"
                            >
                                ✅ Approve
                            </button>

                            <button
                                type="button"
                                onclick="editFinding(${finding.id})"
                            >
                                ✏️ Edit
                            </button>

                            <button
                                type="button"
                                onclick="rejectFinding(${finding.id})"
                            >
                                ❌ Reject
                            </button>
                        </div>

                        <div
                            id="action-result-${finding.id}"
                            class="action-result"
                        ></div>
                    </div>
                `;
            });

        } else {

            findingsHtml = `
                <div class="success-message">
                    <strong>✅ No issues found.</strong>
                    <p>
                        This listing complies with the current
                        marketplace validation rules.
                    </p>
                </div>
            `;
        }

        result.innerHTML = `
            <div class="result-card">
                <h2>Review Result</h2>

                <p>
                    <strong>Status:</strong>
                    <span class="status">
                        ${escapeHtml(data.status)}
                    </span>
                </p>

                <p>
                    <strong>Listing ID:</strong>
                    ${escapeHtml(data.listing_id)}
                </p>

                <p>
                    <strong>Review ID:</strong>
                    ${escapeHtml(data.review_id)}
                </p>

                <p>
                    <strong>Summary:</strong>
                    ${escapeHtml(data.summary || "Review completed.")}
                </p>

                ${
                    data.findings && data.findings.length > 0
                        ? findingsHtml
                        : findingsHtml
                }
            </div>
        `;
    }


    // =========================================================
    // APPROVE FINDING
    // =========================================================

    window.approveFinding = async function (findingId) {

        const confirmed = confirm(
            "Approve this suggestion and apply the recommended revision?"
        );

        if (!confirmed) {
            return;
        }

        await performFindingAction(
            findingId,
            "approve"
        );
    };


    // =========================================================
    // REJECT FINDING
    // =========================================================

    window.rejectFinding = async function (findingId) {

        const confirmed = confirm(
            "Reject this suggestion?"
        );

        if (!confirmed) {
            return;
        }

        await performFindingAction(
            findingId,
            "reject"
        );
    };


    // =========================================================
    // EDIT FINDING
    // =========================================================

    window.editFinding = async function (findingId) {

        const revisedValue = prompt(
            "Enter the revised value:"
        );

        if (revisedValue === null) {
            return;
        }

        if (revisedValue.trim() === "") {
            alert("Revised value cannot be empty.");
            return;
        }

        await performFindingAction(
            findingId,
            "edit",
            revisedValue
        );
    };


    // =========================================================
    // FINDING ACTION API
    // =========================================================

    async function performFindingAction(
        findingId,
        action,
        revisedValue = null
    ) {

        const actionResult = document.getElementById(
            `action-result-${findingId}`
        );

        if (actionResult) {
            actionResult.innerHTML = "Processing...";
        }

        const requestBody = {
            action: action,
            reviewer: "Reviewer"
        };

        if (action === "edit") {
            requestBody.revised_value = revisedValue;
        }

        try {

            const response = await fetch(
                `/api/reviews/${findingId}/action`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(requestBody)
                }
            );

            const data = await response.json();

            if (!response.ok || !data.success) {

                if (actionResult) {
                    actionResult.innerHTML = `
                        <div class="error-card">
                            <p>
                                ${escapeHtml(
                                    data.error ||
                                    "Action failed."
                                )}
                            </p>
                        </div>
                    `;
                }

                return;
            }

            if (actionResult) {
                actionResult.innerHTML = `
                    <div class="action-success">
                        <strong>✅ Action completed</strong>
                        <p>
                            Action:
                            ${escapeHtml(data.action)}
                        </p>
                        <p>
                            Field:
                            ${escapeHtml(data.field)}
                        </p>
                        <p>
                            Revised value:
                            ${escapeHtml(
                                data.revised_value || ""
                            )}
                        </p>
                    </div>
                `;
            }

        } catch (error) {

            if (actionResult) {
                actionResult.innerHTML = `
                    <div class="error-card">
                        <p>
                            ${escapeHtml(error.message)}
                        </p>
                    </div>
                `;
            }
        }
    }


    // =========================================================
    // BATCH REVIEW
    // =========================================================

    const batchListings =
        document.getElementById("batchListings");

    const addBatchListing =
        document.getElementById("addBatchListing");

    const reviewBatch =
        document.getElementById("reviewBatch");

    const batchLoading =
        document.getElementById("batchLoading");

    const batchResult =
        document.getElementById("batchResult");


    // =========================================================
    // ADD NEW BATCH LISTING
    // =========================================================

    if (addBatchListing) {

        addBatchListing.addEventListener(
            "click",
            function () {

                const currentListings =
                    document.querySelectorAll(
                        ".batch-listing"
                    );

                if (currentListings.length >= 10) {

                    alert(
                        "You can review a maximum of 10 listings."
                    );

                    return;
                }

                const newNumber =
                    currentListings.length + 1;

                const listingDiv =
                    document.createElement("div");

                listingDiv.className =
                    "batch-listing";

                listingDiv.innerHTML = `
                    <div class="batch-heading">

                        <h3>
                            Listing ${newNumber}
                        </h3>

                        <button
                            type="button"
                            class="remove-batch-listing"
                        >
                            🗑️ Remove
                        </button>

                    </div>

                    <label>Title</label>

                    <input
                        type="text"
                        class="batch-title"
                        placeholder="Listing title"
                    >

                    <label>Description</label>

                    <textarea
                        class="batch-description"
                        rows="4"
                        placeholder="Listing description"
                    ></textarea>

                    <label>Category</label>

                    <select class="batch-category">

                        <option value="">
                            Select category
                        </option>

                        <option value="Electronics">
                            Electronics
                        </option>

                        <option value="Home">
                            Home
                        </option>

                        <option value="Clothing">
                            Clothing
                        </option>

                        <option value="Books">
                            Books
                        </option>

                        <option value="Beauty">
                            Beauty
                        </option>

                        <option value="Services">
                            Services
                        </option>

                        <option value="Sports">
                            Sports
                        </option>

                        <option value="Accessories">
                            Accessories
                        </option>

                    </select>

                    <label>Price</label>

                    <input
                        type="number"
                        class="batch-price"
                        min="0"
                        step="0.01"
                        placeholder="Price"
                    >

                    <label>Attributes</label>

                    <input
                        type="text"
                        class="batch-attributes"
                        placeholder="Example: Bluetooth, 8GB RAM"
                    >

                    <label>Seller</label>

                    <input
                        type="text"
                        class="batch-seller"
                        placeholder="Seller name"
                    >

                    <label>Tags</label>

                    <input
                        type="text"
                        class="batch-tags"
                        placeholder="Example: laptop, electronics"
                    >
                `;

                batchListings.appendChild(
                    listingDiv
                );

                updateBatchNumbers();
            }
        );
    }


    // =========================================================
    // REMOVE BATCH LISTING
    // =========================================================

    if (batchListings) {

        batchListings.addEventListener(
            "click",
            function (event) {

                if (
                    event.target.classList.contains(
                        "remove-batch-listing"
                    )
                ) {

                    const cards =
                        document.querySelectorAll(
                            ".batch-listing"
                        );

                    if (cards.length <= 1) {

                        alert(
                            "At least one listing is required."
                        );

                        return;
                    }

                    const card =
                        event.target.closest(
                            ".batch-listing"
                        );

                    if (card) {
                        card.remove();
                    }

                    updateBatchNumbers();
                }
            }
        );
    }


    // =========================================================
    // UPDATE BATCH LISTING NUMBERS
    // =========================================================

    function updateBatchNumbers() {

        const cards =
            document.querySelectorAll(
                ".batch-listing"
            );

        cards.forEach(
            function (card, index) {

                const heading =
                    card.querySelector(
                        ".batch-heading h3"
                    );

                if (heading) {
                    heading.textContent =
                        `Listing ${index + 1}`;
                }
            }
        );
    }


    // =========================================================
    // REVIEW BATCH
    // =========================================================

    if (reviewBatch) {

        reviewBatch.addEventListener(
            "click",
            async function () {

                const batchCards =
                    document.querySelectorAll(
                        ".batch-listing"
                    );

                if (batchCards.length === 0) {

                    alert(
                        "Please add at least one listing."
                    );

                    return;
                }

                const listings = [];
                let hasError = false;

                batchCards.forEach(
                    function (card, index) {

                        const titleElement =
                            card.querySelector(
                                ".batch-title"
                            );

                        const descriptionElement =
                            card.querySelector(
                                ".batch-description"
                            );

                        const categoryElement =
                            card.querySelector(
                                ".batch-category"
                            );

                        const priceElement =
                            card.querySelector(
                                ".batch-price"
                            );

                        const attributesElement =
                            card.querySelector(
                                ".batch-attributes"
                            );

                        const sellerElement =
                            card.querySelector(
                                ".batch-seller"
                            );

                        const tagsElement =
                            card.querySelector(
                                ".batch-tags"
                            );


                        // Safely read every field

                        const title =
                            titleElement
                                ? titleElement.value.trim()
                                : "";

                        const description =
                            descriptionElement
                                ? descriptionElement.value.trim()
                                : "";

                        const category =
                            categoryElement
                                ? categoryElement.value.trim()
                                : "";

                        const price =
                            priceElement
                                ? priceElement.value.trim()
                                : "";

                        const attributes =
                            attributesElement
                                ? attributesElement.value.trim()
                                : "";

                        const seller =
                            sellerElement
                                ? sellerElement.value.trim()
                                : "";

                        const tags =
                            tagsElement
                                ? tagsElement.value.trim()
                                : "";


                        // Required-field validation

                        if (
                            title === "" ||
                            description === "" ||
                            category === "" ||
                            price === "" ||
                            seller === ""
                        ) {

                            alert(
                                "Please fill Title, Description, Category, Price and Seller for Listing " +
                                (index + 1) +
                                "."
                            );

                            hasError = true;

                            return;
                        }


                        // Price validation

                        const numericPrice =
                            Number(price);

                        if (
                            Number.isNaN(numericPrice) ||
                            numericPrice <= 0
                        ) {

                            alert(
                                "Please enter a valid positive price for Listing " +
                                (index + 1) +
                                "."
                            );

                            hasError = true;

                            return;
                        }


                        // Add listing to batch

                        listings.push({

                            title: title,

                            description: description,

                            category: category,

                            price: numericPrice,

                            attributes: attributes,

                            seller: seller,

                            tags: tags

                        });
                    }
                );


                if (hasError) {
                    return;
                }


                // Show loading

                if (batchLoading) {
                    batchLoading.classList.remove(
                        "hidden"
                    );
                }

                if (batchResult) {
                    batchResult.innerHTML = "";
                }


                try {

                    const response =
                        await fetch(
                            "/api/listings/review-batch",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    listings: listings
                                })
                            }
                        );


                    const data =
                        await response.json();


                    if (batchLoading) {
                        batchLoading.classList.add(
                            "hidden"
                        );
                    }


                    if (
                        !response.ok ||
                        !data.success
                    ) {

                        if (batchResult) {

                            batchResult.innerHTML = `
                                <div class="result-card error-card">

                                    <h2>
                                        Batch Review Failed
                                    </h2>

                                    <p>
                                        ${escapeHtml(
                                            data.error ||
                                            "Something went wrong."
                                        )}
                                    </p>

                                </div>
                            `;
                        }

                        return;
                    }


                    displayBatchResults(data);


                } catch (error) {

                    if (batchLoading) {
                        batchLoading.classList.add(
                            "hidden"
                        );
                    }

                    if (batchResult) {

                        batchResult.innerHTML = `
                            <div class="result-card error-card">

                                <h2>
                                    Connection Error
                                </h2>

                                <p>
                                    Could not connect to the review server.
                                </p>

                                <p>
                                    ${escapeHtml(
                                        error.message
                                    )}
                                </p>

                            </div>
                        `;
                    }
                }
            }
        );
    }


    // =========================================================
    // DISPLAY BATCH RESULTS
    // =========================================================

    function displayBatchResults(data) {

        if (!batchResult) {
            return;
        }

        let html = `

            <div class="result-card">

                <h2>
                    📦 Batch Review Result
                </h2>

                <div class="batch-summary">

                    <div>
                        <strong>Total</strong>
                        <span>
                            ${escapeHtml(data.total)}
                        </span>
                    </div>

                    <div>
                        <strong>Successful</strong>
                        <span>
                            ${escapeHtml(data.successful)}
                        </span>
                    </div>

                    <div>
                        <strong>Failed</strong>
                        <span>
                            ${escapeHtml(data.failed)}
                        </span>
                    </div>

                </div>

        `;


        if (
            data.results &&
            data.results.length > 0
        ) {

            data.results.forEach(
                function (item) {

                    if (!item.success) {

                        html += `

                            <div class="batch-result-item">

                                <h3>
                                    Listing ${escapeHtml(
                                        item.batch_index
                                    )}

                                    <span class="batch-status reject">
                                        Failed
                                    </span>
                                </h3>

                                <p>
                                    <strong>Error:</strong>
                                    ${escapeHtml(
                                        item.error ||
                                        "Unknown error"
                                    )}
                                </p>

                            </div>

                        `;

                        return;
                    }


                    const status =
                        String(
                            item.status || ""
                        );

                    const statusClass =
                        status
                            .toLowerCase()
                            .replace(/\s+/g, "-");


                    html += `

                        <div class="batch-result-item">

                            <h3>

                                Listing ${escapeHtml(
                                    item.batch_index
                                )}

                                <span
                                    class="batch-status ${escapeHtml(
                                        statusClass
                                    )}"
                                >
                                    ${escapeHtml(status)}
                                </span>

                            </h3>

                            <p>
                                <strong>Listing ID:</strong>
                                ${escapeHtml(
                                    item.listing_id
                                )}
                            </p>

                            <p>
                                <strong>Review ID:</strong>
                                ${escapeHtml(
                                    item.review_id
                                )}
                            </p>

                            <p>
                                <strong>Summary:</strong>
                                ${escapeHtml(
                                    item.summary ||
                                    "Review completed."
                                )}
                            </p>

                    `;


                    if (
                        item.findings &&
                        item.findings.length > 0
                    ) {

                        html += `
                            <div class="batch-findings">

                                <h4>
                                    Findings
                                </h4>
                        `;


                        item.findings.forEach(
                            function (finding) {

                                const severityClass =
                                    String(
                                        finding.severity ||
                                        ""
                                    )
                                        .toLowerCase()
                                        .replace(
                                            /\s+/g,
                                            "-"
                                        );


                                html += `

                                    <div
                                        class="finding ${escapeHtml(
                                            severityClass
                                        )}"
                                    >

                                        <h4>
                                            ${escapeHtml(
                                                finding.issue
                                            )}
                                        </h4>

                                        <p>
                                            <strong>
                                                Field:
                                            </strong>

                                            ${escapeHtml(
                                                finding.field
                                            )}
                                        </p>

                                        <p>
                                            <strong>
                                                Severity:
                                            </strong>

                                            ${escapeHtml(
                                                finding.severity
                                            )}
                                        </p>

                                        <p>
                                            <strong>
                                                Explanation:
                                            </strong>

                                            ${escapeHtml(
                                                finding.explanation
                                            )}
                                        </p>

                                        <p class="policy">
                                            Policy:
                                            ${escapeHtml(
                                                finding.policy_section ||
                                                "Not specified"
                                            )}
                                        </p>

                                        ${
                                            finding.suggestion
                                                ? `
                                                    <div class="suggestion-box">

                                                        <strong>
                                                            Suggested Revision:
                                                        </strong>

                                                        <p>
                                                            ${escapeHtml(
                                                                finding.suggestion
                                                            )}
                                                        </p>

                                                    </div>
                                                `
                                                : ""
                                        }

                                    </div>

                                `;
                            }
                        );


                        html += `
                            </div>
                        `;
                    } else {

                        html += `

                            <div class="success-message">

                                <strong>
                                    ✅ No issues found
                                </strong>

                                <p>
                                    This listing complies with
                                    the current marketplace rules.
                                </p>

                            </div>

                        `;
                    }


                    html += `
                        </div>
                    `;
                }
            );

        } else {

            html += `
                <div class="success-message">
                    No batch results available.
                </div>
            `;
        }


        html += `
            </div>
        `;


        batchResult.innerHTML = html;
    }


    // =========================================================
    // HTML ESCAPE FUNCTION
    // =========================================================

    function escapeHtml(value) {

        if (value === null || value === undefined) {
            return "";
        }

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

});