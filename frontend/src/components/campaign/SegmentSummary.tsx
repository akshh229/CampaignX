import { motion } from "framer-motion";
import { Users, UserCheck, UserX } from "lucide-react";

interface SegmentData {
  totalAudience: number;
  groupA: { name: string; count: number };
  groupB: { name: string; count: number };
  excludedInactive: boolean;
}

interface SegmentSummaryProps {
  data: SegmentData;
}

const SegmentSummary = ({ data }: SegmentSummaryProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-elevated p-6"
    >
      <h3 className="text-base font-display font-semibold text-foreground mb-4">Segmentation</h3>

      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-secondary rounded-lg p-3 text-center">
          <Users className="h-4 w-4 text-muted-foreground mx-auto mb-1" />
          <p className="text-lg font-body font-bold text-foreground">{data.totalAudience.toLocaleString()}</p>
          <span className="text-xs text-muted-foreground font-body">Total</span>
        </div>
        <div className="bg-secondary rounded-lg p-3 text-center">
          <UserCheck className="h-4 w-4 text-forest mx-auto mb-1" />
          <p className="text-lg font-body font-bold text-foreground">{data.groupA.count.toLocaleString()}</p>
          <span className="text-xs text-muted-foreground font-body">Group A</span>
        </div>
        <div className="bg-secondary rounded-lg p-3 text-center">
          <UserCheck className="h-4 w-4 text-teal mx-auto mb-1" />
          <p className="text-lg font-body font-bold text-foreground">{data.groupB.count.toLocaleString()}</p>
          <span className="text-xs text-muted-foreground font-body">Group B</span>
        </div>
      </div>

      <div className="flex items-center gap-2 text-xs font-body text-muted-foreground">
        {data.excludedInactive ? (
          <UserX className="h-3.5 w-3.5 text-terracotta" />
        ) : (
          <UserCheck className="h-3.5 w-3.5 text-forest" />
        )}
        <span>
          {data.excludedInactive
            ? "Inactive users excluded"
            : "Inactive users included per brief instructions"}
        </span>
      </div>
    </motion.div>
  );
};

export default SegmentSummary;
