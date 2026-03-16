import { motion } from "framer-motion";
import { RefreshCw, TrendingUp, TrendingDown } from "lucide-react";

interface IterationRecord {
  iteration: number;
  variantAScore: number;
  variantBScore: number;
  winner: "A" | "B";
  action: string;
}

interface OptimizationHistoryProps {
  iterations: IterationRecord[];
}

const OptimizationHistory = ({ iterations }: OptimizationHistoryProps) => {
  if (iterations.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-elevated p-6"
    >
      <div className="flex items-center gap-2 mb-4">
        <RefreshCw className="h-4 w-4 text-muted-foreground" />
        <h3 className="text-base font-display font-semibold text-foreground">Optimization History</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm font-body">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 pr-4 text-xs text-muted-foreground font-medium uppercase tracking-wide">Iter.</th>
              <th className="text-left py-2 pr-4 text-xs text-muted-foreground font-medium uppercase tracking-wide">Variant A</th>
              <th className="text-left py-2 pr-4 text-xs text-muted-foreground font-medium uppercase tracking-wide">Variant B</th>
              <th className="text-left py-2 pr-4 text-xs text-muted-foreground font-medium uppercase tracking-wide">Winner</th>
              <th className="text-left py-2 text-xs text-muted-foreground font-medium uppercase tracking-wide">Action</th>
            </tr>
          </thead>
          <tbody>
            {iterations.map((iter) => (
              <tr key={iter.iteration} className="border-b border-border/50 last:border-0">
                <td className="py-3 pr-4 text-foreground font-medium">#{iter.iteration}</td>
                <td className="py-3 pr-4">
                  <span className={iter.winner === "A" ? "text-forest font-medium" : "text-muted-foreground"}>
                    {iter.variantAScore.toFixed(3)}
                  </span>
                </td>
                <td className="py-3 pr-4">
                  <span className={iter.winner === "B" ? "text-forest font-medium" : "text-muted-foreground"}>
                    {iter.variantBScore.toFixed(3)}
                  </span>
                </td>
                <td className="py-3 pr-4">
                  <span className="badge-active text-xs">
                    {iter.winner === "A" ? (
                      <TrendingUp className="h-3 w-3" />
                    ) : (
                      <TrendingDown className="h-3 w-3" />
                    )}
                    Variant {iter.winner}
                  </span>
                </td>
                <td className="py-3 text-muted-foreground">{iter.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

export default OptimizationHistory;
