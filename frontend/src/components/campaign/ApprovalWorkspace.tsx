import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Check, X, Mail, Eye } from "lucide-react";

interface EmailVariant {
  id: string;
  label: string;
  tone: string;
  subject: string;
  preheader: string;
  body: string;
}

interface ApprovalWorkspaceProps {
  variantA: EmailVariant;
  variantB: EmailVariant;
  onApprove: (notes?: string) => void;
  onReject: (notes: string) => void;
  isLoading?: boolean;
}

const VariantCard = ({ variant, selected, onSelect }: { variant: EmailVariant; selected: boolean; onSelect: () => void }) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    className={`card-elevated p-6 cursor-pointer transition-all ${
      selected ? "ring-2 ring-gold border-gold/30" : "hover:border-foreground/10"
    }`}
    onClick={onSelect}
  >
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        <Mail className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-body font-semibold text-foreground">{variant.label}</span>
      </div>
      <span className="badge-status bg-secondary text-muted-foreground">{variant.tone}</span>
    </div>

    <div className="space-y-3">
      <div>
        <span className="text-xs text-muted-foreground font-body uppercase tracking-wide">Subject</span>
        <p className="text-sm font-body font-medium text-foreground mt-1">{variant.subject}</p>
      </div>
      <div>
        <span className="text-xs text-muted-foreground font-body uppercase tracking-wide">Preheader</span>
        <p className="text-sm font-body text-muted-foreground mt-1">{variant.preheader}</p>
      </div>
      <div>
        <span className="text-xs text-muted-foreground font-body uppercase tracking-wide">Body</span>
        <div className="mt-2 p-4 bg-background rounded-md border border-border">
          <p className="text-sm font-body text-foreground leading-relaxed whitespace-pre-wrap">{variant.body}</p>
        </div>
      </div>
    </div>

    {selected && (
      <div className="mt-4 flex items-center gap-2 text-gold">
        <Eye className="h-3.5 w-3.5" />
        <span className="text-xs font-body font-medium">Selected for review</span>
      </div>
    )}
  </motion.div>
);

const ApprovalWorkspace = ({ variantA, variantB, onApprove, onReject, isLoading }: ApprovalWorkspaceProps) => {
  const [selectedVariant, setSelectedVariant] = useState<string | null>(null);
  const [notes, setNotes] = useState("");

  return (
    <section className="py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-display font-bold text-foreground">Approval Required</h3>
          <p className="text-sm text-muted-foreground font-body mt-1">
            Review both variants before approving the campaign for scheduling.
          </p>
        </div>
        <span className="badge-pending">
          <span className="w-1.5 h-1.5 rounded-full bg-gold" />
          Awaiting Review
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <VariantCard variant={variantA} selected={selectedVariant === variantA.id} onSelect={() => setSelectedVariant(variantA.id)} />
        <VariantCard variant={variantB} selected={selectedVariant === variantB.id} onSelect={() => setSelectedVariant(variantB.id)} />
      </div>

      {/* Reviewer notes */}
      <div className="card-elevated p-6 mb-6">
        <h4 className="text-sm font-body font-semibold text-foreground mb-2">Reviewer Notes</h4>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Add any notes or feedback for the campaign audit log..."
          className="w-full h-20 px-3 py-2 bg-background border border-border rounded-md text-sm font-body text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-gold/50 transition-all"
        />
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3">
        <Button variant="reject" onClick={() => onReject(notes)} disabled={isLoading}>
          <X className="h-4 w-4 mr-1" />
          Reject & Regenerate
        </Button>
        <Button variant="approve" onClick={() => onApprove(notes)} disabled={isLoading}>
          <Check className="h-4 w-4 mr-1" />
          Approve & Schedule
        </Button>
      </div>
    </section>
  );
};

export default ApprovalWorkspace;
