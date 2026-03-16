import { motion } from "framer-motion";
import { Calendar, ChevronRight, Trophy, RotateCcw } from "lucide-react";

interface CampaignRecord {
  id: string;
  name: string;
  product: string;
  status: "completed" | "running" | "paused" | "failed";
  iterations: number;
  winningVariant?: string;
  topScore?: number;
  date: string;
}

interface CampaignHistoryProps {
  campaigns: CampaignRecord[];
  onSelect?: (id: string) => void;
}

const statusStyles: Record<string, string> = {
  completed: "badge-active",
  running: "badge-pending",
  paused: "badge-status bg-secondary text-muted-foreground",
  failed: "badge-error",
};

const CampaignHistory = ({ campaigns, onSelect }: CampaignHistoryProps) => {
  if (campaigns.length === 0) {
    return (
      <div className="card-elevated p-12 text-center">
        <RotateCcw className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
        <h4 className="text-base font-display font-semibold text-foreground mb-1">No campaigns yet</h4>
        <p className="text-sm text-muted-foreground font-body">
          Submit your first brief to start a campaign.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {campaigns.map((campaign, i) => (
        <motion.div
          key={campaign.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
          onClick={() => onSelect?.(campaign.id)}
          className="card-elevated p-5 cursor-pointer hover:border-foreground/10 transition-all group"
        >
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-1">
                <h4 className="text-sm font-body font-semibold text-foreground truncate">{campaign.name}</h4>
                <span className={statusStyles[campaign.status]}>
                  <span className="w-1.5 h-1.5 rounded-full bg-current" />
                  {campaign.status}
                </span>
              </div>
              <div className="flex items-center gap-4 text-xs text-muted-foreground font-body">
                <span className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {campaign.date}
                </span>
                <span>{campaign.product}</span>
                <span>{campaign.iterations} iteration{campaign.iterations !== 1 ? "s" : ""}</span>
                {campaign.topScore !== undefined && (
                  <span className="flex items-center gap-1">
                    <Trophy className="h-3 w-3 text-gold" />
                    {campaign.topScore.toFixed(3)}
                  </span>
                )}
              </div>
            </div>
            <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors flex-shrink-0" />
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default CampaignHistory;
