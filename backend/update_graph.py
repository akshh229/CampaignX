with open('e:/CampaignX/backend/graph.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith('    return {"content_b": new_content'):
        lines[i] = "            return {'content_b': new_content, 'iteration': iteration, 'status': 'optimizing'}\n"
    elif line.startswith('    return {"content_a": new_content'):
        lines[i] = "            return {'content_a': new_content, 'iteration': iteration, 'status': 'optimizing'}\n"

with open('e:/CampaignX/backend/graph.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
