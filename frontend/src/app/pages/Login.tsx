import React from "react";
import { useNavigate, useSearchParams } from "react-router";
import { notify } from "@/lib/toast";
import { useAuthStore } from "@/stores/auth";
import {
  ArrowRight,
  BookOpenCheck,
  Bot,
  BrainCircuit,
  CheckCircle2,
  GraduationCap,
  LockKeyhole,
  Network,
  ShieldCheck,
  Sparkles,
  UserCog,
  UserRound,
  Users,
} from "lucide-react";

const FLOW = ["学生画像", "智能体诊断", "路径规划", "资源生成", "教师审核", "学习反馈", "持续优化"];

const ROLE_ENTRIES = [
  {
    role: "学生体验",
    desc: "查看个性化学习路径、推荐资源和学习反馈",
    account: "student01 / Student@123",
    path: "/student",
    icon: GraduationCap,
    cls: "bg-blue-50 text-blue-700 ring-blue-100",
  },
  {
    role: "教师体验",
    desc: "管理课程、生成资源、审核 AI 内容和查看教学分析",
    account: "teacher01 / Teacher@123",
    path: "/teacher",
    icon: Users,
    cls: "bg-purple-50 text-purple-700 ring-purple-100",
  },
  {
    role: "管理员体验",
    desc: "管理用户、模型、调用审计和平台运行状态",
    account: "admin / Admin@123456",
    path: "/admin",
    icon: UserCog,
    cls: "bg-slate-100 text-slate-800 ring-slate-200",
  },
];

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
    <div className="flex min-h-dvh w-full overflow-x-hidden bg-[#F6F8FC] text-slate-950 lg:h-screen lg:min-h-[760px] lg:overflow-hidden">
      <section className="relative hidden w-[60%] min-w-[720px] flex-col justify-between overflow-hidden bg-[#101C48] p-12 text-white lg:flex">
        <div className="absolute inset-0 edu-grid-bg opacity-[0.18]" />
        <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(37,99,235,0.92),rgba(30,41,59,0.72)_48%,rgba(124,58,237,0.86))]" />
        <div className="absolute left-12 right-12 top-[42%] h-px bg-gradient-to-r from-transparent via-white/30 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-36 bg-[linear-gradient(180deg,transparent,rgba(15,23,42,0.38))]" />

        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="grid h-12 w-12 place-items-center rounded-2xl border border-white/25 bg-white/10 shadow-[0_18px_44px_rgba(37,99,235,0.35)] backdrop-blur">
              <Bot className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black tracking-tight">智学工坊</h1>
              <p className="mt-1 text-sm font-bold uppercase tracking-[0.22em] text-blue-100/80">EduAgent Studio</p>
            </div>
          </div>

          <div className="mt-14 max-w-3xl">
            <div className="mb-4 flex w-fit items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-bold text-blue-100 backdrop-blur">
              <Sparkles className="h-3.5 w-3.5 text-cyan-200" />
              大模型驱动的高校课程资源生成平台
            </div>
            <h2 className="text-[44px] font-black leading-[1.12] tracking-tight">
              基于大模型的个性化学习资源生成与
              <span className="block text-cyan-100">多智能体协作系统</span>
            </h2>
            <p className="mt-5 max-w-2xl text-base leading-7 text-blue-50/[0.82]">
              从学生画像、课程知识库、多智能体协作到教师审核与学习反馈，形成可追溯、可治理、可展示的个性化学习闭环。
            </p>
          </div>
        </div>

        <div className="relative z-10 mx-auto w-full max-w-3xl">
          <div className="rounded-[24px] border border-white/20 bg-white/10 p-5 shadow-[0_24px_70px_rgba(15,23,42,0.28)] backdrop-blur-xl">
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-bold text-white">
                <Network className="h-5 w-5 text-cyan-200" />
                智能体协同闭环
              </div>
              <div className="rounded-full bg-emerald-300/15 px-3 py-1 text-xs font-bold text-emerald-100 ring-1 ring-emerald-200/20">
                Evidence Tracked
              </div>
            </div>

            <div className="relative grid grid-cols-7 gap-2">
              <div className="absolute left-8 right-8 top-6 h-px bg-gradient-to-r from-cyan-200/40 via-white/35 to-purple-200/40" />
              {FLOW.map((item, index) => (
                <div key={item} className="relative flex flex-col items-center gap-2">
                  <div className="grid h-12 w-12 place-items-center rounded-2xl border border-white/20 bg-white/[0.12] text-white shadow-lg backdrop-blur">
                    {index === 0 ? (
                      <GraduationCap className="h-5 w-5" />
                    ) : index === 1 ? (
                      <BrainCircuit className="h-5 w-5" />
                    ) : index === 4 ? (
                      <ShieldCheck className="h-5 w-5" />
                    ) : (
                      <CheckCircle2 className="h-5 w-5" />
                    )}
                  </div>
                  <div className="text-center text-[11px] font-bold leading-4 text-blue-50">{item}</div>
                </div>
              ))}
            </div>

            <div className="mt-5 grid grid-cols-3 gap-3">
              {[
                ["画像维度", "8 类"],
                ["资源形态", "6 种"],
                ["审核链路", "全追溯"],
              ].map(([label, value]) => (
                <div key={label} className="rounded-2xl border border-white/[0.12] bg-white/[0.08] p-3">
                  <div className="text-[11px] font-bold text-blue-100/[0.70]">{label}</div>
                  <div className="mt-1 text-lg font-black text-white">{value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="relative z-10">
          <p className="w-fit rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-bold text-blue-50 backdrop-blur">
            让每位学生都拥有专属的课程资源生成智能体。
          </p>
        </div>
      </section>

      <section className="flex min-w-0 flex-1 items-center justify-center px-4 py-6 sm:p-8">
        <div className="w-full max-w-[430px]">
          <div className="mb-6 text-center lg:hidden">
            <div className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-2xl bg-[linear-gradient(135deg,#2563EB,#7C3AED)] text-white shadow-lg shadow-blue-500/20">
              <Bot className="h-7 w-7" />
            </div>
            <h1 className="text-2xl font-black text-slate-950">智学工坊 EduAgent Studio</h1>
          </div>

          <div className="edu-card rounded-[22px] p-5 sm:rounded-[24px] sm:p-8">
            <div className="mb-6 text-center">
              <div className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-[linear-gradient(135deg,#2563EB,#7C3AED)] text-white shadow-[0_16px_36px_rgba(37,99,235,0.24)]">
                <BookOpenCheck className="h-7 w-7" />
              </div>
              <h2 className="text-2xl font-black text-slate-950">欢迎登录智学工坊</h2>
              <p className="mt-2 text-sm font-medium text-slate-500">开启个性化学习资源生成之旅</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-5">
              <div>
                <label htmlFor="username" className="mb-1.5 block text-sm font-bold text-slate-700">
                  用户名
                </label>
                <div className="relative">
                  <UserRound className="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-slate-400" />
                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="edu-focus-ring h-11 w-full rounded-xl border border-slate-200 bg-slate-50 pl-10 pr-4 text-sm text-slate-800"
                    autoComplete="username"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="mb-1.5 block text-sm font-bold text-slate-700">
                  密码
                </label>
                <div className="relative">
                  <LockKeyhole className="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-slate-400" />
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="edu-focus-ring h-11 w-full rounded-xl border border-slate-200 bg-slate-50 pl-10 pr-4 text-sm text-slate-800"
                    autoComplete="current-password"
                  />
                </div>
              </div>

              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <label className="flex min-h-10 cursor-pointer items-center gap-2">
                  <input type="checkbox" className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                  <span className="text-sm font-medium text-slate-600">记住我</span>
                </label>
                <a href="#" className="inline-flex min-h-10 items-center text-sm font-bold text-blue-700 hover:text-blue-800">
                  忘记密码？
                </a>
              </div>

              <button
                type="submit"
                disabled={loading}
                aria-busy={loading}
                className="group flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-[linear-gradient(110deg,#2563EB,#7C3AED)] text-sm font-black text-white shadow-[0_16px_36px_rgba(37,99,235,0.26)] transition hover:shadow-[0_20px_42px_rgba(37,99,235,0.32)] disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? '登录中...' : '登录系统'}
                {!loading && <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />}
              </button>
            </form>

            <div className="mt-6 border-t border-slate-100 pt-5">
              <div className="mb-3 flex items-center justify-between">
                <p className="text-xs font-black uppercase tracking-[0.14em] text-slate-400">角色体验入口</p>
                <span className="rounded-full bg-emerald-50 px-2 py-1 text-[11px] font-bold text-emerald-700 ring-1 ring-emerald-100">
                  Role Demo
                </span>
              </div>
              <div className="space-y-2">
                {ROLE_ENTRIES.map((entry) => {
                  const Icon = entry.icon;
                  return (
                    <button
                      key={entry.role}
                      type="button"
                      onClick={() => {
                        setUsername(entry.account.split(' / ')[0]);
                        notify.info(`已填入 ${entry.account.split(' / ')[0]}，请输入密码后登录`);
                      }}
                      className="flex min-h-11 w-full items-center gap-3 rounded-2xl border border-slate-100 bg-slate-50 p-3 text-left transition hover:border-blue-200 hover:bg-white hover:shadow-sm"
                    >
                      <div className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl ring-1 ${entry.cls}`}>
                        <Icon className="h-5 w-5" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-3">
                          <span className="text-sm font-black text-slate-900">{entry.role}</span>
                          <span className="hidden truncate font-mono text-[11px] font-bold text-slate-400 sm:inline">{entry.account}</span>
                        </div>
                        <p className="mt-1 text-xs leading-5 text-slate-500">{entry.desc}</p>
                      </div>
                      <ArrowRight className="h-4 w-4 shrink-0 text-slate-300" />
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
