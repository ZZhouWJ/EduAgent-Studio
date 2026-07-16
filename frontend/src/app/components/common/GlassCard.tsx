import React from "react";
import { motion } from "motion/react";

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  /** hover 时是否上浮 */
  hover?: boolean;
  /** hover 时是否出现蓝紫边框光带 */
  glow?: boolean;
  onClick?: () => void;
  /** 延迟 stagger（秒） */
  delay?: number;
}

export function GlassCard({
  children,
  className = "",
  hover = true,
  glow = true,
  onClick,
  delay = 0,
}: GlassCardProps) {
  return (
    <motion.div
      className={`edu-glass ${hover ? "edu-glass-hover" : ""} ${glow ? "edu-ring-glow" : ""} ${className}`}
      onClick={onClick}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}

export default GlassCard;
