import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { X, Send, ChevronDown } from "lucide-react";

interface FloatingHelperProps {
  /** "student" | "teacher" | "admin" */
  role?: string;
}

const roleConfig = {
  student: {
    color: "from-cyan-400 to-blue-500",
    glow: "shadow-blue-400/40",
    bg: "bg-blue-50",
    border: "border-blue-200",
    text: "text-blue-700",
    accent: "bg-blue-500",
    hint: "学习助手",
    emoji: false,
  },
  teacher: {
    color: "from-purple-400 to-blue-500",
    glow: "shadow-purple-400/40",
    bg: "bg-purple-50",
    border: "border-purple-200",
    text: "text-purple-700",
    accent: "bg-purple-500",
    hint: "教学助手",
    emoji: false,
  },
  admin: {
    color: "from-emerald-400 to-blue-500",
    glow: "shadow-emerald-400/40",
    bg: "bg-emerald-50",
    border: "border-emerald-200",
    text: "text-emerald-700",
    accent: "bg-emerald-500",
    hint: "管理助手",
    emoji: false,
  },
};

const QUICK_QUESTIONS = {
  student: [
    "帮我规划今日学习任务",
    "推荐适合我的资源",
    "分析我的薄弱知识点",
  ],
  teacher: [
    "生成班级薄弱点报告",
    "创建新的学习资源",
    "查看待审核资源",
  ],
  admin: [
    "查看系统运行状态",
    "检查 API 调用日志",
    "配置智能体参数",
  ],
};

