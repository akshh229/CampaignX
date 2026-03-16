def compute_score(open_rate: float, click_rate: float) -> float:
    return (click_rate * 0.7) + (open_rate * 0.3)


def compute_metrics(campaigns: list) -> dict:
    """Compute weighted campaign metrics using real report data."""
    normalized_campaigns = []
    total_eo = 0
    total_ec = 0

    for index, campaign in enumerate(campaigns):
        open_rate = float(campaign.get("open_rate", 0) or 0)
        click_rate = float(campaign.get("click_rate", 0) or 0)
        eo_count = int(campaign.get("eo_count", 0) or 0)
        ec_count = int(campaign.get("ec_count", 0) or 0)
        score = compute_score(open_rate, click_rate)

        normalized_campaigns.append(
            {
                **campaign,
                "variant": campaign.get("variant") or chr(ord("A") + index),
                "open_rate": open_rate,
                "click_rate": click_rate,
                "eo_count": eo_count,
                "ec_count": ec_count,
                "score": score,
            }
        )
        total_eo += eo_count
        total_ec += ec_count

    avg_open = (
        sum(c["open_rate"] for c in normalized_campaigns) / len(normalized_campaigns)
        if normalized_campaigns
        else 0
    )
    avg_click = (
        sum(c["click_rate"] for c in normalized_campaigns) / len(normalized_campaigns)
        if normalized_campaigns
        else 0
    )
    winner = (
        max(normalized_campaigns, key=lambda campaign: campaign["score"])["variant"]
        if normalized_campaigns
        else None
    )

    return {
        "campaigns": normalized_campaigns,
        "score": compute_score(avg_open, avg_click),
        "avg_open_rate": avg_open,
        "avg_click_rate": avg_click,
        "total_eo": total_eo,
        "total_ec": total_ec,
        "winner": winner,
    }
