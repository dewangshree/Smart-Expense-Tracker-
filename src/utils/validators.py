from datetime import date


def parse_iso_date(value: str) -> date:
    """Parse an ISO 8601 date string, raising ValueError on bad input."""
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"'{value}' is not a valid ISO date (expected YYYY-MM-DD)")
