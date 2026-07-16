import React from "react";

interface AuroraBackgroundProps {
  className?: string;
  children?: React.ReactNode;
  intensity?: "subtle" | "default" | "strong";
}

const DOT_OPACITY = {
  subtle: "opacity-20",
  default: "opacity-30",
  strong: "opacity-40",
};

export function AuroraBackground({ className = "", children, intensity = "default" }: AuroraBackgroundProps) {
  return (
    <div className={`relative overflow-hidden ${className}`}>
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-blue-200/70" aria-hidden />
      <div
        className={`pointer-events-none absolute inset-0 select-none ${DOT_OPACITY[intensity]}`}
        style={{
          backgroundImage: "radial-gradient(circle, rgba(37, 99, 235, 0.16) 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
        aria-hidden
      />
      {children && <div className="relative z-10">{children}</div>}
    </div>
  );
}

export default AuroraBackground;
