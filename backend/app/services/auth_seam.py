from fastapi import Header


def get_current_user_id(
    x_user_id: str = Header(...),
) -> str:
    """
    Temporary development identity provider.

    Somesh's authentication implementation can replace the
    internal logic later without changing complaint services.
    """

    user_id = x_user_id.strip()

    if not user_id:
        raise ValueError("User identity is required.")

    return user_id