function CharacterHead({ role }: { role: string }) {
  const cfg = roleConfig[role as keyof typeof roleConfig] ?? roleConfig.student;
  return (
    <div className="relative flex flex-col items-center">
      {/* Antenna */}
      <motion.div
        className="h-3 w-1 bg-white/80"
        animate={{ y: [-1, -3, -1], rotate: [-3, 3, -3] }}
        transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
        style={{ borderRadius: 2 }}
      >
        <motion.div
          className={`h-2.5 w-2.5 -mt-0.5 rounded-full ${cfg.accent}`}
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
        />
      </motion.div>

      {/* Head */}
      <div
        className={`relative flex h-14 w-14 flex-col items-center justify-center border-2 border-white/30 bg-gradient-to-br ${cfg.color} shadow-lg`}
        style={{ borderRadius: "28% 28% 40% 40%" }}
      >
        {/* Eyes */}
        <div className="mt-1 flex gap-3">
          <Eye />
          <Eye />
        </div>
        {/* Mouth — smile curve */}
        <motion.div
          className="mt-1.5 h-1.5 w-5 rounded-b-full border-b-2 border-white/70"
          animate={{ scaleX: [1, 0.85, 1] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      {/* Body */}
      <div
        className={`relative -mt-1 flex h-10 w-12 flex-col items-center bg-gradient-to-b ${cfg.color} shadow-md`}
        style={{ borderRadius: "30% 30% 20% 20%" }}
      >
        {/* Screen face on body */}
        <div className="mt-2 flex gap-2">
          <div className="h-2 w-2 rounded-full bg-white/50" />
          <div className="h-2 w-2 rounded-full bg-white/50" />
        </div>
        {/* Arms */}
        <motion.div
          className="absolute -left-3 top-2 h-2 w-3 rounded-full bg-white/40"
          animate={{ rotate: [-15, 5, -15] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute -right-3 top-2 h-2 w-3 rounded-full bg-white/40"
          animate={{ rotate: [15, -5, 15] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>
    </div>
  );
}

function Eye() {
  return (
    <motion.div
      className="relative h-3.5 w-3.5 rounded-full bg-white"
      animate={{ height: ["14px", "3px", "14px"] }}
      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", repeatDelay: Math.random() * 3 + 1 }}
    >
      <motion.div
        className="absolute left-1/2 top-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-slate-800"
        animate={{ x: [0, 1, 0, -1, 0], y: [0, -1, 0, 1, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
      />
    </motion.div>
  );
}

function ChatBubble({ role }: { role: string }) {
  const cfg = roleConfig[role as keyof typeof roleConfig] ?? roleConfig.student;
  const questions = QUICK_QUESTIONS[role as keyof typeof QUICK_QUESTIONS] ?? QUICK_QUESTIONS.student;
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 10 }}
      transition={{ duration: 0.25 }}
      className={`absolute bottom-20 right-0 w-64 ${cfg.bg} border ${cfg.border} p-4 shadow-xl`}
      style={{ borderRadius: 0 }}
    >
      <div className={`mb-3 flex items-center gap-2 border-b ${cfg.border} pb-2`}>
        <div className={`h-2 w-2 rounded-full ${cfg.accent} animate-pulse`} />
        <span className={`text-xs font-bold ${cfg.text}`}>{cfg.hint}</span>
      </div>
      <p className="mb-3 text-xs text-slate-600">有什么可以帮你的？试试这些快捷操作：</p>
      <div className="flex flex-col gap-2">
        {questions.map((q) => (
          <button
            key={q}
            onClick={() => setSelected(q)}
            className={`w-full border ${cfg.border} ${cfg.bg} px-3 py-2 text-left text-xs transition-colors hover:${cfg.accent} hover:text-white ${selected === q ? (cfg.accent + " text-white") : cfg.text}`}
            style={{ borderRadius: 0 }}
          >
            <div className="flex items-center gap-2">
              <Send className="h-3 w-3 shrink-0" />
              {q}
            </div>
          </button>
        ))}
      </div>
      <div className="mt-3 flex items-center justify-between">
        <span className="text-[10px] text-slate-400">Powered by EduAgent</span>
        <ChevronDown className="h-3 w-3 text-slate-400" />
      </div>
    </motion.div>
  );
}

export function FloatingHelper({ role = "student" }: FloatingHelperProps) {
  const [isOpen, setIsOpen] = useState(false);
  const cfg = roleConfig[role as keyof typeof roleConfig] ?? roleConfig.student;

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <AnimatePresence>
        {isOpen && <ChatBubble role={role} key="chat" />}
      </AnimatePresence>

      {/* Floating character */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className={`group relative flex h-20 w-20 cursor-pointer flex-col items-center justify-center border-0 shadow-xl transition-shadow hover:shadow-2xl ${cfg.glow}`}
        style={{ background: "transparent" }}
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
        whileTap={{ scale: 0.92 }}
        aria-label={isOpen ? "关闭助手" : `打开${cfg.hint}`}
      >
        {/* Outer glow ring */}
        <motion.div
          className="absolute inset-0"
          animate={{ scale: [1, 1.15, 1], opacity: [0.4, 0.1, 0.4] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
          style={{
            borderRadius: 0,
            background: `linear-gradient(135deg, rgba(255,255,255,0.15), transparent)`,
            border: `2px solid ${cfg.accent}33`,
          }}
        />

        {/* Character */}
        <CharacterHead role={role} />

        {/* Notification dot */}
        {!isOpen && (
          <motion.div
            className={`absolute -right-1 -top-1 h-4 w-4 rounded-full ${cfg.accent}`}
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}

        {/* Close icon overlay */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0 }}
              className={`absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center ${cfg.bg} border ${cfg.border} ${cfg.text} shadow`}
              style={{ borderRadius: 0 }}
            >
              <X className="h-3.5 w-3.5" />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Label below */}
      <motion.div
        className={`mt-2 text-center text-[10px] font-semibold ${cfg.text} opacity-70`}
        animate={{ opacity: [0.5, 0.9, 0.5] }}
        transition={{ duration: 3, repeat: Infinity }}
      >
        {isOpen ? "点击外部关闭" : cfg.hint}
      </motion.div>
    </div>
  );
}

export default FloatingHelper;
