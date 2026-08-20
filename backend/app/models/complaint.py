from typing import Optional

from pydantic import BaseModel, Field


class ComplaintCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=5000)
    category: str
    location: Optional[str] = Field(
        default=None,
        max_length=300
    )


class DuplicateCheckRequest(BaseModel):
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=5000)
    category: str
    location: Optional[str] = Field(
        default=None,
        max_length=300
    )


class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    location: Optional[str]

    status: str
    priority: str

    created_by: str
    support_count: int

    created_at: str
    updated_at: str


class RelatedComplaint(BaseModel):
    id: int
    title: str
    description_snippet: str

    category: str
    location: Optional[str]

    status: str
    priority: str
    support_count: int

    relevance_score: float


class DuplicateCheckResponse(BaseModel):
    related_complaints: list[RelatedComplaint]


class SupportResponse(BaseModel):
    message: str
    support_count: int
    priority: str