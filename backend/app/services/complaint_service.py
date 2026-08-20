from typing import Optional

from app.models.constants import PRIORITIES, STATUSES, SORT_OPTIONS
from app.services.database import get_connection
from app.services.priority_service import calculate_priority
from app.services.validation import (
    validate_category,
    validate_description,
    validate_location,
    validate_priority,
    validate_status,
    validate_title,
)


def create_complaint(
    title: str,
    description: str,
    category: str,
    location: Optional[str],
    created_by: str,
):
    """
    Validate and create a new complaint.

    Duplicate detection is intentionally NOT performed here.
    A related complaint may be shown to the citizen before creation,
    but a citizen is always allowed to create a new complaint.
    """

    title = validate_title(title)
    description = validate_description(description)
    category = validate_category(category)
    location = validate_location(location)

    if not created_by or not created_by.strip():
        raise ValueError("User identity is required.")

    created_by = created_by.strip()

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO complaints (
                title,
                description,
                category,
                location,
                status,
                priority,
                created_by,
                support_count
            )
            VALUES (?, ?, ?, ?, 'Pending', 'Low', ?, 0)
            """,
            (
                title,
                description,
                category,
                location,
                created_by,
            ),
        )

        complaint_id = cursor.lastrowid

        connection.commit()

        row = connection.execute(
            """
            SELECT *
            FROM complaints
            WHERE id = ?
            """,
            (complaint_id,),
        ).fetchone()

        return dict(row)

    finally:
        connection.close()


def get_complaint(complaint_id: int):
    """
    Fetch a single complaint by ID.
    """

    if complaint_id <= 0:
        raise ValueError("Complaint ID must be a positive integer.")

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM complaints
            WHERE id = ?
            """,
            (complaint_id,),
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()


def search_complaints(
    search: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    sort: str = "newest",
):
    """
    Search, filter and sort complaints.

    All filters are optional and can be combined.
    """

    if category is not None:
        category = validate_category(category)

    if location is not None:
        location = validate_location(location)

    if status is not None:
        status = validate_status(status)

    if priority is not None:
        priority = validate_priority(priority)

    if sort not in SORT_OPTIONS:
        raise ValueError(
            f"Invalid sort option. Allowed values: "
            f"{', '.join(SORT_OPTIONS)}"
        )

    if search is not None:
        search = search.strip()

        if not search:
            search = None

    connection = get_connection()

    try:
        query = """
            SELECT *
            FROM complaints
            WHERE 1 = 1
        """

        parameters = []

        # Search title, description, category and location.
        if search is not None:
            query += """
                AND (
                    LOWER(title) LIKE LOWER(?)
                    OR LOWER(description) LIKE LOWER(?)
                    OR LOWER(category) LIKE LOWER(?)
                    OR LOWER(COALESCE(location, '')) LIKE LOWER(?)
                )
            """

            search_value = f"%{search}%"

            parameters.extend(
                [
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                ]
            )

        if category is not None:
            query += " AND category = ?"
            parameters.append(category)

        if location is not None:
            query += " AND LOWER(location) LIKE LOWER(?)"
            parameters.append(f"%{location}%")

        if status is not None:
            query += " AND status = ?"
            parameters.append(status)

        if priority is not None:
            query += " AND priority = ?"
            parameters.append(priority)

        # Sorting.
        if sort == "newest":
            query += " ORDER BY created_at DESC, id DESC"

        elif sort == "oldest":
            query += " ORDER BY created_at ASC, id ASC"

        elif sort == "priority":
            query += """
                ORDER BY
                    CASE priority
                        WHEN 'High' THEN 3
                        WHEN 'Medium' THEN 2
                        WHEN 'Low' THEN 1
                    END DESC,
                    id DESC
            """

        elif sort == "most_supported":
            query += """
                ORDER BY support_count DESC, id DESC
            """

        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

        results = [dict(row) for row in rows]

        return {
            "results": results,
            "count": len(results),
        }

    finally:
        connection.close()