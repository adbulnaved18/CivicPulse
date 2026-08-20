from difflib import SequenceMatcher
from typing import Optional

from app.config.duplicate_detection import (
    CATEGORY_MATCH_BONUS,
    LOCATION_MATCH_BONUS,
    MAX_RELATED_RESULTS,
    SIMILARITY_THRESHOLD,
)
from app.services.database import get_connection


def normalize_text(text: Optional[str]) -> str:
    """
    Normalize text before comparing complaints.
    """
    if not text:
        return ""

    return " ".join(text.lower().strip().split())


def calculate_similarity(
    title: str,
    description: str,
    existing_title: str,
    existing_description: str,
) -> float:
    """
    Calculate similarity between two complaints.
    """

    new_text = normalize_text(
        f"{title} {description}"
    )

    existing_text = normalize_text(
        f"{existing_title} {existing_description}"
    )

    if not new_text or not existing_text:
        return 0.0

    return SequenceMatcher(
        None,
        new_text,
        existing_text,
    ).ratio()


def find_related_complaints(
    title: str,
    description: str,
    category: str,
    location: Optional[str] = None,
):
    """
    Find complaints that may be related to the new complaint.

    Similarity is the main signal.
    Category and location provide small relevance bonuses.

    A related complaint NEVER blocks creation.
    """

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                title,
                description,
                category,
                location,
                status,
                priority,
                support_count
            FROM complaints
            ORDER BY id DESC
            LIMIT 200
            """
        ).fetchall()

        results = []

        normalized_location = normalize_text(location)

        for row in rows:

            score = calculate_similarity(
                title,
                description,
                row["title"],
                row["description"],
            )

            # Category is a signal, not a requirement.
            if (
                normalize_text(category)
                == normalize_text(row["category"])
            ):
                score += CATEGORY_MATCH_BONUS

            # Location is also a signal, not a requirement.
            existing_location = normalize_text(
                row["location"]
            )

            if (
                normalized_location
                and existing_location
                and normalized_location == existing_location
            ):
                score += LOCATION_MATCH_BONUS

            score = min(score, 1.0)

            if score >= SIMILARITY_THRESHOLD:
                results.append(
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "description_snippet": (
                            row["description"][:200]
                        ),
                        "category": row["category"],
                        "location": row["location"],
                        "status": row["status"],
                        "priority": row["priority"],
                        "support_count": row["support_count"],
                        "relevance_score": round(score, 3),
                    }
                )

        results.sort(
            key=lambda item: (
                item["relevance_score"],
                item["support_count"],
            ),
            reverse=True,
        )

        return results[:MAX_RELATED_RESULTS]

    finally:
        connection.close()