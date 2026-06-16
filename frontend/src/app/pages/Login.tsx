import React, { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { notify } from "@/lib/toast";
import { useAuthStore } from "@/stores/auth";
import {
  ArrowRight,
  BookOpenCheck,
  Bot,
  LockKeyhole,
  ShieldCheck,
  UserRound,
} from "lucide-react";

/* ─── Lottie 动画资源 URL ───────────────────────────────────── */
// 极简数据流 / 学习主题动画（dotLottie 格式，体积小、透明背景）
const LOTTIE_LEARNING =
  "https://lottie.host/4db68bbd-31f6-4cd8-84eb-189de081159a/IGmMCqhzpt.lottie";
// 备用：在线学习场景
const LOTTIE_ONLINE_STUDY =
  "https://assets5.lottiefiles.com/packages/lf20_gb5bmwlm.json";

const ROLE_ENTRIES = [
  {
    role: "管理员",
    desc: "全平台管理、用户/角色、模型/智能体配置、调用审计与成本",
    account: "admin / Pass@1234",
    icon: ShieldCheck,
  },
  {
    role: "教师体验",
    desc: "管理课程、生成资源、审核 AI 内容和查看教学分析",
    account: "teacher_li / Pass@1234",
    icon: BookOpenCheck,
  },
  {
    role: "学生体验",
    desc: "查看个性化学习路径、推荐资源和学习反馈",
    account: "student_zhang / Pass@1234",
    icon: Bot,
  },
];

async function loginAndGo(username: string, password: string) {
  try {
    const user = await useAuthStore.getState().login(username, password);
    const target = user.roles.includes("admin") ? "/admin"
      : user.roles.includes("teacher") ? "/teacher"
      : "/student";
    window.location.href = target;
  } catch (e) {
    notify.error("登录失败：" + String(e));
  }
}

/* Lottie 学习动画组件 */
function LearningAnimation() {
  return (
    <lottie-player
      autoplay
      loop
      mode="normal"
      src={LOTTIE_LEARNING}
      style={{
        width: "100%",
        height: "100%",
        maxWidth: "520px",
        maxHeight: "420px",
        opacity: 0.85,
        filter: "brightness(1.1)",
      }}
    />
  );
}

export function Login() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { login, loading } = useAuthStore();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const user = await login(username, password);
      notify.success(`欢迎回来，${user.real_name || user.username}`);
      const redirect = params.get('redirect');
      const home = user.roles?.includes('admin') ? '/admin'
        : user.roles?.includes('teacher') ? '/teacher'
        : '/student';
      navigate(redirect || home, { replace: true });
    } catch (err) {
      notify.error(err instanceof Error ? err.message : '登录失败');
    }
  };

  return (
    <div className="flex min-h-dvh w-full overflow-hidden bg-white text-slate-900">
      {/* ── Left panel ─────────────────────────────────── */}
      <section className="relative hidden w-[55%] min-w-[600px] flex-col overflow-hidden lg:flex">
        {/* 渐变动画背景 */}
        <div className="edu-login-bg" />

        {/* 微妙的网点纹理 */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)',
            backgroundSize: '24px 24px',
          }}
        />

        {/* Lottie 学习动画（透明背景、不干扰文字） */}
        <div className="relative z-10 flex flex-1 items-center justify-center px-10">
          <LearningAnimation />
        </div>

        {/* 底部标语 */}
        <div className="relative z-10 p-10">
          <p className="max-w-md text-sm leading-relaxed text-white/70">
            让每位学生都拥有专属的课程资源生成智能体。
          </p>
        </div>
      </section>

      {/* ── Right form panel ──────────────────────────── */}
      <section className="flex min-w-0 flex-1 items-center justify-center bg-white px-6 py-10">
        <div className="w-full max-w-[400px]">
          {/* 移动端品牌 */}
          <div className="mb-8 text-center lg:hidden">
            <div className="mx-auto mb-3 grid h-10 w-10 place-items-center rounded-lg bg-blue-600">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-lg font-semibold text-slate-900">
              智学工坊 EduAgent Studio
            </h1>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            {/* 表单头部 */}
            <div className="mb-6 text-center">
              <div className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-lg bg-blue-600">
                <BookOpenCheck className="h-6 w-6 text-white" />
              </div>
              <h2 className="text-lg font-semibold text-slate-900">欢迎登录</h2>
              <p className="mt-1 text-sm text-slate-500">
                开启个性化学习资源生成之旅
              </p>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              {/* 用户名 */}
              <div>
                <label htmlFor="username" className="mb-1.5 block text-sm font-medium text-slate-700">
                  用户名
                </label>
                <div className="relative">
                  <UserRound className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="edu-focus-ring h-10 w-full rounded-lg border border-slate-200 bg-white pl-9 pr-3 text-sm text-slate-900 placeholder:text-slate-400 transition duration-200 hover:border-slate-300 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/10"
                    autoComplete="username"
                    placeholder="请输入用户名"
                  />
                </div>
              </div>

              {/* 密码 */}
              <div>
                <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-slate-700">
                  密码
                </label>
                <div className="relative">
                  <LockKeyhole className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="edu-focus-ring h-10 w-full rounded-lg border border-slate-200 bg-white pl-9 pr-3 text-sm text-slate-900 placeholder:text-slate-400 transition duration-200 hover:border-slate-300 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/10"
                    autoComplete="current-password"
                    placeholder="请输入密码"
                  />
                </div>
              </div>

              {/* 记住我 / 忘记密码 */}
              <div className="flex items-center justify-between">
                <label className="flex cursor-pointer items-center gap-2">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                    defaultChecked
                  />
                  <span className="text-sm text-slate-600">记住我</span>
                </label>
                <a href="/login" className="text-sm font-medium text-blue-700 hover:text-blue-800">
                  忘记密码？
                </a>
              </div>

              {/* 登录按钮（带 shimmer hover 动效） */}
              <button
                type="submit"
                disabled={loading}
                aria-busy={loading}
                className="edu-btn-shimmer group flex h-10 w-full items-center justify-center gap-2 rounded-lg bg-blue-600 text-sm font-semibold text-white transition duration-200 hover:bg-blue-700 active:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
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
                    <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5" />
                  </>
                )}
              </button>
            </form>

            {/* 角色体验入口 */}
            <div className="mt-6 border-t border-slate-100 pt-5">
              <p className="mb-3 text-xs font-medium uppercase tracking-wide text-slate-400">
                角色体验入口
              </p>
              <div className="space-y-2">
                {ROLE_ENTRIES.map((entry) => {
                  const Icon = entry.icon;
                  const [acc, pwd] = entry.account.split(' / ');
                  return (
                    <button
                      key={entry.role}
                      type="button"
                      onClick={() => loginAndGo(acc, pwd)}
                      className="flex w-full items-center gap-3 rounded-lg border border-slate-100 bg-slate-50 p-2.5 text-left transition duration-200 hover:border-slate-200 hover:bg-white hover:shadow-sm"
                    >
                      <div className="grid h-8 w-8 shrink-0 place-items-center rounded-md bg-slate-100">
                        <Icon className="h-4 w-4 text-slate-600" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <span className="block text-sm font-medium text-slate-900">{entry.role}</span>
                        <span className="text-xs text-slate-500">{entry.desc}</span>
                      </div>
                      <span className="hidden text-xs text-slate-400 sm:inline">{entry.account}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
