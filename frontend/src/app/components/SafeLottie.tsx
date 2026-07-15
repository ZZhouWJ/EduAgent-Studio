import {
  BarChart3,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  LoaderCircle,
  Sparkles,
} from "lucide-react";

type VisualKey = "loading" | "empty" | "success" | "dashboard" | "teaching" | "studying";

interface SafeLottieProps {
  source: VisualKey;
  className?: string;
  loop?: boolean;
  autoplay?: boolean;
  speed?: number;
}

const VISUALS = {
  loading: { icon: LoaderCircle, tone: "text-blue-600", surface: "bg-blue-50", spin: true },
  empty: { icon: BookOpen, tone: "text-slate-500", surface: "bg-slate-100", spin: false },
  success: { icon: CheckCircle2, tone: "text-emerald-600", surface: "bg-emerald-50", spin: false },
  teaching: { icon: Sparkles, tone: "text-violet-600", surface: "bg-violet-50", spin: false },
  studying: { icon: BrainCircuit, tone: "text-cyan-700", surface: "bg-cyan-50", spin: false },
} as const;

export function SafeLottie({
  source,
  className = "h-32 w-32",
  loop = true,
  autoplay = true,
  speed = 1,
}: SafeLottieProps) {
  const duration = `${Math.max(1.4, 2.8 / Math.max(speed, 0.25))}s`;
  const animationStyle = autoplay
    ? { animationDuration: duration, animationIterationCount: loop ? "infinite" : "1" }
    : { animation: "none" };

  if (source === "dashboard") {
    return (
      <div className={`${className} flex items-center justify-center p-4`} aria-hidden="true">
        <div
          className="relative h-full w-full max-h-28 max-w-28 motion-safe:animate-pulse"
          style={animationStyle}
        >
          <div className="absolute inset-0 rounded-lg border border-slate-200 bg-white shadow-sm" />
          <div className="absolute left-3 top-3 flex h-8 w-8 items-center justify-center rounded-md bg-slate-900 text-white">
            <BarChart3 className="h-4 w-4" />
          </div>
          <div className="absolute bottom-4 left-4 right-4 flex h-12 items-end gap-2">
            {[45, 75, 58, 92].map((height, index) => (
              <span
                key={height}
                className={`flex-1 rounded-t-sm ${index === 3 ? "bg-emerald-500" : "bg-blue-500"}`}
                style={{ height: `${height}%` }}
              />
            ))}
          </div>
        </div>
      </div>
    );
  }

  const visual = VISUALS[source];
  const Icon = visual.icon;
  return (
    <div className={`${className} flex items-center justify-center`} aria-hidden="true">
      <div
        className={`flex h-16 w-16 items-center justify-center rounded-lg ${visual.surface} ${visual.tone} ${
          visual.spin ? "motion-safe:animate-spin" : "motion-safe:animate-pulse"
        }`}
        style={animationStyle}
      >
        <Icon className="h-8 w-8" strokeWidth={1.7} />
      </div>
    </div>
  );
}

export default SafeLottie;
