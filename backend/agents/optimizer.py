from agents.content_gen import generate_content


def optimize_campaign(state: dict) -> dict:
    """Determine winner variant and regenerate the loser. Max 3 iterations."""
    iteration = state.get("iteration", 0) + 1
    if iteration >= 3:
        return {"iteration": iteration, "status": "done"}

    campaigns = state.get("metrics", {}).get("campaigns", [])
    if len(campaigns) >= 2:
        if campaigns[0].get("click_rate", 0) > campaigns[1].get("click_rate", 0):
            # A wins, regenerate B
            new_content = generate_content(state["parsed_brief"], "B")
            return {"content_b": new_content, "iteration": iteration, "status": "optimizing"}
        else:
            # B wins, regenerate A
            new_content = generate_content(state["parsed_brief"], "A")
            return {"content_a": new_content, "iteration": iteration, "status": "optimizing"}

    return {"iteration": iteration, "status": "done"}
