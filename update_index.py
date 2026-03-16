import re

with open('e:/CampaignX/frontend/src/pages/Index.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

new_impl = '''const Index = () => {
  const [section, setSection] = useState("home");
  const [phase, setPhase] = useState<CampaignPhase>("idle");
  const [isLoading, setIsLoading] = useState(false);
  
  // Real backend states
  const [threadId, setThreadId] = useState<string | null>(null);
  const [campaignState, setCampaignState] = useState<any>(null);

  const handleBriefSubmit = useCallback(async (brief: string) => {
    setSection("dashboard");
    setIsLoading(true);
    setPhase("parsing");
    
    let i = 0;
    const sequence: CampaignPhase[] = ["parsing", "segmenting", "planning", "generating"];
    const interval = setInterval(() => {
      if (i < sequence.length - 1) {
        i++;
        setPhase(sequence[i]);
      }
    }, 2500);

    try {
      const res = await fetch("http://localhost:8000/api/campaign/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brief })
      });
      const data = await res.json();
      
      clearInterval(interval);
      setThreadId(data.thread_id);
      setCampaignState(data.state);
      setPhase("approval");
    } catch (e) {
      console.error("API error", e);
      clearInterval(interval);
    }
    setIsLoading(false);
  }, []);

  const handleApprove = useCallback(async () => {
    if (!threadId) return;
    setIsLoading(true);
    setPhase("scheduling");
    try {
      const res = await fetch("http://localhost:8000/api/campaign/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread_id: threadId, decision: "approved" })
      });
      const data = await res.json();
      setCampaignState(data.state);
      setPhase("completed");
    } catch (e) {
      console.error("API error", e);
    }
    setIsLoading(false);
  }, [threadId]);

  const handleReject = useCallback(async (feedbackOrNone?: any) => {
    if (!threadId) return;
    setPhase("generating");
    setIsLoading(true);
    const feedback = typeof feedbackOrNone === "string" ? feedbackOrNone : "Needs revision";
    try {
      const res = await fetch("http://localhost:8000/api/campaign/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread_id: threadId, decision: "rejected", feedback })
      });
      const data = await res.json();
      setCampaignState(data.state);
      setPhase("approval");
    } catch (e) {
      console.error("API error", e);
    }
    setIsLoading(false);
  }, [threadId]);

  const handleReset = useCallback(() => {
    setPhase("idle");
    setThreadId(null);
    setCampaignState(null);
    setIsLoading(false);
  }, []);

  const getTimelineSteps = () => {
    const allSteps = [
      { id: 1, name: "Brief Parser" },
      { id: 2, name: "Segmentation Agent" },
      { id: 3, name: "Strategy Planner" },
      { id: 4, name: "Content Generator" },
      { id: 5, name: "HITL Approval" },
      { id: 6, name: "Scheduler" },
      { id: 7, name: "Monitor & Optimize" },
    ];
    const completed = getCompletedSteps(phase);
    const active = getActiveStep(phase);

    return allSteps.map((s) => ({
      ...s,
      status: completed.includes(s.id)
        ? ("completed" as const)
        : s.id === active
          ? ("active" as const)
          : ("pending" as const),
      timestamp: completed.includes(s.id) ? "Completed" : s.id === active ? "In progress..." : undefined,
    }));
  };

  const showParsed = PHASE_STEPS[phase].includes(1) && phase !== "parsing";
  const showSegment = PHASE_STEPS[phase].includes(2) && phase !== "segmenting";
  const showStrategy = PHASE_STEPS[phase].includes(3) && phase !== "planning";
  const showApproval = phase === "approval";
  const showMetrics = phase === "monitoring" || phase === "completed";

  const parsedBriefProp = campaignState?.parsed_brief ? {
    product: campaignState.parsed_brief.product_name || "Unknown Product",
    usp: campaignState.parsed_brief.usp || "No USP",
    offer: campaignState.parsed_brief.special_offers || "No Offers",
    cta: campaignState.parsed_brief.cta_url || "Link",
    tone: "Professional/Friendly",
  } : mockParsedBrief;

  const strategyProp = campaignState?.strategy_text ? {
    sendTime: "Determined dynamically",
    targeting: "A/B Segment derived",
    testStrategy: campaignState.strategy_text
  } : mockStrategy;

  const segmentProp = campaignState?.segments ? {
    totalAudience: (campaignState.segments.segment_a?.length || 0) + (campaignState.segments.segment_b?.length || 0) || 200,
    groupA: { name: "Variant A cohort", count: campaignState.segments.segment_a?.length || 100 },
    groupB: { name: "Variant B cohort", count: campaignState.segments.segment_b?.length || 100 },
    excludedInactive: true
  } : mockSegment;

  const variantAProp = campaignState?.content_a ? {
    id: "a",
    label: "Variant A",
    tone: "Professional",
    subject: campaignState.content_a.subject || "",
    preheader: "Dynamically generated variant A",
    body: campaignState.content_a.body || ""
  } : mockVariantA;

  const variantBProp = campaignState?.content_b ? {
    id: "b",
    label: "Variant B",
    tone: "Friendly",
    subject: campaignState.content_b.subject || "",
    preheader: "Dynamically generated variant B",
    body: campaignState.content_b.body || ""
  } : mockVariantB;

  return ('''

text = re.sub(r'const Index = \(\) => \{.+?(?=  return \()', new_impl, text, flags=re.DOTALL)

text = text.replace('data={mockParsedBrief}', 'data={parsedBriefProp}')
text = text.replace('data={mockStrategy}', 'data={strategyProp}')
text = text.replace('data={mockSegment}', 'data={segmentProp}')
text = text.replace('variantA={mockVariantA}', 'variantA={variantAProp}')
text = text.replace('variantB={mockVariantB}', 'variantB={variantBProp}')

with open('e:/CampaignX/frontend/src/pages/Index.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
