def _customer_id(customer: dict) -> str:
    return (
        customer.get("customer_id")
        or customer.get("customerId")
        or customer.get("id")
        or ""
    )


def segment_customers(customers: list, parsed_brief: dict) -> dict:
    """Create two A/B segments for testing."""
    mid = len(customers) // 2
    segment_a = [_customer_id(customer) for customer in customers[:mid] if _customer_id(customer)]
    segment_b = [_customer_id(customer) for customer in customers[mid:] if _customer_id(customer)]

    # Filter inactive if needed
    if not parsed_brief.get("include_inactive", True):
        segment_a = [
            _customer_id(customer)
            for customer in customers[:mid]
            if customer.get("status") != "inactive" and _customer_id(customer)
        ]
        segment_b = [
            _customer_id(customer)
            for customer in customers[mid:]
            if customer.get("status") != "inactive" and _customer_id(customer)
        ]

    return {
        "segment_a": segment_a,
        "segment_b": segment_b,
        "total": len(segment_a) + len(segment_b),
        "strategy": "A/B split for content optimization",
    }
