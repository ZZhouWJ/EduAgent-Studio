interface SparklineProps {
  /** 数值数组，会归一化到 0-100 */
  data: number[];
  /** 颜色，默认蓝紫渐变 */
  color?: string;
  /** 高度（px） */
  height?: number;
  className?: string;
}

export function Sparkline({ data, color = "#165DFF", height = 36, className = "" }: SparklineProps) {
  if (!data || data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const W = 100;
  const H = 100;

  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * W;
    const y = H - ((v - min) / range) * H;
    return `${x},${y}`;
  });

  const areaPoints = [
    `0,${H}`,
    ...data.map((v, i) => {
      const x = (i / (data.length - 1)) * W;
      const y = H - ((v - min) / range) * H;
      return `${x},${y}`;
    }),
    `${W},${H}`,
  ];

  const gradientId = `spark-${Math.random().toString(36).slice(2, 7)}`;

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="none"
      className={className}
      style={{ height }}
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <polygon points={areaPoints.join(" ")} fill={`url(#${gradientId})`} />
      <polyline
        points={points.join(" ")}
        fill="none"
        stroke={color}
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
