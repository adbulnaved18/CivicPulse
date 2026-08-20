# PLACEHOLDER PRIORITY RULES
# 0-4 supports   -> Low
# 5-14 supports  -> Medium
# 15+ supports   -> High


LOW_MAX_SUPPORTS = 4
MEDIUM_MAX_SUPPORTS = 14


def calculate_priority(support_count: int) -> str:
    if support_count < 0:
        raise ValueError("Support count cannot be negative.")

    if support_count <= LOW_MAX_SUPPORTS:
        return "Low"

    if support_count <= MEDIUM_MAX_SUPPORTS:
        return "Medium"

    return "High"