import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Send, RotateCcw } from "lucide-react";

const SAMPLE_BRIEF = `Run email campaign for launching XDeposit, a flagship term deposit product from SuperBFSI, that gives 1 percentage point higher returns than its competitors. Announce an additional 0.25 percentage point higher returns for female senior citizens. Optimise for open rate and click rate. Don't skip emails to customers marked inactive. Include the call to action: https://superbfsi.com/xdeposit/explore/`;

interface BriefInputProps {
  onSubmit: (brief: string) => void;
  isLoading?: boolean;
}

const BriefInput = ({ onSubmit, isLoading = false }: BriefInputProps) => {
  const [brief, setBrief] = useState("");

  const handleUseSample = () => {
    setBrief(SAMPLE_BRIEF);
  };

  const handleSubmit = () => {
    if (brief.trim()) {
      onSubmit(brief.trim());
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-elevated p-6 sm:p-8"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-display font-semibold text-foreground">Campaign Brief</h3>
          <p className="text-sm text-muted-foreground font-body mt-1">
            Describe your campaign in plain English. The agents will handle the rest.
          </p>
        </div>
        <button
          onClick={handleUseSample}
          className="text-xs font-body font-medium text-gold hover:text-gold/80 transition-colors underline underline-offset-2"
        >
          Use sample brief
        </button>
      </div>

      <textarea
        value={brief}
        onChange={(e) => setBrief(e.target.value)}
        placeholder="Describe your campaign objectives, target audience, product details, and any specific requirements..."
        className="w-full h-40 px-4 py-3 bg-background border border-border rounded-lg text-sm font-body text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-gold/50 focus:border-gold/50 transition-all"
      />

      <div className="flex items-center justify-between mt-4">
        <span className="text-xs text-muted-foreground font-body">
          {brief.length} characters
        </span>
        <div className="flex gap-3">
          {brief && (
            <Button variant="ghost" size="sm" onClick={() => setBrief("")}>
              <RotateCcw className="h-3.5 w-3.5 mr-1" />
              Clear
            </Button>
          )}
          <Button
            variant="hero"
            size="sm"
            onClick={handleSubmit}
            disabled={!brief.trim() || isLoading}
          >
            {isLoading ? (
              <>
                <span className="animate-pulse-subtle">Processing...</span>
              </>
            ) : (
              <>
                Launch Campaign
                <Send className="h-3.5 w-3.5 ml-1" />
              </>
            )}
          </Button>
        </div>
      </div>
    </motion.div>
  );
};

export default BriefInput;
