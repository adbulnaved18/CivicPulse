from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.complaint import (
    ComplaintCreate,
    DuplicateCheckRequest,
)
from app.services.auth_seam import get_current_user_id
from app.services.complaint_service import (
    create_complaint,
    get_complaint,
    search_complaints,
)
from app.services.duplicate_service import find_related_complaints
from app.services.support_service import support_complaint


router = APIRouter(
    prefix="/complaints",
    tags=["Complaints"],
)


@router.post("/check-duplicates")
def check_duplicates(
    complaint: DuplicateCheckRequest,
):
    """
    Check whether the submitted complaint appears related
    to existing complaints.

    This endpoint ONLY checks for related complaints.
    It does not create or block anything.
    """

    try:
        related = find_related_complaints(
            title=complaint.title,
            description=complaint.description,
            category=complaint.category,
            location=complaint.location,
        )

        return {
            "related_complaints": related,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.post(
    "",
    status_code=201,
)
def create_new_complaint(
    complaint: ComplaintCreate,
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a new complaint.

    Duplicate detection does NOT block creation.
    """

    try:
        return create_complaint(
            title=complaint.title,
            description=complaint.description,
            category=complaint.category,
            location=complaint.location,
            created_by=user_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get("")
def get_complaints(
    search: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    location: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    sort: str = Query(default="newest"),
):
    """
    Search, filter and sort complaints.

    All parameters are optional and can be combined.
    """

    try:
        return search_complaints(
            search=search,
            category=category,
            location=location,
            status=status,
            priority=priority,
            sort=sort,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get("/{complaint_id}")
def get_single_complaint(
    complaint_id: int,
):
    """
    Get one complaint by ID.
    """

    try:
        complaint = get_complaint(complaint_id)

        if complaint is None:
            raise HTTPException(
                status_code=404,
                detail="Complaint not found.",
            )

        return complaint

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.post("/{complaint_id}/support")
def support_existing_complaint(
    complaint_id: int,
    user_id: str = Depends(get_current_user_id),
):
    """
    Register the authenticated user's support
    for an existing complaint.
    """

    try:
        return support_complaint(
            complaint_id=complaint_id,
            user_id=user_id,
        )

    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except PermissionError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )