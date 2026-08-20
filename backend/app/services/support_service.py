import sqlite3

from app.services.database import get_connection
from app.services.priority_service import calculate_priority


def support_complaint(
    complaint_id: int,
    user_id: str,
):
    """
    Add one user's support to a complaint.

    A user can support the same complaint only once.
    The database UNIQUE constraint is the final protection
    against duplicate support.
    """

    if complaint_id <= 0:
        raise ValueError("Complaint ID must be a positive integer.")

    if not user_id or not user_id.strip():
        raise ValueError("User identity is required.")

    user_id = user_id.strip()

    connection = get_connection()

    try:
        # First check that the complaint exists.
        complaint = connection.execute(
            """
            SELECT id, support_count
            FROM complaints
            WHERE id = ?
            """,
            (complaint_id,),
        ).fetchone()

        if complaint is None:
            raise LookupError("Complaint not found.")

        # Check whether this user has already supported it.
        existing_support = connection.execute(
            """
            SELECT id
            FROM complaint_support
            WHERE complaint_id = ?
              AND user_id = ?
            """,
            (complaint_id, user_id),
        ).fetchone()

        if existing_support is not None:
            raise PermissionError(
                "You have already supported this complaint."
            )

        try:
            # Register support.
            connection.execute(
                """
                INSERT INTO complaint_support (
                    complaint_id,
                    user_id
                )
                VALUES (?, ?)
                """,
                (
                    complaint_id,
                    user_id,
                ),
            )

            # Get the authoritative count from the support table.
            support_row = connection.execute(
                """
                SELECT COUNT(*) AS support_count
                FROM complaint_support
                WHERE complaint_id = ?
                """,
                (complaint_id,),
            ).fetchone()

            support_count = support_row["support_count"]

            # Recalculate priority from the new support count.
            priority = calculate_priority(support_count)

            # Keep the cached count and priority synchronized.
            connection.execute(
                """
                UPDATE complaints
                SET
                    support_count = ?,
                    priority = ?,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (
                    support_count,
                    priority,
                    complaint_id,
                ),
            )

            connection.commit()

        except sqlite3.IntegrityError:
            # Database UNIQUE(complaint_id, user_id) is the final
            # protection against duplicate support.
            connection.rollback()

            raise PermissionError(
                "You have already supported this complaint."
            )

        return {
            "message": "Your support has been recorded.",
            "support_count": support_count,
            "priority": priority,
        }

    finally:
        connection.close()