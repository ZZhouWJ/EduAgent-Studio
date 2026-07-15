import React, { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { motion, type Variants } from "motion/react";
import confetti from "canvas-confetti";
import { notify } from "@/lib/toast";
import { useAuthStore } from "@/stores/auth";
import {
  ArrowRight,
  Atom,
  BookOpenCheck,
  Bot,
  Brain,
  CircuitBoard,
  Cpu,
  Database,
  GraduationCap,
  Languages,
  LockKeyhole,
  Network,
  Rocket,
  ShieldCheck,
  Sparkles,
  Telescope,
  UserRound,
  Wand2,
  Zap,
} from "lucide-react";

/* ─── 角色快捷登录入口 ───────────────────────────────────── */
const ROLE_ENTRIES = [
  {
    role: "管理员",
    desc: "全平台管理、用户/角色、模型/智能体配置、调用审计与成本",
    account: "admin",
    password: "Pass@1234",
    icon: ShieldCheck,
    accent: "from-indigo-500 via-violet-500 to-purple-500",
  },
  {
    role: "教师体验",
    desc: "管理课程、生成资源、审核 AI 内容和查看教学分析",
    account: "teacher_li",
    password: "Pass@1234",
    icon: BookOpenCheck,
    accent: "from-blue-500 via-cyan-500 to-teal-400",
  },
  {
    role: "学生体验",
    desc: "查看个性化学习路径、推荐资源和学习反馈",
    account: "student_zhang",
    password: "Pass@1234",
    icon: Bot,
    accent: "from-emerald-500 via-teal-400 to-cyan-500",
  },
];

/* ─── 满版左侧品牌：4 块面板 + 12 浮元素 + 8 上升粒子 ──── */
function FloatingIcons() {
  const items = [
    { Icon: Sparkles, x: "6%", y: "10%", size: 30, delay: 0, color: "text-amber-300/85", duration: 9 },
    { Icon: Zap, x: "86%", y: "12%", size: 34, delay: 0.5, color: "text-yellow-300/75", duration: 10 },
    { Icon: Bot, x: "10%", y: "80%", size: 40, delay: 1.0, color: "text-cyan-300/75", duration: 12 },
    { Icon: GraduationCap, x: "84%", y: "76%", size: 36, delay: 1.4, color: "text-blue-300/75", duration: 11 },
    { Icon: Atom, x: "44%", y: "6%", size: 28, delay: 1.8, color: "text-pink-300/70", duration: 13 },
    { Icon: Zap, x: "48%", y: "90%", size: 30, delay: 2.2, color: "text-violet-300/65", duration: 14 },
    { Icon: Cpu, x: "92%", y: "44%", size: 26, delay: 0.3, color: "text-sky-300/70", duration: 15 },
    { Icon: Network, x: "4%", y: "46%", size: 28, delay: 1.5, color: "text-fuchsia-300/65", duration: 16 },
    { Icon: CircuitBoard, x: "62%", y: "92%", size: 22, delay: 0.8, color: "text-emerald-300/60", duration: 12 },
    { Icon: Brain, x: "92%", y: "62%", size: 26, delay: 2.6, color: "text-rose-300/65", duration: 13 },
    { Icon: Database, x: "6%", y: "62%", size: 24, delay: 1.2, color: "text-indigo-300/65", duration: 14 },
    { Icon: Languages, x: "58%", y: "10%", size: 24, delay: 0.6, color: "text-teal-300/60", duration: 11 },
  ];
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {items.map((it, i) => {
        const Icon = it.Icon;
        return (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.4 }}
            animate={{
              opacity: [0, 0.95, 0.95, 0.5, 0.95],
              scale: [0.4, 1, 1, 0.92, 1],
              y: [0, -22, 0, 14, 0],
              x: [0, 10, 0, -10, 0],
              rotate: [0, 14, -10, 0],
            }}
            transition={{ duration: it.duration, repeat: Infinity, delay: it.delay, ease: "easeInOut" }}
            className={`absolute ${it.color} drop-shadow-[0_0_20px_rgba(255,255,255,0.4)]`}
            style={{ left: it.x, top: it.y }}
          >
            <Icon style={{ width: it.size, height: it.size }} />
          </motion.div>
        );
      })}
    </div>
  );
}

