import { motion } from "framer-motion";
import { Clock, Target, TestTubes } from "lucide-react";

interface StrategyData {
  sendTime: string;
  targeting: string;
  testStrategy: string;
}

interface StrategySummaryProps {
  data: StrategyData;
}

const StrategySummary = ({ data }: StrategySummaryProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-elevated p-6"
    >
      <h3 className="text-base font-display font-semibold text-foreground mb-4">Strategy</h3>

      <div className="space-y-3">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-md bg-secondary flex items-center justify-center flex-shrink-0">
            <Clock className="h-4 w-4 text-muted-foreground" />
          </div>
          <div>
            <span className="text-xs text-muted-foreground font-body uppercase tracking-wide">Send Time</span>
            <p className="text-sm font-body text-foreground mt-0.5">{data.sendTime}</p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-md bg-secondary flex items-center justify-center flex-shrink-0">
            <Target className="h-4 w-4 text-muted-foreground" />
          </div>
          <div>
            <span className="text-xs text-muted-foreground font-body uppercase tracking-wide">Targeting</span>
            <p className="text-sm font-body text-foreground mt-0.5">{data.targeting}</p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-md bg-secondary flex items-center justify-center flex-shrink-0">
            <TestTubes className="h-4 w-4 text-muted-foreground" />
          </div>
          <div>
            <span className="text-xs text-muted-foreground font-body uppercase tracking-wide">Test Strategy</span>
            <p className="text-sm font-body text-foreground mt-0.5">{data.testStrategy}</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default StrategySummary;
