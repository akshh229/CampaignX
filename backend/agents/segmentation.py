def segment_customers(customers: list, parsed_brief: dict) -> dict:
    """Create two A/B segments for testing."""
    mid = len(customers) // 2
    segment_a = [c["customer_id"] for c in customers[:mid]]
    segment_b = [c["customer_id"] for c in customers[mid:]]

    # Filter inactive if needed
    if not parsed_brief.get("include_inactive", True):
        segment_a = [
            c["customer_id"]
            for c in customers[:mid]
            if c.get("status") != "inactive"
        ]
        segment_b = [
            c["customer_id"]
            for c in customers[mid:]
            if c.get("status") != "inactive"
        ]

    return {
        "segment_a": segment_a,
        "segment_b": segment_b,
        "total": len(segment_a) + len(segment_b),
        "strategy": "A/B split for content optimization",
    }