/* ─── 上升粒子（更多、更密） ───────────────────────────── */
function RisingParticles() {
  const items = Array.from({ length: 22 }).map((_, i) => ({
    left: `${3 + (i * 4.3) % 94}%`,
    size: 3 + ((i * 11) % 8),
    delay: i * 0.45,
    duration: 9 + (i % 6) * 1.2,
    hue: ["#FCD34D", "#67E8F9", "#C4B5FD", "#F9A8D4", "#86EFAC", "#FCA5A5"][i % 6],
  }));
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {items.map((p, i) => (
        <motion.span
          key={i}
          className="absolute bottom-[-12px] rounded-full"
          style={{
            left: p.left,
            width: p.size,
            height: p.size,
            background: p.hue,
            boxShadow: `0 0 ${p.size * 2.2}px ${p.hue}`,
          }}
          animate={{ y: [-20, -900], opacity: [0, 0.85, 0] }}
          transition={{ duration: p.duration, repeat: Infinity, delay: p.delay, ease: "easeOut" }}
        />
      ))}
    </div>
  );
}

/* ─── 中心品牌视觉（多圈层、多浮点） ─────────────────── */
function HeroVisual() {
  return (
    <div className="relative flex h-full w-full flex-col items-center justify-center px-12">
      <motion.div
        className="absolute h-[560px] w-[560px] rounded-full"
        style={{ background: "radial-gradient(circle, rgba(139,92,246,0.6) 0%, rgba(59,130,246,0.22) 35%, transparent 70%)" }}
        animate={{ scale: [1, 1.18, 1], opacity: [0.7, 1, 0.7] }}
        transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute h-[380px] w-[380px] rounded-full"
        style={{ background: "radial-gradient(circle, rgba(6,182,212,0.5) 0%, transparent 65%)" }}
        animate={{ scale: [1, 1.25, 1], opacity: [0.5, 0.95, 0.5] }}
        transition={{ duration: 3.6, repeat: Infinity, ease: "easeInOut", delay: 0.6 }}
      />
      <motion.div
        className="absolute h-[260px] w-[260px] rounded-full"
        style={{ background: "radial-gradient(circle, rgba(236,72,153,0.42) 0%, transparent 65%)" }}
        animate={{ scale: [1, 1.3, 1], opacity: [0.4, 0.85, 0.4] }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1.2 }}
      />
      <motion.div
        className="absolute h-[180px] w-[180px] rounded-full"
        style={{ background: "radial-gradient(circle, rgba(34,197,94,0.4) 0%, transparent 65%)" }}
        animate={{ scale: [1, 1.4, 1], opacity: [0.3, 0.8, 0.3] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: 2 }}
      />

      <motion.div
        className="absolute h-[360px] w-[360px] rounded-full border border-white/15"
        animate={{ rotate: 360 }}
        transition={{ duration: 22, repeat: Infinity, ease: "linear" }}
      />
      <motion.div
        className="absolute h-[280px] w-[280px] rounded-full border-2 border-dashed border-white/35"
        animate={{ rotate: -360 }}
        transition={{ duration: 16, repeat: Infinity, ease: "linear" }}
      />
      <motion.div
        className="absolute h-[200px] w-[200px] rounded-full border border-white/15"
        animate={{ rotate: 360 }}
        transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
      />

      <motion.div
        className="absolute"
        animate={{ rotate: 360 }}
        transition={{ duration: 22, repeat: Infinity, ease: "linear" }}
      >
        <div className="relative h-[360px] w-[360px]">
          {[
            { color: "bg-amber-400", Icon: Sparkles, angle: 0 },
            { color: "bg-pink-400", Icon: Wand2, angle: 45 },
            { color: "bg-cyan-400", Icon: Database, angle: 90 },
            { color: "bg-emerald-400", Icon: Languages, angle: 135 },
            { color: "bg-violet-400", Icon: Brain, angle: 180 },
            { color: "bg-blue-400", Icon: Telescope, angle: 225 },
            { color: "bg-rose-400", Icon: Rocket, angle: 270 },
            { color: "bg-fuchsia-400", Icon: Atom, angle: 315 },
          ].map((it, i) => {
            const rad = (it.angle * Math.PI) / 180;
            const x = Math.cos(rad) * 180 + 180 - 16;
            const y = Math.sin(rad) * 180 + 180 - 16;
            const Icon = it.Icon;
            return (
              <motion.div
                key={i}
                className={`absolute grid h-8 w-8 place-items-center rounded-full ${it.color} shadow-[0_0_24px_rgba(255,255,255,0.6)]`}
                style={{ left: x, top: y }}
                animate={{ rotate: -360, scale: [1, 1.18, 1] }}
                transition={{
                  rotate: { duration: 22, repeat: Infinity, ease: "linear" },
                  scale: { duration: 2.4, repeat: Infinity, ease: "easeInOut", delay: i * 0.25 },
                }}
              >
                <Icon className="h-4 w-4 text-white" />
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      <motion.div
        initial={{ scale: 0, rotate: -45 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 110, damping: 12, delay: 0.2 }}
        className="relative z-10 grid h-36 w-36 place-items-center rounded-[28px] bg-gradient-to-br from-indigo-500 via-blue-500 to-cyan-400 shadow-[0_20px_60px_rgba(59,130,246,0.55)]"
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0 rounded-[28px] border-2 border-dashed border-white/40"
        />
        <motion.div
          animate={{ scale: [1, 1.2, 1], opacity: [0.4, 0.7, 0.4] }}
          transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
          className="absolute inset-0 rounded-[28px] bg-white/15 blur-md"
        />
        <Bot className="h-16 w-16 text-white drop-shadow-[0_0_18px_rgba(255,255,255,0.55)]" strokeWidth={1.6} />
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.7 }}
        className="relative z-10 mt-8 text-center"
      >
        <h1 className="bg-gradient-to-r from-white via-blue-100 to-cyan-200 bg-clip-text text-4xl font-black tracking-tight text-transparent sm:text-5xl">
          智学工坊
        </h1>
        <p className="mt-2 text-sm font-semibold uppercase tracking-[0.36em] text-white/70">
          EduAgent Studio
        </p>
      </motion.div>
    </div>
  );
}

/* ─── 庆祝粒子（登录成功） ─────────────────────────────── */
function fireConfetti() {
  const colors = ["#2563EB", "#7C3AED", "#10B981", "#F59E0B", "#06B6D4", "#EC4899"];
  const defaults = { spread: 70, startVelocity: 50, ticks: 100, zIndex: 9999 };
  confetti({ ...defaults, particleCount: 90, origin: { x: 0.3, y: 0.7 }, colors });
  confetti({ ...defaults, particleCount: 90, origin: { x: 0.7, y: 0.7 }, colors });
  confetti({ ...defaults, particleCount: 70, origin: { x: 0.5, y: 0.5 }, colors, shapes: ["circle"] });
}

export function Login() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { login, loading } = useAuthStore();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [focused, setFocused] = useState<"user" | "pass" | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const user = await login(username, password);
      notify.success(`欢迎回来，${user.real_name || user.username}`);
      fireConfetti();
      const redirect = params.get("redirect");
      const home = user.roles?.includes("admin")
        ? "/admin"
        : user.roles?.includes("teacher")
        ? "/teacher"
        : (user.roles?.includes("student_member") ? "/student" : "/student");
      setTimeout(() => navigate(redirect || home, { replace: true }), 450);
    } catch (err) {
      notify.error(err instanceof Error ? err.message : "登录失败");
    }
  };

  const quickLogin = async (acc: string, pwd: string) => {
    setUsername(acc);
    setPassword(pwd);
    try {
      const user = await login(acc, pwd);
      notify.success(`欢迎回来，${user.real_name || user.username}`);
      fireConfetti();
      const home = user.roles?.includes("admin")
        ? "/admin"
        : user.roles?.includes("teacher")
        ? "/teacher"
        : (user.roles?.includes("student_member") ? "/student" : "/student");
      setTimeout(() => navigate(home, { replace: true }), 450);
    } catch (err) {
      notify.error(err instanceof Error ? err.message : "登录失败");
    }
  };

  const leftFade: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: { delay: 0.4 + i * 0.1, duration: 0.5, ease: [0.22, 1, 0.36, 1] as const },
    }),
  };

  return (
    <div className="relative flex min-h-dvh w-full overflow-hidden bg-slate-50 text-slate-900">
      {/* ════════════════ 左侧品牌区（更饱满） ════════════════ */}
      <section className="relative hidden w-[60%] min-w-[640px] flex-col overflow-hidden lg:flex">
        <motion.div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(120deg, #0F172A 0%, #1E1B4B 25%, #312E81 50%, #4C1D95 75%, #0F172A 100%)",
            backgroundSize: "300% 300%",
          }}
          animate={{ backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
        />

        <motion.div
          className="absolute -left-32 -top-32 h-[600px] w-[600px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(139,92,246,0.55) 0%, transparent 70%)" }}
          animate={{ scale: [1, 1.3, 1], x: [0, 40, 0], y: [0, 24, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute -bottom-40 -right-32 h-[680px] w-[680px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(6,182,212,0.5) 0%, transparent 70%)" }}
          animate={{ scale: [1, 1.22, 1], x: [0, -28, 0], y: [0, -36, 0] }}
          transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute left-1/3 top-1/4 h-[320px] w-[320px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(236,72,153,0.32) 0%, transparent 70%)" }}
          animate={{ scale: [1, 1.4, 1], opacity: [0.6, 1, 0.6] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute right-1/4 top-2/3 h-[260px] w-[260px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(34,197,94,0.3) 0%, transparent 70%)" }}
          animate={{ scale: [1, 1.3, 1], opacity: [0.5, 0.9, 0.5] }}
          transition={{ duration: 11, repeat: Infinity, ease: "easeInOut", delay: 1.5 }}
        />

        <motion.div
          className="absolute inset-0 opacity-[0.08]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.6) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.6) 1px, transparent 1px)",
            backgroundSize: "32px 32px",
          }}
          animate={{ backgroundPosition: ["0px 0px", "32px 32px"] }}
          transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
        />

        <FloatingIcons />
        <RisingParticles />

        <div className="relative z-10 flex flex-1 items-center justify-center">
          <HeroVisual />
        </div>

        <motion.div
          initial="hidden"
          animate="visible"
          className="relative z-10 px-12 pb-10"
        >
          <motion.h2
            custom={0}
            variants={leftFade}
            className="bg-gradient-to-r from-white via-blue-50 to-cyan-100 bg-clip-text text-[34px] font-black leading-[1.2] tracking-tight text-transparent sm:text-[42px]"
          >
            每一次学习
            <br />
            都更接近答案
          </motion.h2>

          <motion.p
            custom={1}
            variants={leftFade}
            className="mt-4 max-w-[520px] text-[15px] leading-relaxed text-white/80"
          >
            智学工坊融合大模型与多智能体协同，让每位学生拥有专属学习路径，
            让每位教师拥有 AI 教学助理，让知识在被需要的时刻精准抵达。
          </motion.p>

          <motion.div
            custom={2}
            variants={leftFade}
            className="mt-6 grid max-w-[560px] grid-cols-4 gap-3"
          >
            {[
              { num: "5+", label: "教学智能体", color: "from-violet-400 to-fuchsia-400" },
              { num: "10x", label: "备课提速", color: "from-cyan-400 to-blue-400" },
              { num: "30+", label: "知识图谱节点", color: "from-emerald-400 to-teal-400" },
              { num: "24h", label: "全天候辅导", color: "from-amber-400 to-orange-400" },
            ].map((m, i) => (
              <motion.div
                key={m.label}
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 + i * 0.08, duration: 0.45 }}
                whileHover={{ y: -3, borderColor: "rgba(255,255,255,0.4)" }}
                className="group cursor-default rounded-xl border border-white/12 bg-white/5 p-3 backdrop-blur-md transition-colors hover:bg-white/10"
              >
                <div className={`bg-gradient-to-r ${m.color} bg-clip-text text-2xl font-black text-transparent`}>
                  {m.num}
                </div>
                <div className="mt-0.5 text-[11px] font-medium text-white/65">{m.label}</div>
              </motion.div>
            ))}
          </motion.div>

          <motion.div
            custom={3}
            variants={leftFade}
            className="mt-6 flex flex-wrap items-center gap-2 text-xs font-semibold text-white/75"
          >
            {["个性化学习路径", "AI 资源生成", "多智能体协同", "教师审核", "知识图谱", "学情诊断", "智能评估"].map((t, i) => (
              <motion.span
                key={t}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.0 + i * 0.06, duration: 0.4 }}
                whileHover={{ y: -2, scale: 1.04 }}
                className="cursor-default rounded-full border border-white/15 bg-white/5 px-3 py-1 backdrop-blur-sm transition-colors hover:border-white/40 hover:bg-white/10"
              >
                {t}
              </motion.span>
            ))}
          </motion.div>
        </motion.div>
      </section>

      {/* ════════════════ 右侧登录卡片 ════════════════ */}
      <section className="relative flex min-w-0 flex-1 items-center justify-center bg-gradient-to-br from-white via-slate-50 to-blue-50/40 px-6 py-10">
        <div className="w-full max-w-[400px]">
          <div className="mb-6 text-center lg:hidden">
            <div className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 shadow-lg shadow-blue-500/30">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-lg font-semibold text-slate-900">智学工坊</h1>
          </div>

          <div className="rounded-2xl border border-slate-200/80 bg-white/90 p-7 shadow-xl shadow-slate-200/60 backdrop-blur-xl sm:p-9">
            <div className="mb-6">
              <div className="mb-3 flex items-center gap-3">
                <div className="grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 shadow-lg shadow-blue-500/30">
                  <BookOpenCheck className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-lg font-black text-slate-900">欢迎登录</h2>
                  <p className="text-xs text-slate-500">开启个性化学习资源生成之旅</p>
                </div>
              </div>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label htmlFor="username" className="mb-1.5 block text-xs font-semibold text-slate-600">
                  用户名
                </label>
                <div
                  className={`relative rounded-lg border bg-white transition-colors ${
                    focused === "user" ? "border-blue-500 ring-2 ring-blue-500/10" : "border-slate-200"
                  }`}
                >
                  <UserRound
                    className={`pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 ${
                      focused === "user" ? "text-blue-500" : "text-slate-400"
                    }`}
                  />
                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    onFocus={() => setFocused("user")}
                    onBlur={() => setFocused(null)}
                    className="h-10 w-full rounded-lg bg-transparent pl-9 pr-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none"
                    autoComplete="username"
                    placeholder="请输入用户名"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="mb-1.5 block text-xs font-semibold text-slate-600">
                  密码
                </label>
                <div
                  className={`relative rounded-lg border bg-white transition-colors ${
                    focused === "pass" ? "border-blue-500 ring-2 ring-blue-500/10" : "border-slate-200"
                  }`}
                >
                  <LockKeyhole
                    className={`pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 ${
                      focused === "pass" ? "text-blue-500" : "text-slate-400"
                    }`}
                  />
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onFocus={() => setFocused("pass")}
                    onBlur={() => setFocused(null)}
                    className="h-10 w-full rounded-lg bg-transparent pl-9 pr-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none"
                    autoComplete="current-password"
                    placeholder="请输入密码"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <label className="flex cursor-pointer items-center gap-2">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                    defaultChecked
                  />
                  <span className="text-xs text-slate-600">记住我</span>
                </label>
                <a
                  href="/login"
                  className="text-xs font-medium text-blue-600 transition-colors hover:text-blue-700"
                >
                  忘记密码？
                </a>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-sm font-semibold text-white shadow-lg shadow-blue-500/30 transition-opacity hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a10 10 0 00-10 10h2z" />
                    </svg>
                    登录中...
                  </>
                ) : (
                  <>
                    登录系统
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 border-t border-slate-100 pt-5">
              <p className="mb-3 flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                <Sparkles className="h-3 w-3" />
                角色体验入口
              </p>
              <div className="space-y-2">
                {ROLE_ENTRIES.map((entry) => {
                  const Icon = entry.icon;
                  return (
                    <button
                      key={entry.role}
                      type="button"
                      onClick={() => quickLogin(entry.account, entry.password)}
                      className="group flex w-full items-center gap-3 rounded-lg border border-slate-100 bg-gradient-to-r from-slate-50 to-white p-2.5 text-left transition-colors hover:border-blue-200 hover:bg-blue-50/40"
                    >
                      <div
                        className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-gradient-to-br ${entry.accent} text-white shadow-sm`}
                      >
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <span className="block text-sm font-bold text-slate-900">{entry.role}</span>
                        <span className="block text-[11px] leading-snug text-slate-500">{entry.desc}</span>
                      </div>
                      <ArrowRight className="h-4 w-4 shrink-0 text-slate-300 transition-colors group-hover:text-blue-500" />
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <p className="mt-6 text-center text-[11px] text-slate-400">
            © 2026 智学工坊 · 基于大模型的个性化学习多智能体系统
          </p>
        </div>
      </section>
    </div>
  );
}

export default Login;
