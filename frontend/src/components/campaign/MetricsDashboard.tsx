import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, BarChart3, MousePointerClick, Mail, Trophy } from "lucide-react";

interface VariantMetrics {
  label: string;
  openRate: number;
  clickRate: number;
  score: number;
  isWinner?: boolean;
}

interface MetricsDashboardProps {
  variantA: VariantMetrics;
  variantB: VariantMetrics;
  iteration: number;
  maxIterations: number;
  campaignStatus: "running" | "optimizing" | "completed" | "paused";
}

const ScoreBar = ({ score, maxScore = 1, color }: { score: number; maxScore?: number; color: string }) => (
  <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
    <motion.div
      initial={{ width: 0 }}
      animate={{ width: `${(score / maxScore) * 100}%` }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className={`h-full rounded-full ${color}`}
    />
  </div>
);

const MetricCard = ({ label, value, suffix = "%", icon: Icon, trend }: {
  label: string; value: number; suffix?: string; icon: React.ElementType; trend?: "up" | "down"
}) => (
  <div className="bg-secondary rounded-lg p-4">
    <div className="flex items-center justify-between mb-2">
      <Icon className="h-4 w-4 text-muted-foreground" />
      {trend && (
        trend === "up"
          ? <TrendingUp className="h-3.5 w-3.5 text-forest" />
          : <TrendingDown className="h-3.5 w-3.5 text-oxblood" />
      )}
    </div>
    <p className="text-2xl font-body font-bold text-foreground">{value.toFixed(1)}{suffix}</p>
    <span className="text-xs text-muted-foreground font-body">{label}</span>
  </div>
);

const VariantRow = ({ variant }: { variant: VariantMetrics }) => (
  <div className={`card-elevated p-5 ${variant.isWinner ? "ring-2 ring-gold" : ""}`}>
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        <span className="text-sm font-body font-semibold text-foreground">{variant.label}</span>
        {variant.isWinner && (
          <span className="badge-active">
            <Trophy className="h-3 w-3" />
            Winner
          </span>
        )}
      </div>
      <span className="text-lg font-body font-bold text-foreground">
        {variant.score.toFixed(3)}
      </span>
    </div>

    <div className="space-y-3">
      <div>
        <div className="flex justify-between text-xs font-body text-muted-foreground mb-1">
          <span>Open Rate ({variant.openRate.toFixed(1)}%)</span>
          <span className="text-foreground/60">weight: 0.3</span>
        </div>
        <ScoreBar score={variant.openRate} maxScore={100} color="bg-teal" />
      </div>
      <div>
        <div className="flex justify-between text-xs font-body text-muted-foreground mb-1">
          <span>Click Rate ({variant.clickRate.toFixed(1)}%)</span>
          <span className="text-foreground/60">weight: 0.7</span>
        </div>
        <ScoreBar score={variant.clickRate} maxScore={100} color="bg-navy" />
      </div>
    </div>

    <div className="mt-4 pt-3 border-t border-border">
      <span className="text-xs font-body text-muted-foreground">
        Score = (click × 0.7) + (open × 0.3) = {variant.score.toFixed(3)}
      </span>
    </div>
  </div>
);

const statusLabels: Record<string, { label: string; className: string }> = {
  running: { label: "Running", className: "badge-active" },
  optimizing: { label: "Optimizing", className: "badge-pending" },
  completed: { label: "Completed", className: "badge-active" },
  paused: { label: "Paused", className: "badge-status bg-secondary text-muted-foreground" },
};

const MetricsDashboard = ({ variantA, variantB, iteration, maxIterations, campaignStatus }: MetricsDashboardProps) => {
  const status = statusLabels[campaignStatus];
  const bestVariant = variantA.score >= variantB.score ? variantA : variantB;

  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="py-8"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-display font-bold text-foreground">Campaign Performance</h3>
          <p className="text-sm text-muted-foreground font-body mt-1">
            Iteration {iteration} of {maxIterations} · Weighted scoring active
          </p>
        </div>
        <span className={status.className}>
          <span className="w-1.5 h-1.5 rounded-full bg-current" />
          {status.label}
        </span>
      </div>

      {/* Summary metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Best Open Rate" value={bestVariant.openRate} icon={Mail} trend="up" />
        <MetricCard label="Best Click Rate" value={bestVariant.clickRate} icon={MousePointerClick} trend="up" />
        <MetricCard label="Top Score" value={bestVariant.score} suffix="" icon={BarChart3} />
        <MetricCard label="Iteration" value={iteration} suffix={` / ${maxIterations}`} icon={TrendingUp} />
      </div>

      {/* Variant comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <VariantRow variant={variantA} />
        <VariantRow variant={variantB} />
      </div>
    </motion.section>
  );
};

export default MetricsDashboard;
