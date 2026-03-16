import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ArrowRight, Zap } from "lucide-react";

interface HeroSectionProps {
  onGetStarted: () => void;
}

const HeroSection = ({ onGetStarted }: HeroSectionProps) => {
  return (
    <section className="relative overflow-hidden gradient-navy min-h-[85vh] flex items-center">
      {/* Subtle pattern overlay */}
      <div className="absolute inset-0 opacity-[0.03]" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
      }} />

      <div className="section-container relative z-10 py-20">
        <div className="max-w-3xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center gap-2 mb-6">
              <div className="h-px w-8 bg-gold" />
              <span className="text-gold text-sm font-body font-medium tracking-wider uppercase">
                Autonomous Campaign Operations
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-display font-bold text-cream leading-[1.1] mb-6">
              Your campaigns run themselves.{" "}
              <span className="text-gold italic">You approve the results.</span>
            </h1>

            <p className="text-lg sm:text-xl text-sand/80 font-body leading-relaxed mb-10 max-w-2xl">
              CampaignX replaces manual campaign ops with a 7-agent AI workflow.
              From brief to optimized delivery — segmentation, content, approval,
              scheduling, and A/B optimization happen autonomously.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-4"
          >
            <Button variant="hero" size="lg" onClick={onGetStarted} className="text-base">
              Launch a Campaign
              <ArrowRight className="ml-1 h-4 w-4" />
            </Button>
            <Button variant="outline" size="lg" className="text-base border-sand/20 text-sand hover:bg-sand/10 hover:text-cream">
              See How It Works
              <Zap className="ml-1 h-4 w-4" />
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="mt-16 flex items-center gap-8 text-sand/50 text-sm font-body"
          >
            <span>Built for SuperBFSI</span>
            <span className="h-4 w-px bg-sand/20" />
            <span>7 Autonomous Agents</span>
            <span className="h-4 w-px bg-sand/20" />
            <span>Human-in-the-Loop Approval</span>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
