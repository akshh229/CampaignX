from datetime import datetime, timedelta


def get_optimal_schedule() -> str:
    """Return an optimal schedule time (1 hour from now) in ISO format."""
    return (datetime.utcnow() + timedelta(hours=1)).isoformat()
