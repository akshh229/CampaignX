const Footer = () => {
  return (
    <footer className="border-t border-border py-12 bg-background">
      <div className="section-container">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span className="text-base font-display font-bold text-foreground tracking-tight">
              Campaign<span className="text-gold">X</span>
            </span>
            <p className="text-xs text-muted-foreground font-body mt-1">
              Autonomous AI campaign operations for SuperBFSI
            </p>
          </div>
          <div className="text-xs text-muted-foreground font-body">
            Built with LangGraph · Multi-Agent Architecture · Human-in-the-Loop
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
