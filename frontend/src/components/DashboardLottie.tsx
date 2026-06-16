import { useRef } from "react";
import { useLottieAnimation } from "@/hooks/useLottieAnimation";

const ANIMATIONS: Record<string, string> = {
  admin: "/src/animations/admin.json",
  teacher: "/src/animations/teacher.json",
  student: "/src/animations/student.json",
};

export function DashboardLottie({
  variant,
  className,
}: {
  variant: "admin" | "teacher" | "student";
  className?: string;
}) {
  const { containerRef, error, reduceMotion } = useLottieAnimation({
    src: ANIMATIONS[variant],
    loop: true,
  });

  // 降级：reduce-motion 或加载失败时，显示一个静态占位（不破图）
  if (reduceMotion || error) {
    return (
      <div
        className={`flex items-center justify-center ${className ?? ""}`}
        aria-hidden="true"
      >
        <StaticMark variant={variant} />
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ background: "transparent" }}
      aria-hidden="true"
    />
  );
}

/* ─── 静态降级占位（极简 SVG，无任何动画） ───────────────── */
function StaticMark({ variant }: { variant: string }) {
  const fill = variant === "admin" ? "#0F172A" : variant === "teacher" ? "#7C3AED" : "#2563EB";
  return (
    <svg viewBox="0 0 360 280" className="w-full" aria-hidden="true">
      <rect x="30" y="30" width="300" height="220" rx="12" fill="white" stroke="#CBD5E1" strokeWidth="1" />
      <rect x="50" y="60" width="90" height="110" rx="8" fill={fill} opacity="0.08" />
      <rect x="160" y="60" width="90" height="110" rx="8" fill={fill} opacity="0.06" />
      <rect x="50" y="190" width="110" height="6" rx="3" fill="#CBD5E1" />
      <rect x="50" y="205" width="80" height="6" rx="3" fill="#E2E8F0" />
      <circle cx="300" cy="50" r="10" fill={fill} opacity="0.15" />
    </svg>
  );
}
