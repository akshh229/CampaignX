import { motion } from "framer-motion";
import { Package, Star, Tag, MousePointerClick, Palette } from "lucide-react";

interface ParsedBriefData {
  product: string;
  usp: string;
  offer: string;
  cta: string;
  tone: string;
}

interface ParsedBriefProps {
  data: ParsedBriefData;
}

const fields = [
  { key: "product", label: "Product", icon: Package },
  { key: "usp", label: "USP", icon: Star },
  { key: "offer", label: "Offer", icon: Tag },
  { key: "cta", label: "CTA", icon: MousePointerClick },
  { key: "tone", label: "Tone", icon: Palette },
] as const;

const ParsedBrief = ({ data }: ParsedBriefProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-elevated p-6"
    >
      <h3 className="text-base font-display font-semibold text-foreground mb-4">Parsed Brief</h3>
      <div className="space-y-3">
        {fields.map(({ key, label, icon: Icon }) => (
          <div key={key} className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-md bg-secondary flex items-center justify-center flex-shrink-0 mt-0.5">
              <Icon className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="min-w-0">
              <span className="text-xs text-muted-foreground font-body uppercase tracking-wide">{label}</span>
              <p className="text-sm font-body text-foreground mt-0.5 break-words">{data[key]}</p>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default ParsedBrief;
