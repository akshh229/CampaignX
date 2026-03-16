import { motion } from "framer-motion";
import { Check, Loader2, Circle, AlertCircle } from "lucide-react";

interface TimelineStep {
  id: number;
  name: string;
  status: "completed" | "active" | "pending" | "error";
  timestamp?: string;
  detail?: string;
}

interface ExecutionTimelineProps {
  steps: TimelineStep[];
}

const statusConfig = {
  completed: {
    icon: Check,
    dotClass: "bg-forest text-cream",
    lineClass: "bg-forest",
    textClass: "text-foreground",
  },
  active: {
    icon: Loader2,
    dotClass: "bg-gold text-primary",
    lineClass: "bg-border",
    textClass: "text-foreground font-semibold",
  },
  pending: {
    icon: Circle,
    dotClass: "bg-secondary text-muted-foreground",
    lineClass: "bg-border",
    textClass: "text-muted-foreground",
  },
  error: {
    icon: AlertCircle,
    dotClass: "bg-oxblood text-cream",
    lineClass: "bg-oxblood/30",
    textClass: "text-oxblood",
  },
};

const ExecutionTimeline = ({ steps }: ExecutionTimelineProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-elevated p-6"
    >
      <h3 className="text-base font-display font-semibold text-foreground mb-5">Agent Execution</h3>

      <div className="space-y-0">
        {steps.map((step, i) => {
          const config = statusConfig[step.status];
          const Icon = config.icon;
          const isLast = i === steps.length - 1;

          return (
            <div key={step.id} className="flex gap-3">
              {/* Timeline column */}
              <div className="flex flex-col items-center">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${config.dotClass}`}>
                  <Icon className={`h-3.5 w-3.5 ${step.status === "active" ? "animate-spin" : ""}`} />
                </div>
                {!isLast && <div className={`w-px flex-1 min-h-[24px] ${config.lineClass}`} />}
              </div>

              {/* Content */}
              <div className={`pb-4 ${isLast ? "" : ""}`}>
                <p className={`text-sm font-body ${config.textClass}`}>{step.name}</p>
                {step.detail && (
                  <p className="text-xs font-body text-muted-foreground mt-0.5">{step.detail}</p>
                )}
                {step.timestamp && (
                  <span className="text-xs font-body text-muted-foreground/60">{step.timestamp}</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
};

export default ExecutionTimeline;
