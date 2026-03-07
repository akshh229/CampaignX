def compute_metrics(campaigns: list) -> dict:
    """Compute weighted score from campaign reports.
    Formula: (click_rate * 0.7) + (open_rate * 0.3)
    """
    metrics = {"campaigns": campaigns}
    if campaigns:
        avg_click = sum(c.get("click_rate", 0) for c in campaigns) / len(campaigns)
        avg_open = sum(c.get("open_rate", 0) for c in campaigns) / len(campaigns)
        metrics["score"] = (avg_click * 0.7) + (avg_open * 0.3)
    else:
        metrics["score"] = 0
    return metrics
