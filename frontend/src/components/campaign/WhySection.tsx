import { motion } from "framer-motion";
import { Clock, Brain, ShieldCheck, TrendingUp } from "lucide-react";

const reasons = [
  {
    icon: Clock,
    title: "Hours to minutes",
    description: "What takes a campaign team 2–3 days runs in under 10 minutes with full audit trail.",
  },
  {
    icon: Brain,
    title: "Consistent strategy",
    description: "AI agents apply the same rigorous segmentation and personalization logic every time.",
  },
  {
    icon: ShieldCheck,
    title: "Human oversight, always",
    description: "No email sends without explicit human approval. Compliant with BFSI governance standards.",
  },
  {
    icon: TrendingUp,
    title: "Continuous optimization",
    description: "Automated A/B testing with weighted scoring means every campaign improves itself.",
  },
];

const WhySection = () => {
  return (
    <section className="py-24 bg-background">
      <div className="section-container">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-2xl mb-16"
        >
          <span className="text-sm font-body font-medium tracking-wider uppercase text-muted-foreground">
            Why CampaignX
          </span>
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-foreground mt-3 mb-4">
            Built for the teams who run campaigns every day
          </h2>
          <p className="text-lg text-muted-foreground font-body">
            Campaign managers at financial institutions don't need another chatbot.
            They need an operations platform that handles the repetitive work
            while keeping them in control.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {reasons.map((reason, i) => {
            const Icon = reason.icon;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="group"
              >
                <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center mb-4 group-hover:bg-gold/10 transition-colors">
                  <Icon className="h-5 w-5 text-muted-foreground group-hover:text-gold transition-colors" />
                </div>
                <h3 className="text-base font-body font-semibold text-foreground mb-2">{reason.title}</h3>
                <p className="text-sm text-muted-foreground font-body leading-relaxed">{reason.description}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default WhySection;
