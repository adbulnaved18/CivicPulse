from typing import Optional

from app.config.categories import ALLOWED_CATEGORIES
from app.models.constants import PRIORITIES, STATUSES


MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 5000
MAX_LOCATION_LENGTH = 300


def validate_title(title: str) -> str:
    if not isinstance(title, str):
        raise ValueError("Title must be a string.")

    title = title.strip()

    if not title:
        raise ValueError("Title cannot be empty.")

    if len(title) > MAX_TITLE_LENGTH:
        raise ValueError(
            f"Title cannot exceed {MAX_TITLE_LENGTH} characters."
        )

    return title


def validate_description(description: str) -> str:
    if not isinstance(description, str):
        raise ValueError("Description must be a string.")

    description = description.strip()

    if not description:
        raise ValueError("Description cannot be empty.")

    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise ValueError(
            f"Description cannot exceed "
            f"{MAX_DESCRIPTION_LENGTH} characters."
        )

    return description


def validate_category(category: str) -> str:
    if not isinstance(category, str):
        raise ValueError("Category must be a string.")

    category = category.strip()

    if not category:
        raise ValueError("Category is required.")

    if category not in ALLOWED_CATEGORIES:
        raise ValueError(
            f"Invalid category. Allowed categories: "
            f"{', '.join(ALLOWED_CATEGORIES)}"
        )

    return category


def validate_location(location: Optional[str]) -> Optional[str]:
    if location is None:
        return None

    location = location.strip()

    if not location:
        return None

    if len(location) > MAX_LOCATION_LENGTH:
        raise ValueError(
            f"Location cannot exceed {MAX_LOCATION_LENGTH} characters."
        )

    return location


def validate_status(status: Optional[str]) -> Optional[str]:
    if status is None:
        return None

    if status not in STATUSES:
        raise ValueError(
            f"Invalid status. Allowed values: {', '.join(STATUSES)}"
        )

    return status


def validate_priority(priority: Optional[str]) -> Optional[str]:
    if priority is None:
        return None

    if priority not in PRIORITIES:
        raise ValueError(
            f"Invalid priority. Allowed values: {', '.join(PRIORITIES)}"
        )

    return priority