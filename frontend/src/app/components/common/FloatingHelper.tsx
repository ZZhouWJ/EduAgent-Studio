import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import ReactMarkdown from "react-markdown";
import { Bot, X, Send, Loader2, Zap, Sparkles } from "lucide-react";
import { useAuthStore } from "@/stores/auth";
import { tutorApi } from "@/lib/api/tutor";
import { profilesApi } from "@/lib/api/profiles";
import type { Citation } from "@/lib/api/tutor";

/* ─── 角色配置 ─────────────────────────────────────── */
const ROLE_CONFIG = {
  student: {
    color: "from-cyan-400 to-blue-600",
    accent: "bg-cyan-500",
    glow: "shadow-cyan-400/30",
    border: "border-cyan-200",
    bg: "bg-cyan-50",
    text: "text-cyan-700",
    hint: "学习助手",
    name: "AI 学习助手",
    desc: "随时为你答疑解惑",
  },
  teacher: {
    color: "from-purple-400 to-blue-600",
    accent: "bg-purple-500",
    glow: "shadow-purple-400/30",
    border: "border-purple-200",
    bg: "bg-purple-50",
    text: "text-purple-700",
    hint: "教学助手",
    name: "AI 教学助手",
    desc: "辅助教学工作",
  },
  admin: {
    color: "from-emerald-400 to-blue-600",
    accent: "bg-emerald-500",
    glow: "shadow-emerald-400/30",
    border: "border-emerald-200",
    bg: "bg-emerald-50",
    text: "text-emerald-700",
    hint: "管理助手",
    name: "AI 管理助手",
    desc: "系统管理支持",
  },
};

type Role = keyof typeof ROLE_CONFIG;

/* ─── 消息类型 ─────────────────────────────────────── */
type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
};

/* ─── 建议问题 ─────────────────────────────────────── */
const SUGGESTIONS: Record<Role, string[]> = {
  student: [
    "帮我规划今日学习任务",
    "推荐适合我的资源",
    "分析我的薄弱知识点",
    "什么是事务隔离级别？",
  ],
  teacher: [
    "生成班级薄弱点报告",
    "帮我写一个教学设计",
    "分析学生学习数据",
    "推荐生成哪些资源？",
  ],
  admin: [
    "系统运行状态如何？",
    "最近有哪些异常调用？",
    "帮我优化智能体配置",
    "生成成本分析报告",
  ],
};

