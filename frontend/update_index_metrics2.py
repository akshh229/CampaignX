import re

with open('e:/CampaignX/frontend/src/pages/Index.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

old_logic = '''        try {
          const res = await fetch(http://localhost:8000/api/campaign/status/);
          if (!res.ok) return;
          const data = await res.json();
          if (data && data.state) {
            setCampaignState(data.state);
            const serverStatus = data.status || data.state.status;

            if (serverStatus?.startsWith('hitl_')) {
               setPhase('approval');
               setIsLoading(false);
            } else if (serverStatus === 'done') {
               setPhase('completed');
               setIsLoading(false);
            }
          }
        }'''

new_logic = '''        try {
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
                .then(r => r.ok ? r.json() : [])
                .then(evs => {
                   if (Array.isArray(evs)) {
                       setAuditLogs(evs.map((e: any) => ({
                          id: e.id, action: e.action, agent: e.agent, timestamp: new Date(e.timestamp).toLocaleTimeString(), detail: e.details
                       })));
                   }
                });

              fetch(http://localhost:8000/api/campaign//iterations)
                .then(r => r.ok ? r.json() : [])
                .then(iters => {
                   if (Array.isArray(iters)) {
                       setOptHistory(iters.map((iter: any) => ({
                          iteration: iter.iteration_number,
                          variantAScore: iter.metrics_snapshot?.variantA?.score || 0,
                          variantBScore: iter.metrics_snapshot?.variantB?.score || 0,
                          winner: iter.winner,
                          action: iter.action_taken || "Iteration run"
                       })));
                   }
                });
            }
          }
        }'''

# Replace exactly
text = text.replace(old_logic, new_logic)

with open('e:/CampaignX/frontend/src/pages/Index.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
