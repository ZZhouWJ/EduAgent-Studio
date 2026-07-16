import React from "react";
import { motion } from "motion/react";

type Variant = "primary" | "secondary" | "ghost";
type Size = "sm" | "md" | "lg";

interface GradientButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: Variant;
  size?: Size;
  className?: string;
  icon?: React.ReactNode;
  iconPosition?: "left" | "right";
  loading?: boolean;
}

const sizeClasses: Record<Size, string> = {
  sm: "h-9 px-4 text-xs rounded-xl",
  md: "h-11 px-5 text-sm rounded-xl",
  lg: "h-13 px-6 text-base rounded-2xl",
};

const variantClasses: Record<Variant, string> = {
  primary: "edu-accent-gradient text-white shadow-[0_12px_28px_rgba(22,93,255,0.25)] hover:shadow-[0_18px_38px_rgba(22,93,255,0.32)] hover:brightness-110",
  secondary: "bg-white border border-slate-200 text-slate-800 shadow-sm hover:border-blue-300 hover:text-blue-700 hover:shadow-md",
  ghost: "bg-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900",
};

export function GradientButton({
  children,
  onClick,
  disabled,
  variant = "primary",
  size = "md",
  className = "",
  icon,
  iconPosition = "left",
  loading,
}: GradientButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      disabled={disabled || loading}
      whileHover={disabled ? {} : { scale: 1.02, y: -1 }}
      whileTap={disabled ? {} : { scale: 0.98 }}
      transition={{ duration: 0.18 }}
      className={`
        inline-flex items-center justify-center gap-2 font-bold
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
        ${className}
      `}
    >
      {loading ? (
        <span className="flex h-4 w-4 items-center justify-center">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        </span>
      ) : (
        <>
          {icon && iconPosition === "left" && <span className="shrink-0">{icon}</span>}
          {children}
          {icon && iconPosition === "right" && <span className="shrink-0">{icon}</span>}
        </>
      )}
    </motion.button>
  );
}

export default GradientButton;