/* ─── 头部装饰 ─────────────────────────────────────── */
function CharacterHead({ role }: { role: Role }) {
  const cfg = ROLE_CONFIG[role];
  return (
    <div className="relative flex flex-col items-center">
      <motion.div
        className="h-3 w-1 bg-white/70"
        animate={{ y: [-1.5, -4, -1.5], rotate: [-4, 4, -4] }}
        transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
      >
        <motion.div
          className={`-mt-1 h-3 w-3 rounded-full ${cfg.accent}`}
          animate={{ scale: [1, 1.3, 1] }}
          transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
        />
      </motion.div>
      <div
        className={`relative flex h-16 w-16 flex-col items-center justify-center border-2 border-white/25 bg-gradient-to-br ${cfg.color} shadow-lg`}
        style={{ borderRadius: "28% 28% 38% 38%" }}
      >
        <div className="mt-2 flex gap-4">
          {[0, 1].map((i) => (
            <motion.div
              key={i}
              className="relative h-4 w-4 rounded-full bg-white"
              animate={{ height: ["16px", "3px", "16px"] }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: "easeInOut",
                repeatDelay: i * 0.8 + Math.random() * 2,
              }}
            >
              <motion.div
                className="absolute left-1/2 top-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-slate-800"
                animate={{ x: [0, 1.5, 0, -1.5, 0], y: [0, -1, 0, 1, 0] }}
                transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
              />
            </motion.div>
          ))}
        </div>
        <motion.div
          className="mt-2 h-2 w-6 rounded-b-full border-b-2 border-white/60"
          animate={{ scaleX: [1, 0.8, 1] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>
      <div
        className={`relative -mt-1 flex h-12 w-14 flex-col items-center bg-gradient-to-b ${cfg.color} shadow-md`}
        style={{ borderRadius: "30% 30% 18% 18%" }}
      >
        <div className="mt-2 flex gap-3">
          <div className="h-2.5 w-2.5 rounded-full bg-white/40" />
          <div className="h-2.5 w-2.5 rounded-full bg-white/40" />
        </div>
        <motion.div
          className="absolute -left-4 top-3 h-2 w-3.5 rounded-full bg-white/30"
          animate={{ rotate: [-12, 8, -12] }}
          transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute -right-4 top-3 h-2 w-3.5 rounded-full bg-white/30"
          animate={{ rotate: [12, -8, 12] }}
          transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>
    </div>
  );
}

/* ─── 气泡消息 ─────────────────────────────────────── */
function MessageBubble({ msg }: { msg: Message; last: boolean }) {
  const isUser = msg.role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.22 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-[85%] px-3.5 py-2.5 ${
          isUser
            ? "bg-blue-600 text-white"
            : "border border-slate-100 bg-slate-50 text-slate-700"
        }`}
        style={{ borderRadius: 0 }}
      >
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown>{msg.content}</ReactMarkdown>
        </div>
        {msg.citations && msg.citations.length > 0 && (
          <div className="mt-2 border-t border-slate-200/50 pt-2">
            <div className="text-[10px] font-bold text-slate-400 mb-1">引用来源</div>
            {msg.citations.slice(0, 2).map((c, i) => (
              <div key={i} className="text-[10px] text-slate-500 truncate">{c.source}: {c.content}</div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

/* ─── 主组件 ─────────────────────────────────────── */
export function FloatingHelper({ role: propRole }: { role?: Role }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [profileId, setProfileId] = useState<number>(1);
  const [courseId, setCourseId] = useState<number>(1);
  const abortRef = useRef<(() => void) | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const user = useAuthStore((s) => s.user);

  const role: Role = propRole ?? (user?.roles?.includes("admin") ? "admin" : user?.roles?.includes("teacher") ? "teacher" : "student");
  const cfg = ROLE_CONFIG[role];

  // 加载学生画像
  useEffect(() => {
    profilesApi.getMyProfile().then((p: any) => {
      if (p?.profile_id) setProfileId(p.profile_id);
      if (p?.course_id) setCourseId(p.course_id);
    }).catch(() => {});
  }, []);

  // 自动滚动
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentAnswer]);

  const handleSend = useCallback(
    async (text?: string) => {
      const question = text ?? input.trim();
      if (!question || isGenerating) return;

      setInput("");
      const userMsg: Message = { id: `u_${Date.now()}`, role: "user", content: question };
      setMessages((prev) => [...prev, userMsg]);
      setCurrentAnswer("");
      setIsGenerating(true);

      let assistantId = `a_${Date.now()}`;
      setMessages((prev) => [
        ...prev,
        { id: assistantId, role: "assistant", content: "" },
      ]);

      const cancel = tutorApi.chatStream(
        { profile_id: profileId, course_id: courseId, question },
        {
          onEvent: () => {},
          onFinal: (answer, _, citations) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, content: answer, citations } : m
              )
            );
            setIsGenerating(false);
            setCurrentAnswer("");
          },
          onError: (err) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: `出错了：${err}，请稍后重试。` }
                  : m
              )
            );
            setIsGenerating(false);
          },
        }
      );
      abortRef.current = cancel;
    },
    [input, isGenerating, profileId, courseId]
  );

  const handleClose = () => {
    abortRef.current?.();
    setIsOpen(false);
  };

  const handleSuggestion = (s: string) => {
    handleSend(s);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chat panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
            className={`absolute bottom-24 right-0 w-80 border-2 ${cfg.border} ${cfg.bg} shadow-2xl flex flex-col`}
            style={{ borderRadius: 0, maxHeight: "520px" }}
          >
            {/* Header */}
            <div className={`flex items-center gap-3 border-b ${cfg.border} ${cfg.accent} px-4 py-3`}>
              <CharacterHead role={role} />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-bold text-white">{cfg.name}</div>
                <div className="text-[11px] text-white/70">{cfg.desc}</div>
              </div>
              <button
                onClick={handleClose}
                className="flex h-7 w-7 items-center justify-center rounded-none bg-white/20 text-white hover:bg-white/30 transition"
                aria-label="关闭"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
              {messages.length === 0 && !isGenerating && (
                <div className="text-center py-6">
                  <Sparkles className={`mx-auto h-8 w-8 ${cfg.text} opacity-30 mb-2`} />
                  <p className="text-xs text-slate-400">问我任何问题</p>
                </div>
              )}
              {messages.map((msg, i) => (
                <MessageBubble key={msg.id} msg={msg} last={i === messages.length - 1} />
              ))}

              {/* Generating indicator */}
              {isGenerating && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center gap-2 text-slate-500"
                >
                  <Loader2 className="h-4 w-4 animate-spin text-blue-500 shrink-0" />
                  <span className="text-xs flex items-center gap-1">
                    <Bot className="h-3 w-3" />
                    正在思考
                    <span className="inline-flex gap-0.5 ml-1">
                      <span className="h-1 w-1 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="h-1 w-1 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="h-1 w-1 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "300ms" }} />
                    </span>
                  </span>
                </motion.div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Suggestions */}
            {messages.length === 0 && !isGenerating && (
              <div className="px-3 pb-2">
                <div className={`text-[10px] font-bold ${cfg.text} mb-2 uppercase tracking-wider`}>快捷问题</div>
                <div className="flex flex-col gap-1.5">
                  {SUGGESTIONS[role].slice(0, 3).map((s) => (
                    <button
                      key={s}
                      onClick={() => handleSuggestion(s)}
                      className={`w-full border ${cfg.border} ${cfg.bg} px-3 py-2 text-left text-xs font-medium ${cfg.text} transition hover:${cfg.accent} hover:text-white hover:border-transparent`}
                      style={{ borderRadius: 0 }}
                    >
                      <div className="flex items-center gap-2">
                        <Sparkles className="h-3 w-3 shrink-0 opacity-60" />
                        {s}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input */}
            <div className={`flex items-end gap-2 border-t ${cfg.border} p-3`}>
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="输入问题..."
                rows={1}
                className={`edu-focus-ring flex-1 resize-none border ${cfg.border} ${cfg.bg} px-3 py-2 text-xs text-slate-700 placeholder:text-slate-400`}
                style={{ borderRadius: 0, maxHeight: 80, overflowY: "auto" }}
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || isGenerating}
                className={`flex h-9 w-9 shrink-0 items-center justify-center text-white transition ${isGenerating || !input.trim() ? "bg-slate-300 cursor-not-allowed" : cfg.accent + " hover:opacity-90"}`}
                aria-label="发送"
              >
                <Send className="h-3.5 w-3.5" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className={`group relative flex h-20 w-20 cursor-pointer flex-col items-center justify-center border-0 shadow-2xl transition-shadow hover:shadow-3xl ${cfg.glow}`}
        style={{ background: "transparent" }}
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
        whileTap={{ scale: 0.92 }}
        aria-label={isOpen ? "关闭助手" : `打开${cfg.hint}`}
      >
        {/* Outer pulse ring */}
        <motion.div
          className="absolute inset-0"
          animate={{ scale: [1, 1.18, 1], opacity: [0.45, 0.08, 0.45] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
          style={{
            borderRadius: 0,
            border: `2px solid ${cfg.accent}55`,
            background: "transparent",
          }}
        />
        {/* Mid ring */}
        <motion.div
          className="absolute inset-1"
          animate={{ scale: [1, 1.1, 1], opacity: [0.25, 0, 0.25] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut", delay: 0.4 }}
          style={{ borderRadius: 0, border: `1px solid ${cfg.accent}40`, background: "transparent" }}
        />
        <CharacterHead role={role} />

        {/* Notification dot */}
        {!isOpen && (
          <motion.div
            className={`absolute -right-1 -top-1 h-5 w-5 rounded-full ${cfg.accent}`}
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <Zap className="h-3 w-3 m-1 text-white" />
          </motion.div>
        )}

        {/* Close X overlay */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0 }}
              className={`absolute -right-2 -top-2 flex h-7 w-7 items-center justify-center ${cfg.bg} border-2 ${cfg.border} ${cfg.text} shadow`}
              style={{ borderRadius: 0 }}
            >
              <X className="h-4 w-4" />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Label */}
      <motion.div
        className={`mt-2 text-center text-[10px] font-semibold ${cfg.text} opacity-60`}
        animate={{ opacity: [0.4, 0.8, 0.4] }}
        transition={{ duration: 3, repeat: Infinity }}
      >
        {isOpen ? "点击外部关闭" : cfg.hint}
      </motion.div>
    </div>
  );
}

export default FloatingHelper;
