import { Activity, CheckCircle2, AlertTriangle } from "lucide-react";

interface HealthIndicatorProps {
  status: "healthy" | "degraded" | "down";
}

const config = {
  healthy: { icon: CheckCircle2, label: "All Systems Operational", className: "text-forest" },
  degraded: { icon: AlertTriangle, label: "Degraded Performance", className: "text-terracotta" },
  down: { icon: Activity, label: "Service Disruption", className: "text-oxblood" },
};

const HealthIndicator = ({ status }: HealthIndicatorProps) => {
  const { icon: Icon, label, className } = config[status];

  return (
    <div className={`flex items-center gap-1.5 text-xs font-body ${className}`}>
      <Icon className="h-3.5 w-3.5" />
      <span>{label}</span>
    </div>
  );
};

export default HealthIndicator;
