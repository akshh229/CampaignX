import { motion } from "framer-motion";
import { FileText, Clock } from "lucide-react";

interface AuditEntry {
  id: string;
  action: string;
  agent: string;
  timestamp: string;
  detail?: string;
}

interface AuditLogProps {
  entries: AuditEntry[];
}

const AuditLog = ({ entries }: AuditLogProps) => {
  if (entries.length === 0) {
    return (
      <div className="card-elevated p-8 text-center">
        <FileText className="h-6 w-6 text-muted-foreground mx-auto mb-2" />
        <p className="text-sm text-muted-foreground font-body">No audit entries yet.</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-elevated p-6"
    >
      <div className="flex items-center gap-2 mb-4">
        <FileText className="h-4 w-4 text-muted-foreground" />
        <h3 className="text-base font-display font-semibold text-foreground">Audit Log</h3>
      </div>

      <div className="space-y-3 max-h-80 overflow-y-auto">
        {entries.map((entry) => (
          <div key={entry.id} className="flex items-start gap-3 py-2 border-b border-border/50 last:border-0">
            <div className="flex items-center gap-1 text-xs text-muted-foreground font-body whitespace-nowrap mt-0.5">
              <Clock className="h-3 w-3" />
              {entry.timestamp}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-body font-medium text-foreground">{entry.action}</span>
                <span className="text-xs text-muted-foreground font-body">by {entry.agent}</span>
              </div>
              {entry.detail && (
                <p className="text-xs text-muted-foreground font-body mt-0.5">{entry.detail}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default AuditLog;
