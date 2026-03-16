import { useCallback, useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { RotateCcw } from "lucide-react";

import ApprovalWorkspace from "@/components/campaign/ApprovalWorkspace";
import AgentWorkflow from "@/components/campaign/AgentWorkflow";
import AuditLog from "@/components/campaign/AuditLog";
import BriefInput from "@/components/campaign/BriefInput";
import CampaignHistory from "@/components/campaign/CampaignHistory";
import ExecutionTimeline from "@/components/campaign/ExecutionTimeline";
import FeatureHighlights from "@/components/campaign/FeatureHighlights";
import Footer from "@/components/campaign/Footer";
import HeroSection from "@/components/campaign/HeroSection";
import MetricsDashboard from "@/components/campaign/MetricsDashboard";
import Navbar from "@/components/campaign/Navbar";
import OptimizationHistory from "@/components/campaign/OptimizationHistory";
import ParsedBrief from "@/components/campaign/ParsedBrief";
import SegmentSummary from "@/components/campaign/SegmentSummary";
import StrategySummary from "@/components/campaign/StrategySummary";
import WhySection from "@/components/campaign/WhySection";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";

const API_BASE = (import.meta.env.VITE_API_BASE || "/api").replace(/\/$/, "");

type Section = "home" | "dashboard" | "history";
type HealthStatus = "healthy" | "degraded" | "down";
type CampaignPhase =
  | "idle"
  | "parsing"
  | "segmenting"
  | "planning"
  | "generating"
  | "approval"
  | "scheduling"
  | "monitoring"
  | "completed";
type TimelineStatus = "completed" | "active" | "pending" | "error";
type HistoryStatus = "completed" | "running" | "paused" | "failed";
type DashboardStatus = "running" | "optimizing" | "completed" | "paused";

interface BackendVariant {
  subject?: string;
  body?: string;
}

interface BackendMetricsReport {
  variant?: string;
  campaign_id?: string;
  open_rate?: number;
  click_rate?: number;
  score?: number;
  eo_count?: number;
  ec_count?: number;
}

interface BackendCampaignState {
  brief?: string;
  parsed_brief?: {
    product_name?: string;
    usp?: string;
    special_offers?: string;
    cta_url?: string;
    tone?: string;
    include_inactive?: boolean;
  };
  segments?: {
    total?: number;
    strategy?: string;
    segment_a?: string[];
    segment_b?: string[];
  };
  strategy_text?: string;
  content_a?: BackendVariant;
  content_b?: BackendVariant;
  metrics?: {
    campaigns?: BackendMetricsReport[];
    score?: number;
    winner?: string;
    total_eo?: number;
    total_ec?: number;
  };
  scheduled_time?: string;
  iteration?: number;
  status?: string;
}

interface CampaignStatusResponse {
  thread_id: string;
  campaign_id: number;
  state: BackendCampaignState;
  status: string;
}

interface HistoryCampaign {
  id: string;
  name: string;
  product: string;
  status: HistoryStatus;
  iterations: number;
  winningVariant?: string;
  topScore?: number;
  date: string;
}

interface AuditEntry {
  id: string;
  action: string;
  agent: string;
  timestamp: string;
  detail?: string;
}

interface IterationEntry {
  iteration: number;
  variantAScore: number;
  variantBScore: number;
  winner: "A" | "B";
  action: string;
}

const PHASE_STEPS: Record<CampaignPhase, number[]> = {
  idle: [],
  parsing: [1],
  segmenting: [1, 2],
  planning: [1, 2, 3],
  generating: [1, 2, 3, 4],
  approval: [1, 2, 3, 4, 5],
  scheduling: [1, 2, 3, 4, 5, 6],
  monitoring: [1, 2, 3, 4, 5, 6, 7],
  completed: [1, 2, 3, 4, 5, 6, 7],
};

const STATUS_TO_PHASE: Record<string, CampaignPhase> = {
  processing: "parsing",
  started: "parsing",
  brief_parsed: "segmenting",
  customers_fetched: "segmenting",
  segmented: "planning",
  strategy_planned: "generating",
  content_ready: "approval",
  awaiting_approval: "approval",
  hitl_rejected: "approval",
  hitl_approved: "scheduling",
  scheduled: "scheduling",
  monitored: "monitoring",
  optimizing: "monitoring",
  done: "completed",
};

const SAMPLE_BRIEF = `Run email campaign for launching XDeposit, a flagship term deposit product from SuperBFSI, that gives 1 percentage point higher returns than its competitors. Announce an additional 0.25 percentage point higher returns for female senior citizens. Optimise for open rate and click rate. Do not skip emails to customers marked inactive. Include the call to action: https://superbfsi.com/xdeposit/explore/`;

function getActiveStep(phase: CampaignPhase): number | undefined {
  const map: Record<CampaignPhase, number | undefined> = {
    idle: undefined,
    parsing: 1,
    segmenting: 2,
    planning: 3,
    generating: 4,
    approval: 5,
    scheduling: 6,
    monitoring: 7,
    completed: undefined,
  };
  return map[phase];
}

function getCompletedSteps(phase: CampaignPhase): number[] {
  const active = getActiveStep(phase);
  if (!active) {
    return phase === "completed" ? [1, 2, 3, 4, 5, 6, 7] : [];
  }
  return Array.from({ length: active - 1 }, (_, index) => index + 1);
}

function mapStatusToPhase(status: string | undefined, state: BackendCampaignState | null): CampaignPhase {
  if (status && STATUS_TO_PHASE[status]) {
    return STATUS_TO_PHASE[status];
  }
  if (state?.metrics?.campaigns?.length) {
    return "monitoring";
  }
  if (state?.content_a && state?.content_b) {
    return "approval";
  }
  if (state?.strategy_text) {
    return "generating";
  }
  if (state?.segments) {
    return "planning";
  }
  if (state?.parsed_brief) {
    return "segmenting";
  }
  return "parsing";
}

function mapCampaignHealth(statusValue: string | undefined): HealthStatus {
  if (statusValue === "ok") {
    return "healthy";
  }
  if (statusValue) {
    return "degraded";
  }
  return "down";
}

function mapHistoryStatus(status: string | undefined): HistoryStatus {
  if (!status) {
    return "paused";
  }
  if (status === "done" || status === "completed") {
    return "completed";
  }
  if (status === "awaiting_approval" || status.startsWith("hitl_")) {
    return "paused";
  }
  if (status === "failed") {
    return "failed";
  }
  return "running";
}

function mapMetricsStatus(status: string | undefined): DashboardStatus {
  if (status === "done" || status === "completed") {
    return "completed";
  }
  if (status === "optimizing") {
    return "optimizing";
  }
  if (status === "awaiting_approval" || status?.startsWith("hitl_")) {
    return "paused";
  }
  return "running";
}

function formatTimestamp(timestamp: string | undefined): string {
  if (!timestamp) {
    return "";
  }
  const date = new Date(timestamp);
  return Number.isNaN(date.getTime()) ? timestamp : date.toLocaleTimeString();
}

function formatDate(value: string | undefined): string {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString();
}

function toPercent(rate: number | undefined): number {
  return (Number(rate) || 0) * 100;
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch {
      // Ignore JSON parse issues and use the default message.
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

const Index = () => {
  const { toast } = useToast();
  const [section, setSection] = useState<Section>("home");
  const [phase, setPhase] = useState<CampaignPhase>("idle");
  const [isLoading, setIsLoading] = useState(false);
  const [healthStatus, setHealthStatus] = useState<HealthStatus>("down");
  const [threadId, setThreadId] = useState<string | null>(null);
  const [campaignId, setCampaignId] = useState<number | null>(null);
  const [campaignStatus, setCampaignStatus] = useState<string>("idle");
  const [campaignState, setCampaignState] = useState<BackendCampaignState | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditEntry[]>([]);
  const [iterationHistory, setIterationHistory] = useState<IterationEntry[]>([]);
  const [campaignHistory, setCampaignHistory] = useState<HistoryCampaign[]>([]);

  const loadHealth = useCallback(async () => {
    try {
      const payload = await fetchJson<{ status?: string }>(`${API_BASE}/health`);
      setHealthStatus(mapCampaignHealth(payload.status));
    } catch {
      setHealthStatus("down");
    }
  }, []);

  const loadCampaignHistory = useCallback(async () => {
    try {
      const campaigns = await fetchJson<any[]>(`${API_BASE}/campaigns`);
      const mappedCampaigns = campaigns.map((campaign) => ({
        id: String(campaign.id),
        name: campaign.content_subject || campaign.product_name || `Campaign ${campaign.id}`,
        product: campaign.product_name || campaign.brief?.slice(0, 32) || "CampaignX",
        status: mapHistoryStatus(campaign.status),
        iterations: campaign.iteration_count || 0,
        winningVariant: campaign.winning_variant || undefined,
        topScore: campaign.top_score ?? undefined,
        date: formatDate(campaign.created_at),
      }));
      setCampaignHistory(mappedCampaigns);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const loadCampaignArtifacts = useCallback(async (id: number) => {
    try {
      const [events, approvals, iterations] = await Promise.all([
        fetchJson<any[]>(`${API_BASE}/campaign/${id}/events`),
        fetchJson<any[]>(`${API_BASE}/campaign/${id}/approvals`),
        fetchJson<any[]>(`${API_BASE}/campaign/${id}/iterations`),
      ]);

      const mappedEvents = events.map((event) => ({
        id: `event-${event.id}`,
        action: event.action || "Event",
        agent: event.agent_name || "Agent",
        timestamp: formatTimestamp(event.timestamp),
        detail: event.details || undefined,
        sortTime: event.timestamp || "",
      }));
      const mappedApprovals = approvals.map((approval) => ({
        id: `approval-${approval.id}`,
        action: `Decision: ${approval.decision}`,
        agent: "Human Reviewer",
        timestamp: formatTimestamp(approval.timestamp),
        detail: approval.reviewer_notes || "No reviewer notes provided.",
        sortTime: approval.timestamp || "",
      }));

      const mergedAudit = [...mappedEvents, ...mappedApprovals]
        .sort((left, right) => left.sortTime.localeCompare(right.sortTime))
        .map(({ sortTime, ...entry }) => entry);
      setAuditLogs(mergedAudit);

      const mappedIterations = iterations.map((iteration) => {
        const variantAScore = Number(iteration.variant_a?.score || 0);
        const variantBScore = Number(iteration.variant_b?.score || 0);
        const winner = iteration.winner || (variantAScore >= variantBScore ? "A" : "B");
        return {
          iteration: Number(iteration.iteration_number || 0),
          variantAScore,
          variantBScore,
          winner,
          action: iteration.action_taken || "Iteration completed.",
        } as IterationEntry;
      });
      setIterationHistory(mappedIterations);
    } catch (error) {
      console.error(error);
    }
  }, []);

  useEffect(() => {
    void loadHealth();
    const intervalId = window.setInterval(() => {
      void loadHealth();
    }, 15000);
    return () => window.clearInterval(intervalId);
  }, [loadHealth]);

  useEffect(() => {
    void loadCampaignHistory();
  }, [loadCampaignHistory]);

  useEffect(() => {
    if (!threadId) {
      return;
    }

    let cancelled = false;
    const pollStatus = async () => {
      try {
        const payload = await fetchJson<CampaignStatusResponse>(`${API_BASE}/campaign/status/${threadId}`);
        if (cancelled) {
          return;
        }

        setCampaignId(payload.campaign_id);
        setCampaignState(payload.state);
        setCampaignStatus(payload.status);
        setPhase(mapStatusToPhase(payload.status, payload.state));

        if (payload.campaign_id) {
          void loadCampaignArtifacts(payload.campaign_id);
        }

        if (payload.status === "awaiting_approval" || payload.status === "done" || payload.status === "failed") {
          setIsLoading(false);
        }

        if (payload.status === "done" || payload.status === "failed") {
          void loadCampaignHistory();
        }
      } catch (error) {
        if (!cancelled) {
          console.error(error);
        }
      }
    };

    void pollStatus();
    const intervalId = window.setInterval(() => {
      void pollStatus();
    }, 2500);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, [threadId, loadCampaignArtifacts, loadCampaignHistory]);

  const handleBriefSubmit = useCallback(
    async (brief: string) => {
      setSection("dashboard");
      setIsLoading(true);
      setPhase("parsing");
      setCampaignStatus("processing");
      setThreadId(null);
      setCampaignId(null);
      setCampaignState(null);
      setAuditLogs([]);
      setIterationHistory([]);

      try {
        const payload = await fetchJson<CampaignStatusResponse>(`${API_BASE}/campaign/start`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ brief }),
        });
        setThreadId(payload.thread_id);
        setCampaignId(payload.campaign_id);
        setCampaignState(payload.state);
        setCampaignStatus(payload.status);
        setPhase(mapStatusToPhase(payload.status, payload.state));
        void loadCampaignHistory();
      } catch (error) {
        const message = error instanceof Error ? error.message : "Unable to start campaign.";
        toast({
          variant: "destructive",
          title: "Campaign start failed",
          description: message,
        });
        setIsLoading(false);
        setPhase("idle");
      }
    },
    [loadCampaignHistory, toast],
  );

  const handleApprove = useCallback(
    async (notes?: string) => {
      if (!threadId) {
        return;
      }

      setIsLoading(true);
      setPhase("scheduling");
      try {
        await fetchJson<{ status: string }>(`${API_BASE}/campaign/approve`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            thread_id: threadId,
            decision: "approved",
            feedback: notes || "Campaign approved for scheduling.",
          }),
        });
        setCampaignStatus("processing");
      } catch (error) {
        const message = error instanceof Error ? error.message : "Unable to approve campaign.";
        toast({
          variant: "destructive",
          title: "Approval failed",
          description: message,
        });
        setIsLoading(false);
        setPhase("approval");
      }
    },
    [threadId, toast]
  );

  const handleReject = useCallback(
    async (feedback: string) => {
      if (!threadId) {
        return;
      }

      setIsLoading(true);
      setPhase("generating");
      try {
        await fetchJson<{ status: string }>(`${API_BASE}/campaign/approve`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            thread_id: threadId,
            decision: "rejected",
            feedback: feedback || "Please refine the underperforming content.",
          }),
        });
        setCampaignStatus("processing");
      } catch (error) {
        const message = error instanceof Error ? error.message : "Unable to reject campaign.";
        toast({
          variant: "destructive",
          title: "Regeneration failed",
          description: message,
        });
        setIsLoading(false);
        setPhase("approval");
      }
    },
    [threadId, toast],
  );

  const handleReset = useCallback(() => {
    setPhase("idle");
    setThreadId(null);
    setCampaignId(null);
    setCampaignStatus("idle");
    setCampaignState(null);
    setAuditLogs([]);
    setIterationHistory([]);
    setIsLoading(false);
  }, []);

  const timelineSteps = useMemo(() => {
    const steps = [
      { id: 1, name: "Brief Parser" },
      { id: 2, name: "Segmentation Agent" },
      { id: 3, name: "Strategy Planner" },
      { id: 4, name: "Content Generator" },
      { id: 5, name: "HITL Approval" },
      { id: 6, name: "Scheduler" },
      { id: 7, name: "Monitor and Optimize" },
    ];

    const completedSteps = getCompletedSteps(phase);
    const activeStep = getActiveStep(phase);
    const hasFailed = campaignStatus === "failed";

    return steps.map((step) => {
      let status: TimelineStatus = "pending";
      if (completedSteps.includes(step.id)) {
        status = "completed";
      } else if (step.id === activeStep) {
        status = hasFailed ? "error" : "active";
      }

      return {
        ...step,
        status,
        timestamp: completedSteps.includes(step.id)
          ? "Completed"
          : step.id === activeStep
            ? hasFailed
              ? "Failed"
              : "In progress"
            : undefined,
      };
    });
  }, [campaignStatus, phase]);

  const parsedBriefData = campaignState?.parsed_brief
    ? {
        product: campaignState.parsed_brief.product_name || "Not specified",
        usp: campaignState.parsed_brief.usp || "Not specified",
        offer: campaignState.parsed_brief.special_offers || "No special offer",
        cta: campaignState.parsed_brief.cta_url || "Not specified",
        tone: campaignState.parsed_brief.tone || "Not specified",
      }
    : null;

  const segmentData = campaignState?.segments
    ? {
        totalAudience:
          Number(campaignState.segments.total) ||
          (campaignState.segments.segment_a?.length || 0) + (campaignState.segments.segment_b?.length || 0),
        groupA: {
          name: "Variant A Cohort",
          count: campaignState.segments.segment_a?.length || 0,
        },
        groupB: {
          name: "Variant B Cohort",
          count: campaignState.segments.segment_b?.length || 0,
        },
        excludedInactive: campaignState.parsed_brief?.include_inactive === false,
      }
    : null;

  const strategyData = campaignState?.strategy_text
    ? {
        sendTime: campaignState.scheduled_time || "Scheduled dynamically after approval",
        targeting: campaignState.segments?.strategy || "A/B split across the live CampaignX cohort",
        testStrategy: campaignState.strategy_text,
      }
    : null;

  const variantA = campaignState?.content_a
    ? {
        id: "a",
        label: "Variant A",
        tone: "Professional",
        subject: campaignState.content_a.subject || "Untitled variant",
        preheader: "Generated from the current campaign brief",
        body: campaignState.content_a.body || "",
      }
    : null;

  const variantB = campaignState?.content_b
    ? {
        id: "b",
        label: "Variant B",
        tone: "Friendly",
        subject: campaignState.content_b.subject || "Untitled variant",
        preheader: "Generated from the current campaign brief",
        body: campaignState.content_b.body || "",
      }
    : null;

  const metricReports = Array.isArray(campaignState?.metrics?.campaigns)
    ? campaignState.metrics.campaigns
    : [];
  const winningVariant = campaignState?.metrics?.winner;

  const metricVariantA = metricReports.find((report) => report.variant === "A") || metricReports[0];
  const metricVariantB = metricReports.find((report) => report.variant === "B") || metricReports[1];

  const metricsDashboardProps = metricVariantA && metricVariantB
    ? {
        variantA: {
          label: "Variant A",
          openRate: toPercent(metricVariantA.open_rate),
          clickRate: toPercent(metricVariantA.click_rate),
          score: Number(metricVariantA.score || 0),
          isWinner: winningVariant === "A",
        },
        variantB: {
          label: "Variant B",
          openRate: toPercent(metricVariantB.open_rate),
          clickRate: toPercent(metricVariantB.click_rate),
          score: Number(metricVariantB.score || 0),
          isWinner: winningVariant === "B",
        },
        iteration: Number(campaignState?.iteration || iterationHistory.length || 1),
        maxIterations: 3,
        campaignStatus: mapMetricsStatus(campaignStatus),
      }
    : null;

  const showParsedBrief = Boolean(parsedBriefData);
  const showSegments = Boolean(segmentData);
  const showStrategy = Boolean(strategyData);
  const showApproval = phase === "approval" && variantA && variantB;
  const showMetrics = Boolean(metricsDashboardProps);
  const heroBrief = campaignState?.brief || SAMPLE_BRIEF;

  return (
    <div className="min-h-screen bg-background">
      <Navbar
        currentSection={section}
        onNavigate={(nextSection) => setSection(nextSection as Section)}
        healthStatus={healthStatus}
      />

      <AnimatePresence mode="wait">
        {section === "home" && (
          <motion.div
            key="home"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          >
            <HeroSection onGetStarted={() => setSection("dashboard")} />
            <AgentWorkflow />
            <WhySection />
            <FeatureHighlights />
          </motion.div>
        )}

        {section === "dashboard" && (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="section-container py-8"
          >
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-display font-bold text-foreground">Campaign Dashboard</h2>
                <p className="mt-1 text-sm text-muted-foreground font-body">
                  {phase === "idle"
                    ? "Submit a campaign brief to start the agent workflow."
                    : `Current status: ${campaignStatus || "processing"}`}
                </p>
              </div>
              {phase !== "idle" && (
                <Button variant="outline" size="sm" onClick={handleReset}>
                  <RotateCcw className="mr-1 h-3.5 w-3.5" />
                  New Campaign
                </Button>
              )}
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
              <div className="space-y-6 lg:col-span-2">
                {phase === "idle" && <BriefInput onSubmit={handleBriefSubmit} isLoading={isLoading} />}

                {phase !== "idle" && !showApproval && !showMetrics && (
                  <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="card-elevated p-6 sm:p-8"
                  >
                    <h3 className="text-lg font-display font-semibold text-foreground">Campaign in Progress</h3>
                    <p className="mt-2 text-sm text-muted-foreground font-body">
                      CampaignX is working through the live cohort and preparing outputs for review.
                    </p>
                    <p className="mt-4 text-xs text-muted-foreground font-body break-words">
                      Active brief: {heroBrief}
                    </p>
                  </motion.div>
                )}

                {showApproval && variantA && variantB && (
                  <ApprovalWorkspace
                    variantA={variantA}
                    variantB={variantB}
                    onApprove={handleApprove}
                    onReject={handleReject}
                    isLoading={isLoading}
                  />
                )}

                {showMetrics && metricsDashboardProps && (
                  <>
                    <MetricsDashboard {...metricsDashboardProps} />
                    <OptimizationHistory iterations={iterationHistory} />
                  </>
                )}
              </div>

              <div className="space-y-6">
                {phase !== "idle" && <ExecutionTimeline steps={timelineSteps} />}
                {showParsedBrief && parsedBriefData && <ParsedBrief data={parsedBriefData} />}
                {showSegments && segmentData && <SegmentSummary data={segmentData} />}
                {showStrategy && strategyData && <StrategySummary data={strategyData} />}
                {(showMetrics || showApproval || auditLogs.length > 0) && <AuditLog entries={auditLogs} />}
              </div>
            </div>
          </motion.div>
        )}

        {section === "history" && (
          <motion.div
            key="history"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="section-container py-8"
          >
            <div className="mb-8">
              <h2 className="text-2xl font-display font-bold text-foreground">Campaign History</h2>
              <p className="mt-1 text-sm text-muted-foreground font-body">
                Real CampaignX runs, their optimization rounds, and the latest recorded scores.
              </p>
            </div>
            <CampaignHistory campaigns={campaignHistory} />
          </motion.div>
        )}
      </AnimatePresence>

      <Footer />
    </div>
  );
};

export default Index;
