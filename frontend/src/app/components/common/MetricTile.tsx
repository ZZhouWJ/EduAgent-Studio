import React from "react";
import { motion } from "motion/react";
import { Sparkles } from "lucide-react";
import { Sparkline } from "./Sparkline";

interface MetricTileProps {
  label: string;
  value: string | number;
  hint?: string;
  icon?: React.ComponentType<{ className?: string }>;
  tone?: "blue" | "purple" | "cyan" | "emerald" | "orange" | "red" | "slate";
  sparkline?: number[];
  trend?: "up" | "down" | "neutral";
  delay?: number;
}

const toneConfig: Record<string, { bg: string; text: string; ring: string; sparkColor: string }> = {
  blue: { bg: "bg-blue-50", text: "text-blue-600", ring: "ring-blue-100", sparkColor: "#165DFF" },
  purple: { bg: "bg-purple-50", text: "text-purple-600", ring: "ring-purple-100", sparkColor: "#7B5CFF" },
  cyan: { bg: "bg-cyan-50", text: "text-cyan-600", ring: "ring-cyan-100", sparkColor: "#0EA5FF" },
  emerald: { bg: "bg-emerald-50", text: "text-emerald-600", ring: "ring-emerald-100", sparkColor: "#10B981" },
  orange: { bg: "bg-orange-50", text: "text-orange-600", ring: "ring-orange-100", sparkColor: "#F59E0B" },
  red: { bg: "bg-red-50", text: "text-red-600", ring: "ring-red-100", sparkColor: "#EF4444" },
  slate: { bg: "bg-slate-100", text: "text-slate-600", ring: "ring-slate-200", sparkColor: "#64748B" },
};

export function MetricTile({
  label,
  value,
  hint,
  icon: Icon,
  tone = "blue",
  sparkline,
  trend,
  delay = 0,
}: MetricTileProps) {
  const cfg = toneConfig[tone];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
      className="edu-card edu-card-hover group relative flex flex-col gap-3 p-5"
    >
      {/* Icon badge */}
      <div className={`grid h-10 w-10 place-items-center rounded-xl ring-1 ${cfg.bg} ${cfg.text} ${cfg.ring}`}>
        {Icon ? <Icon className="h-5 w-5" /> : <Sparkles className="h-5 w-5" />}
      </div>

      {/* Label */}
      <div className="text-sm font-semibold text-slate-500">{label}</div>

      {/* Value row */}
      <div className="flex items-end justify-between">
        <motion.div
          key={String(value)}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="text-[28px] font-black leading-none tracking-tight text-slate-900 edu-num"
        >
          {value}
        </motion.div>
        {trend && (
          <span className={`mb-1 text-xs font-bold ${trend === "up" ? "text-emerald-600" : trend === "down" ? "text-red-600" : "text-slate-400"}`}>
            {trend === "up" ? "↑" : trend === "down" ? "↓" : "—"}
          </span>
        )}
      </div>

      {/* Hint */}
      {hint && <div className="text-xs font-medium text-slate-400">{hint}</div>}

      {/* Sparkline */}
      {sparkline && sparkline.length > 1 && (
        <div className="-mx-1 mt-1">
          <Sparkline data={sparkline} color={cfg.sparkColor} height={38} className="w-full" />
        </div>
      )}

      {/* Hover accent border */}
      <div className="absolute inset-x-0 top-0 h-px rounded-t-[18px] opacity-0 transition-opacity duration-200 group-hover:opacity-100"
        style={{
          background: `linear-gradient(90deg, transparent 0%, ${cfg.sparkColor}55 40%, ${cfg.sparkColor}55 60%, transparent 100%)`,
        }}
        aria-hidden
      />
    </motion.div>
  );
}

export default MetricTile;
