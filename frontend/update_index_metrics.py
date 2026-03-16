import re

with open('e:/CampaignX/frontend/src/pages/Index.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Add states
state_addition = '''  const [threadId, setThreadId] = useState<string | null>(null);
  const [dbCampaignId, setDbCampaignId] = useState<number | null>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [optHistory, setOptHistory] = useState<any[]>([]);
  const [campaignList, setCampaignList] = useState<any[]>([]);'''

text = text.replace('  const [threadId, setThreadId] = useState<string | null>(null);', state_addition)

# Update polling to fetch the rest
poll_logic = '''        try {
          const res = await fetch(http://localhost:8000/api/campaign/status/);
          if (!res.ok) return;
          const data = await res.json();
          if (data && data.state) {
            setCampaignState(data.state);
            if (data.campaign_id) setDbCampaignId(data.campaign_id);
            const serverStatus = data.status || data.state.status;

            if (serverStatus?.startsWith('hitl_')) {
               setPhase('approval');
               setIsLoading(false);
            } else if (serverStatus === 'done') {
               setPhase('completed');
               setIsLoading(false);
            }

            // Fetch extra DB stuff
            if (data.campaign_id) {
              fetch(http://localhost:8000/api/campaign//events)
                .then(r => r.json())
                .then(evs => setAuditLogs(evs.map((e: any) => ({
                   id: e.id, action: e.action, agent: e.agent, timestamp: new Date(e.timestamp).toLocaleTimeString(), detail: e.details
                }))));

              fetch(http://localhost:8000/api/campaign//iterations)
                .then(r => r.json())
                .then(iters => setOptHistory(iters.map((iter: any) => ({
                   iteration: iter.iteration_number,
                   variantAScore: iter.metrics_snapshot?.variantA?.score || 0,
                   variantBScore: iter.metrics_snapshot?.variantB?.score || 0,
                   winner: iter.winner,
                   action: iter.action_taken || "Iteration run"
                }))));
            }
          }
        }'''

text = re.sub(r'        try \{\s+const res = await fetch\(http://localhost:8000/api/campaign/status/\$\{threadId\}\);\s+if \(!res\.ok\) return;\s+const data = await res\.json\(\);\s+if \(data && data\.state\) \{\s+setCampaignState\(data\.state\);\s+const serverStatus = data\.status \|\| data\.state\.status;\s+if \(serverStatus\?\.startsWith\(\'hitl_\'\)\) \{\s+setPhase\(\'approval\'\);\s+setIsLoading\(false\);\s+\} else if \(serverStatus === \'done\'\) \{\s+setPhase\(\'completed\'\);\s+setIsLoading\(false\);\s+\}\s+\}\s+\}', poll_logic, text)

# Update handleBriefSubmit campaignId clearing
text = text.replace('setThreadId(data.thread_id);', 'setThreadId(data.thread_id); setDbCampaignId(data.campaign_id || null);')

with open('e:/CampaignX/frontend/src/pages/Index.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
