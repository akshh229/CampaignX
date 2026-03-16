import re

with open('e:/CampaignX/frontend/src/pages/Index.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('variantA={mockMetricsA}', 'variantA={metricsAProp}')
text = text.replace('variantB={mockMetricsB}', 'variantB={metricsBProp}')
text = text.replace('iteration={3}', 'iteration={campaignState?.iteration || 1}')
text = text.replace('iterations={mockOptHistory}', 'iterations={optHistory.length > 0 ? optHistory : mockOptHistory}')
text = text.replace('entries={mockAuditLog}', 'entries={auditLogs.length > 0 ? auditLogs : mockAuditLog}')
text = text.replace('campaigns={mockCampaigns}', 'campaigns={campaignList.length > 0 ? campaignList : mockCampaigns}')

with open('e:/CampaignX/frontend/src/pages/Index.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
