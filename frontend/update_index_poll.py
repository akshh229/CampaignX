import re

with open('e:/CampaignX/frontend/src/pages/Index.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('http://localhost:8000/api/campaign/status/', 'http://localhost:8000/api/campaign/status/" + threadId + "')
text = text.replace('http://localhost:8000/api/campaign/status/)', 'http://localhost:8000/api/campaign/status/" + threadId)')
text = text.replace('http://localhost:8000/api/campaign/status/\)', 'http://localhost:8000/api/campaign/status/" + threadId')


with open('e:/CampaignX/frontend/src/pages/Index.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
