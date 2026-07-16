import React from "react";
import { motion } from "motion/react";

interface AuroraBackgroundProps {
  className?: string;
  children?: React.ReactNode;
  intensity?: "subtle" | "default" | "strong";
}

const INTENSITY = {
  subtle: { blue: "rgba(22, 93, 255, 0.06)", purple: "rgba(123, 92, 255, 0.04)" },
  default: { blue: "rgba(22, 93, 255, 0.10)", purple: "rgba(123, 92, 255, 0.07)" },
  strong: { blue: "rgba(22, 93, 255, 0.16)", purple: "rgba(123, 92, 255, 0.10)" },
};

const ORBS = [
  { color: "bg-blue-500/20", size: "h-64 w-64", top: "-5%", left: "-5%", dur: 12, dx: 40, dy: -50 },
  { color: "bg-purple-500/20", size: "h-56 w-56", top: "10%", right: "-8%", dur: 16, dx: -35, dy: -40 },
  { color: "bg-cyan-400/15", size: "h-48 w-48", top: "40%", left: "30%", dur: 11, dx: 25, dy: 30 },
  { color: "bg-indigo-400/15", size: "h-52 w-52", top: "60%", right: "10%", dur: 20, dx: -25, dy: 45 },
  { color: "bg-blue-400/12", size: "h-40 w-40", bottom: "-5%", left: "50%", dur: 14, dx: 20, dy: -30 },
];

function Orb({ color, size, top, right, bottom, left, dur, dx, dy }: typeof ORBS[0]) {
  const style: React.CSSProperties = { position: "absolute" };
  if (top) style.top = top;
  if (right) style.right = right;
  if (bottom) style.bottom = bottom;
  if (left) style.left = left;
  return (
    <motion.div
      className={`pointer-events-none select-none rounded-full blur-3xl ${color} ${size}`}
      style={style}
      animate={{ x: [0, dx, 0], y: [0, dy, 0], scale: [1, 1.15, 1] }}
      transition={{ duration: dur, repeat: Infinity, ease: "easeInOut" }}
      aria-hidden
    />
  );
}

function ShootingStar({ topPct, delay, dur }: { topPct: number; delay: number; dur: number }) {
  const startY = topPct * 6; // approximate px from vh
  const endY = startY + topPct * 2.5;
  return (
    <motion.div
      className="pointer-events-none absolute h-px w-40 overflow-visible"
      initial={{ opacity: 0, x: "-10%", y: startY, rotate: 28 }}
      animate={{ opacity: [0, 1, 0], x: ["-10%", "120%"], y: [startY, endY] }}
      transition={{ duration: dur, repeat: Infinity, repeatDelay: delay, ease: "easeInOut" }}
      style={{ background: "linear-gradient(to right, transparent, rgba(200, 215, 255, 0.9), transparent)" }}
      aria-hidden
    />
  );
}

export function AuroraBackground({ className = "", children, intensity = "default" }: AuroraBackgroundProps) {
  const glow = INTENSITY[intensity];
  return (
    <div className={`relative overflow-hidden ${className}`}>
      {/* Big floating orbs */}
      {ORBS.map((orb, i) => (
        <Orb key={i} {...orb} />
      ))}

      {/* Multiple shooting stars at different positions/delays */}
      <ShootingStar topPct={8} delay={0} dur={1.2} />
      <ShootingStar topPct={15} delay={4} dur={1.5} />
      <ShootingStar topPct={5} delay={7} dur={1.0} />
      <ShootingStar topPct={22} delay={2} dur={1.3} />
      <ShootingStar topPct={30} delay={9} dur={1.6} />
      <ShootingStar topPct={12} delay={5.5} dur={1.1} />

      {/* Top radial glow */}
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-72 select-none"
        style={{
          background: `radial-gradient(ellipse 80% 70% at 50% -10%, ${glow.blue} 0%, ${glow.purple} 45%, transparent 70%)`,
        }}
        aria-hidden
      />
      {/* Bottom-right glow */}
      <div
        className="pointer-events-none absolute inset-x-0 bottom-0 h-48 select-none"
        style={{
          background: `radial-gradient(ellipse 60% 80% at 90% 100%, rgba(14, 165, 255, 0.06) 0%, transparent 65%)`,
        }}
        aria-hidden
      />
      {/* Dot grid */}
      <div
        className="pointer-events-none absolute inset-0 select-none opacity-30"
        style={{
          backgroundImage: "radial-gradient(circle, rgba(22, 93, 255, 0.15) 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
        aria-hidden
      />
      {children && <div className="relative z-10">{children}</div>}
    </div>
  );
}

export default AuroraBackground;
