import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";
import HealthIndicator from "./HealthIndicator";

interface NavbarProps {
  onNavigate: (section: string) => void;
  currentSection: string;
  healthStatus: "healthy" | "degraded" | "down";
}

const Navbar = ({ onNavigate, currentSection, healthStatus }: NavbarProps) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const links = [
    { id: "home", label: "Home" },
    { id: "dashboard", label: "Dashboard" },
    { id: "history", label: "History" },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="section-container">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-6">
            <button
              onClick={() => onNavigate("home")}
              className="text-base font-display font-bold text-foreground tracking-tight"
            >
              Campaign<span className="text-gold">X</span>
            </button>

            <div className="hidden sm:flex items-center gap-1">
              {links.map((link) => (
                <button
                  key={link.id}
                  onClick={() => onNavigate(link.id)}
                  className={`px-3 py-1.5 rounded-md text-sm font-body transition-colors ${
                    currentSection === link.id
                      ? "bg-secondary text-foreground font-medium"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {link.label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:block">
              <HealthIndicator status={healthStatus} />
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="sm:hidden"
              onClick={() => setMobileOpen(!mobileOpen)}
            >
              {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="sm:hidden py-3 border-t border-border space-y-1">
            {links.map((link) => (
              <button
                key={link.id}
                onClick={() => { onNavigate(link.id); setMobileOpen(false); }}
                className={`block w-full text-left px-3 py-2 rounded-md text-sm font-body transition-colors ${
                  currentSection === link.id
                    ? "bg-secondary text-foreground font-medium"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {link.label}
              </button>
            ))}
            <div className="px-3 pt-2">
              <HealthIndicator status={healthStatus} />
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
