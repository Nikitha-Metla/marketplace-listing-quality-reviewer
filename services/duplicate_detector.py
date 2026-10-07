from models.listing import Listing


def normalize_title(title):

    if not title:
        return ""

    return " ".join(
        str(title).lower().strip().split()
    )


def find_duplicates(title):

    normalized = normalize_title(title)

    if not normalized:
        return []

    listings = Listing.query.all()

    duplicates = []

    for listing in listings:

        existing = normalize_title(listing.title)

        if existing == normalized:
            duplicates.append(listing.id)

    return duplicates