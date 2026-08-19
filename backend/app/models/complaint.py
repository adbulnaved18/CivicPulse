from pydantic import BaseModel


class Complaint(BaseModel):
    description: str
    category: str
    location: str
    language: str = "en"
    status: str = "Pending"