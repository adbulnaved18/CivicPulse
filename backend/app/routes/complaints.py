from fastapi import APIRouter
import re

from backend.app.models.complaint import Complaint
from backend.app.services.database import get_db


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return set(text.split())


def text_similarity(text1, text2):
    words1 = normalize_text(text1)
    words2 = normalize_text(text2)

    if not words1 or not words2:
        return 0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union)


def calculate_priority(votes, status):
    if status == "Resolved":
        return 0

    if status == "In Progress":
        return votes + 5

    return votes


router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("/")
def create_complaint(complaint: Complaint):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO complaints (
            description,
            category,
            location,
            language,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            complaint.description,
            complaint.category,
            complaint.location,
            complaint.language,
            complaint.status,
        ),
    )

    db.commit()
    db.close()

    return {
        "message": "Complaint saved successfully",
        "complaint": complaint
    }


@router.get("/")
def get_complaints():
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT
            c.id,
            c.description,
            c.category,
            c.location,
            c.language,
            c.status,
            COUNT(v.id) AS votes
        FROM complaints c
        LEFT JOIN complaint_votes v
            ON c.id = v.complaint_id
        GROUP BY c.id
        """
    )

    rows = cursor.fetchall()

    complaints = []

    for row in rows:
        priority = calculate_priority(row[6], row[5])

        complaints.append({
            "id": row[0],
            "description": row[1],
            "category": row[2],
            "location": row[3],
            "language": row[4],
            "status": row[5],
            "votes": row[6],
            "priority": priority
        })

    # Highest-priority complaints appear first
    complaints.sort(
        key=lambda complaint: (
            -complaint["priority"],
            complaint["id"]
        )
    )

    db.close()

    return complaints


@router.patch("/{complaint_id}/status")
def update_complaint_status(complaint_id: int, status: str):
    allowed_statuses = {
        "Pending",
        "In Progress",
        "Resolved",
    }

    if status not in allowed_statuses:
        return {
            "message": "Invalid status",
            "allowed_statuses": list(allowed_statuses),
        }

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE complaints
        SET status = ?
        WHERE id = ?
        """,
        (status, complaint_id),
    )

    db.commit()

    if cursor.rowcount == 0:
        db.close()

        return {
            "message": "Complaint not found"
        }

    db.close()

    return {
        "message": "Complaint status updated successfully",
        "complaint_id": complaint_id,
        "status": status,
    }

@router.post("/{complaint_id}/vote")
def vote_complaint(complaint_id: int, voter_id: str):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO complaint_votes (complaint_id, voter_id)
            VALUES (?, ?)
            """,
            (complaint_id, voter_id),
        )

        db.commit()

    except Exception:
        db.close()
        return {
            "message": "You have already voted for this complaint"
        }

    db.close()

    return {
        "message": "Vote added successfully",
        "complaint_id": complaint_id,
        "voter_id": voter_id,
    }


@router.get("/check-duplicate")
def check_duplicate(
    category: str,
    location: str,
    description: str
):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT
            c.id,
            c.description,
            c.category,
            c.location,
            c.status,
            COUNT(v.id) AS votes
        FROM complaints c
        LEFT JOIN complaint_votes v
            ON c.id = v.complaint_id
        WHERE c.category = ?
        AND c.location = ?
        GROUP BY c.id
        """,
        (category, location),
    )

    rows = cursor.fetchall()
    db.close()

    matches = []

    for row in rows:
        similarity = text_similarity(description, row[1])

        if similarity >= 0.30:
            matches.append({
                "id": row[0],
                "description": row[1],
                "category": row[2],
                "location": row[3],
                "status": row[4],
                "votes": row[5],
                "similarity": round(similarity, 2)
            })

    matches.sort(
        key=lambda complaint: (
            1 if complaint["status"] == "Resolved" else 0,
            -complaint["votes"],
            complaint["id"]
        )
    )

    if not matches:
        return {
            "is_duplicate": False,
            "matches": []
        }

    return {
        "is_duplicate": True,
        "matches": [matches[0]]
    }