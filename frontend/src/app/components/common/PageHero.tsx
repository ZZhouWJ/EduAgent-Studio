import React from "react";
import { motion } from "motion/react";
import { Bot, BookOpen, BrainCircuit } from "lucide-react";

interface PageHeroProps {
  eyebrow?: string;
  title: string;
  description?: string;
  icon?: React.ComponentType<{ className?: string; strokeWidth?: number | string; size?: number | string }>;
  action?: React.ReactNode;
  className?: string;
  /** "student" | "teacher" | "admin" */
  role?: string;
}

const roleAccents: Record<string, { icon: React.ComponentType<{ className?: string }>; color: string; gradient: string; barColor: string }> = {
  student: { icon: BrainCircuit, color: "text-cyan-600", gradient: "from-cyan-400 to-blue-600", barColor: "#06b6d4" },
  teacher: { icon: Bot, color: "text-purple-600", gradient: "from-purple-400 to-blue-600", barColor: "#7c3aed" },
  admin: { icon: BookOpen, color: "text-emerald-600", gradient: "from-emerald-400 to-blue-600", barColor: "#10b981" },
};

export function PageHero({
  eyebrow,
  title,
  description,
  icon: Icon,
  action,
  className = "",
  role,
}: PageHeroProps) {
  const accent = roleAccents[role ?? "student"];

  return (
    <motion.section
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className={`edu-card edu-top-bar relative overflow-hidden p-6 sm:p-7 ${className}`}
    >
      {/* Top-left accent bar */}
      <motion.div
        className="pointer-events-none absolute inset-x-0 top-0 h-1"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 0.8, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
        style={{
          background: `linear-gradient(90deg, ${accent.barColor}99, ${accent.barColor}66, transparent)`,
          transformOrigin: "left",
        }}
        aria-hidden
      />

      {/* Left glow */}
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-full select-none"
        style={{
          background: `radial-gradient(ellipse 40% 80% at -5% 50%, rgba(22, 93, 255, 0.08) 0%, transparent 65%)`,
        }}
        aria-hidden
      />

      <div className="relative flex flex-col items-stretch justify-between gap-5 lg:flex-row lg:items-start lg:gap-6">
        {/* Left: text content */}
        <div className="min-w-0 flex-1">
          {eyebrow && (
            <motion.div
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15, duration: 0.35 }}
              className="mb-4 flex w-fit items-center gap-2 border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-600"
            >
              {Icon && <Icon className="h-3.5 w-3.5" strokeWidth={2} />}
              {eyebrow}
            </motion.div>
          )}

          <motion.h1
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
            className="text-2xl font-black leading-tight tracking-tight text-slate-900 sm:text-[30px]"
          >
            {title}
          </motion.h1>

          {description && (
            <motion.p
              className="mt-2 max-w-2xl text-sm leading-6 text-slate-500"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35, duration: 0.4 }}
            >
              {description}
            </motion.p>
          )}
        </div>

        {/* Right: action + decorative icon */}
        {(action || Icon) && (
          <div className="flex shrink-0 flex-col items-end gap-3">
            {action && <div className="flex shrink-0 flex-col gap-2 sm:flex-row lg:justify-end">{action}</div>}
            {Icon && (
              <motion.div
                initial={{ opacity: 0, scale: 0.5, rotate: -10 }}
                animate={{ opacity: 1, scale: 1, rotate: 0 }}
                transition={{ delay: 0.25, duration: 0.5, type: "spring", stiffness: 180, damping: 12 }}
                className={`hidden h-14 w-14 shrink-0 items-center justify-center border-0 bg-gradient-to-br ${accent.gradient} p-0 shadow-lg lg:flex`}
              >
                {/* Outer pulse rings */}
                <motion.div
                  className="absolute border-2 border-white/30"
                  animate={{ scale: [1, 1.8], opacity: [0.6, 0] }}
                  transition={{ duration: 1.8, repeat: Infinity, ease: "easeOut" }}
                  style={{ width: "100%", height: "100%" }}
                />
                <motion.div
                  className="absolute border border-white/20"
                  animate={{ scale: [1, 2.2], opacity: [0.4, 0] }}
                  transition={{ duration: 1.8, repeat: Infinity, ease: "easeOut", delay: 0.3 }}
                  style={{ width: "100%", height: "100%" }}
                />
                <Icon className="relative z-10 h-7 w-7 text-white" strokeWidth={2} />
              </motion.div>
            )}
          </div>
        )}
      </div>
    </motion.section>
  );
}

export default PageHero;
