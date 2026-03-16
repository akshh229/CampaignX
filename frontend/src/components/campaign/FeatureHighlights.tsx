import { motion } from "framer-motion";
import { Workflow, ShieldCheck, RefreshCw, UserCheck } from "lucide-react";

const features = [
  {
    icon: Workflow,
    title: "Dynamic OpenAPI Tool Calling",
    description: "Campaign scheduling through automatic API endpoint discovery — no hardcoded integrations.",
  },
  {
    icon: ShieldCheck,
    title: "LangGraph Interrupt Approval",
    description: "Deterministic human-in-the-loop gates using LangGraph interrupt nodes for safe, auditable review.",
  },
  {
    icon: RefreshCw,
    title: "A/B Auto-Optimization",
    description: "Weighted scoring regenerates the losing variant automatically, running up to 3 iterations.",
  },
  {
    icon: UserCheck,
    title: "Demographic Personalization",
    description: "Audience segmentation with demographic-aware targeting for precision campaign delivery.",
  },
];

const FeatureHighlights = () => {
  return (
    <section className="py-24 gradient-navy">
      <div className="section-container">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="text-sm font-body font-medium tracking-wider uppercase text-gold">
            Technical Innovations
          </span>
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-cream mt-3 mb-4">
            Built for enterprise campaign ops
          </h2>
          <p className="text-lg text-sand/70 font-body max-w-2xl mx-auto">
            CampaignX combines autonomous AI agents with production-grade controls
            designed for regulated financial services.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {features.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="bg-navy/40 border border-sand/10 rounded-lg p-6 backdrop-blur-sm"
              >
                <div className="w-10 h-10 rounded-lg bg-gold/10 flex items-center justify-center mb-4">
                  <Icon className="h-5 w-5 text-gold" />
                </div>
                <h3 className="text-base font-body font-semibold text-cream mb-2">{feature.title}</h3>
                <p className="text-sm text-sand/60 font-body leading-relaxed">{feature.description}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default FeatureHighlights;
