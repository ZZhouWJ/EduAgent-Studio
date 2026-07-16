import { useState, type FormEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  ArrowRight,
  BookOpenCheck,
  Bot,
  Eye,
  EyeOff,
  GraduationCap,
  LoaderCircle,
  LockKeyhole,
  ShieldCheck,
  UserRound,
  UsersRound,
} from "lucide-react";

import { notify } from "@/lib/toast";
import { useAuthStore } from "@/stores/auth";

const ROLE_CAPABILITIES = [
  {
    icon: GraduationCap,
    title: "学生学习空间",
    detail: "个性化路径、任务与智能辅导",
  },
  {
    icon: UsersRound,
    title: "教师教学工作台",
    detail: "课程、资源、画像与内容审核",
  },
  {
    icon: ShieldCheck,
    title: "平台治理中心",
    detail: "模型、权限、成本与审计管理",
  },
] as const;

function getRoleHome(roles: string[] = []) {
  if (roles.includes("admin")) return "/admin";
  if (roles.includes("teacher")) return "/teacher";
  return "/student";
}

function getSafeRedirect(value: string | null) {
  return value?.startsWith("/") && !value.startsWith("//") ? value : null;
}

export function Login() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { login, loading } = useAuthStore();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);

    try {
      const user = await login(username.trim(), password);
      notify.success(`欢迎回来，${user.real_name || user.username}`);
      const redirect = getSafeRedirect(params.get("redirect"));
      navigate(redirect || getRoleHome(user.roles), { replace: true });
    } catch (loginError) {
      setError(loginError instanceof Error ? loginError.message : "登录失败，请稍后重试");
    }
  };

  return (
    <main className="grid min-h-dvh bg-slate-50 text-slate-950 lg:grid-cols-[minmax(0,1.05fr)_minmax(420px,0.95fr)]">
      <section className="relative hidden overflow-hidden bg-zinc-950 text-white lg:flex lg:min-h-dvh lg:flex-col lg:justify-between lg:px-12 lg:py-10 xl:px-16 xl:py-12">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.8) 1px, transparent 1px)",
            backgroundSize: "40px 40px",
          }}
        />

        <div className="relative flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-lg bg-teal-600">
            <Bot className="h-6 w-6" aria-hidden="true" />
          </div>
          <div>
            <p className="text-lg font-semibold">智学工坊</p>
            <p className="text-sm text-zinc-400">EduAgent Studio</p>
          </div>
        </div>

        <div className="relative max-w-2xl py-12">
          <div className="mb-7 flex items-center gap-3 text-sm font-medium text-teal-300">
            <span className="h-px w-8 bg-teal-400" aria-hidden="true" />
            基于大模型的个性化学习多智能体系统
          </div>
          <h1 className="max-w-xl text-4xl font-semibold leading-tight sm:text-5xl">
            让教学决策有依据，
            <br />
            让每次学习有路径。
          </h1>
          <p className="mt-6 max-w-xl text-base leading-7 text-zinc-300">
            将课程知识、学习画像、资源生成与教师审核连接在同一工作流中，
            为学习者和教学团队提供持续、可追踪的智能支持。
          </p>

          <div className="mt-10 grid max-w-xl gap-3">
            {ROLE_CAPABILITIES.map(({ icon: Icon, title, detail }) => (
              <div
                key={title}
                className="grid grid-cols-[40px_minmax(0,1fr)] items-center gap-3 border-t border-white/10 py-4 first:border-t-0"
              >
                <div className="grid h-10 w-10 place-items-center rounded-md bg-white/8 text-teal-300">
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-white">{title}</p>
                  <p className="mt-1 text-sm text-zinc-400">{detail}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative flex items-center gap-2 text-xs text-zinc-500">
          <ShieldCheck className="h-4 w-4" aria-hidden="true" />
          统一身份认证与角色权限控制
        </div>
      </section>

      <section className="flex min-h-dvh items-center justify-center px-5 py-8 sm:px-8 lg:px-12">
        <div className="w-full max-w-md">
          <div className="mb-8 flex items-center gap-3 lg:hidden">
            <div className="grid h-11 w-11 place-items-center rounded-lg bg-teal-700 text-white">
              <Bot className="h-6 w-6" aria-hidden="true" />
            </div>
            <div>
              <h1 className="text-lg font-semibold">智学工坊</h1>
              <p className="text-sm text-slate-500">EduAgent Studio</p>
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <div className="mb-7">
              <div className="mb-4 grid h-10 w-10 place-items-center rounded-md bg-teal-50 text-teal-700">
                <BookOpenCheck className="h-5 w-5" aria-hidden="true" />
              </div>
              <h2 className="text-2xl font-semibold">登录工作台</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                使用平台管理员分配的账号进入对应角色空间。
              </p>
            </div>

            <form onSubmit={handleLogin} className="space-y-5">
              <div>
                <label htmlFor="username" className="mb-2 block text-sm font-medium text-slate-700">
                  用户名
                </label>
                <div className="relative">
                  <UserRound
                    className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400"
                    aria-hidden="true"
                  />
                  <input
                    id="username"
                    name="username"
                    type="text"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                    autoComplete="username"
                    autoCapitalize="none"
                    spellCheck={false}
                    required
                    disabled={loading}
                    aria-invalid={Boolean(error)}
                    className="h-12 w-full rounded-md border border-slate-300 bg-white pl-11 pr-3 text-base outline-none transition-colors placeholder:text-slate-400 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/15 disabled:cursor-not-allowed disabled:bg-slate-100"
                    placeholder="请输入用户名"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="mb-2 block text-sm font-medium text-slate-700">
                  密码
                </label>
                <div className="relative">
                  <LockKeyhole
                    className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400"
                    aria-hidden="true"
                  />
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    autoComplete="current-password"
                    required
                    disabled={loading}
                    aria-invalid={Boolean(error)}
                    className="h-12 w-full rounded-md border border-slate-300 bg-white pl-11 pr-12 text-base outline-none transition-colors placeholder:text-slate-400 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/15 disabled:cursor-not-allowed disabled:bg-slate-100"
                    placeholder="请输入密码"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((visible) => !visible)}
                    disabled={loading}
                    aria-label={showPassword ? "隐藏密码" : "显示密码"}
                    className="absolute right-0.5 top-1/2 grid h-11 w-11 -translate-y-1/2 place-items-center rounded-md text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-600 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" aria-hidden="true" />
                    ) : (
                      <Eye className="h-5 w-5" aria-hidden="true" />
                    )}
                  </button>
                </div>
              </div>

              <div aria-live="polite" className="min-h-6">
                {error ? (
                  <p className="text-sm leading-6 text-red-700" role="alert">
                    {error}
                  </p>
                ) : (
                  <p className="text-sm leading-6 text-slate-500">
                    账号或权限异常请联系平台管理员。
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="flex h-12 w-full cursor-pointer items-center justify-center gap-2 rounded-md bg-teal-700 px-4 text-sm font-semibold text-white transition-colors hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <LoaderCircle
                      className="h-4 w-4 animate-spin motion-reduce:animate-none"
                      aria-hidden="true"
                    />
                    正在验证
                  </>
                ) : (
                  <>
                    登录
                    <ArrowRight className="h-4 w-4" aria-hidden="true" />
                  </>
                )}
              </button>
            </form>
          </div>

          <p className="mt-6 text-center text-xs leading-5 text-slate-500">
            智学工坊 · EduAgent Studio
          </p>
        </div>
      </section>
    </main>
  );
}

export default Login;
