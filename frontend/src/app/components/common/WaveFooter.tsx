import { motion } from "motion/react";

interface WaveFooterProps {
  className?: string;
}

const WAVE_LAYERS = [
  { color: "bg-blue-400/20", top: "top-0", dur: 6, dy: -14, opacity: 0.5 },
  { color: "bg-blue-500/15", top: "top-2", dur: 8, dy: 12, opacity: 0.4 },
  { color: "bg-purple-400/15", top: "top-4", dur: 10, dy: -10, opacity: 0.35 },
  { color: "bg-cyan-400/12", top: "top-6", dur: 7, dy: 16, opacity: 0.3 },
];

function WaveBlob({ color, top, dur, dy, opacity }: typeof WAVE_LAYERS[0]) {
  return (
    <motion.div
      className={`pointer-events-none absolute ${color} select-none`}
      style={{ top, left: 0, right: 0, height: 80, opacity }}
      animate={{ y: [0, dy, 0], x: [0, dy * 0.5, 0] }}
      transition={{ duration: dur, repeat: Infinity, ease: "easeInOut" }}
      aria-hidden
    />
  );
}

export function WaveFooter({ className = "" }: WaveFooterProps) {
  return (
    <div
      className={`pointer-events-none fixed bottom-0 left-0 right-0 select-none overflow-hidden ${className}`}
      style={{ height: 120, zIndex: 1 }}
      aria-hidden
    >
      {WAVE_LAYERS.map((layer, i) => (
        <WaveBlob key={i} {...layer} />
      ))}
      {/* Base gradient fade to background */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background: "linear-gradient(to top, rgba(246,248,252,0.9) 0%, transparent 100%)",
        }}
      />
    </div>
  );
}

export default WaveFooter;
