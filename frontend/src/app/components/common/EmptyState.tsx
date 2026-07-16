import React from "react";
import { motion } from "motion/react";
import { Inbox } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  icon?: React.ComponentType<{ className?: string; strokeWidth?: number | string }>;
  className?: string;
}

export function EmptyState({
  title,
  description,
  action,
  icon: Icon = Inbox,
  className = "",
}: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      className={`edu-glass flex flex-col items-center justify-center gap-4 rounded-2xl p-10 text-center ${className}`}
    >
      <motion.div
        animate={{ y: [0, -6, 0] }}
        transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
        className="grid h-16 w-16 place-items-center rounded-2xl bg-blue-50 ring-1 ring-blue-100"
      >
        <Icon className="h-7 w-7 text-blue-500" strokeWidth={1.7} />
      </motion.div>
      <div>
        <h3 className="text-base font-black text-slate-800">{title}</h3>
        {description && <p className="mx-auto mt-1.5 max-w-sm text-sm text-slate-400">{description}</p>}
      </div>
      {action && <div className="mt-2 flex justify-center">{action}</div>}
    </motion.div>
  );
}

export default EmptyState;
