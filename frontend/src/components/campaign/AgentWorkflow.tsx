import { motion } from "framer-motion";
import { FileText, Users, Target, PenTool, ShieldCheck, Send, BarChart3, Check } from "lucide-react";

const agents = [
  {
    id: 1,
    name: "Brief Parser",
    description: "Extracts product, USP, offer, CTA, and tone from natural language input.",
    icon: FileText,
    color: "navy",
  },
  {
    id: 2,
    name: "Segmentation Agent",
    description: "Fetches customer cohort data and creates A/B audience segments.",
    icon: Users,
    color: "teal",
  },
  {
    id: 3,
    name: "Strategy Planner",
    description: "Decides send timing, targeting strategy, and test configuration.",
    icon: Target,
    color: "forest",
  },
  {
    id: 4,
    name: "Content Generator",
    description: "Generates two email variants — one formal, one friendly — with personalization.",
    icon: PenTool,
    color: "gold",
  },
  {
    id: 5,
    name: "HITL Approval",
    description: "Pauses execution for human review. Approve, reject, or request changes.",
    icon: ShieldCheck,
    color: "oxblood",
  },
  {
    id: 6,
    name: "Scheduler",
    description: "Schedules campaigns via dynamic OpenAPI-driven endpoint discovery.",
    icon: Send,
    color: "navy",
  },
  {
    id: 7,
    name: "Monitor & Optimize",
    description: "Tracks performance, scores variants, regenerates losers. Up to 3 iterations.",
    icon: BarChart3,
    color: "terracotta",
  },
];

const colorMap: Record<string, string> = {
  navy: "bg-navy text-cream",
  teal: "bg-teal text-cream",
  forest: "bg-forest text-cream",
  gold: "bg-gold text-primary",
  oxblood: "bg-oxblood text-cream",
  terracotta: "bg-terracotta text-cream",
};

const borderColorMap: Record<string, string> = {
  navy: "border-navy/20",
  teal: "border-teal/20",
  forest: "border-forest/20",
  gold: "border-gold/20",
  oxblood: "border-oxblood/20",
  terracotta: "border-terracotta/20",
};

interface AgentWorkflowProps {
  activeStep?: number;
  completedSteps?: number[];
}

const AgentWorkflow = ({ activeStep, completedSteps = [] }: AgentWorkflowProps) => {
  return (
    <section className="py-24 bg-background">
      <div className="section-container">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="text-sm font-body font-medium tracking-wider uppercase text-muted-foreground">
            Orchestration
          </span>
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-foreground mt-3 mb-4">
            Seven agents. One workflow.
          </h2>
          <p className="text-lg text-muted-foreground font-body max-w-2xl mx-auto">
            Each campaign moves through a deterministic pipeline of specialized agents,
            with a human approval gate before any email is sent.
          </p>
        </motion.div>

        <div className="relative">
          {/* Connecting line */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-px bg-border -translate-y-1/2 z-0" />

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-4 relative z-10">
            {agents.map((agent, i) => {
              const Icon = agent.icon;
              const isActive = activeStep === agent.id;
              const isCompleted = completedSteps.includes(agent.id);

              return (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.08 }}
                  className={`card-elevated p-4 text-center relative ${
                    isActive ? "ring-2 ring-gold" : ""
                  } ${borderColorMap[agent.color] || ""}`}
                >
                  <div className={`w-10 h-10 rounded-lg ${colorMap[agent.color]} flex items-center justify-center mx-auto mb-3 relative`}>
                    {isCompleted ? (
                      <Check className="h-5 w-5" />
                    ) : (
                      <Icon className="h-5 w-5" />
                    )}
                    {isActive && (
                      <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-gold animate-pulse-subtle" />
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground font-body">Step {agent.id}</span>
                  <h3 className="text-sm font-semibold font-body text-foreground mt-1 mb-2">{agent.name}</h3>
                  <p className="text-xs text-muted-foreground font-body leading-relaxed hidden lg:block">
                    {agent.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};

export default AgentWorkflow;
