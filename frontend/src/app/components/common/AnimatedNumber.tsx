import { useEffect, useRef } from "react";

interface AnimatedNumberProps {
  value: number;
  /** 显示的精度，小数位 */
  decimals?: number;
  /** 动画时长（毫秒） */
  duration?: number;
  className?: string;
  /** 格式化回调 */
  formatter?: (v: number) => string;
}

export function AnimatedNumber({
  value,
  decimals = 0,
  duration = 900,
  className = "",
  formatter,
}: AnimatedNumberProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const startRef = useRef<number | null>(null);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    startRef.current = null;

    const animate = (timestamp: number) => {
      if (startRef.current === null) startRef.current = timestamp;
      const elapsed = timestamp - startRef.current;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = value * eased;
      el.textContent = formatter ? formatter(current) : current.toFixed(decimals);
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate);
      } else {
        el.textContent = formatter ? formatter(value) : value.toFixed(decimals);
      }
    };

    rafRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafRef.current);
  }, [value, decimals, duration, formatter]);

  return (
    <span ref={ref} className={`edu-num inline-block ${className}`}>
      {formatter ? formatter(0) : value.toFixed(decimals)}
    </span>
  );
}

export default AnimatedNumber;
