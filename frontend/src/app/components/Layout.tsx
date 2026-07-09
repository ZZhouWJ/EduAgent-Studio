import React from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth";
import { useRouterGuard } from "@/lib/router-guard";
import { Toaster } from "sonner";
import {
  ActivitySquare,
  BarChart3,
  Bell,
  BookOpen,
  Bot,
  CheckSquare,
  ChevronDown,
  CircleDot,
  Command,
  Database,
  GraduationCap,
  History,
  LayoutDashboard,
  Library,
  LineChart,
  ListChecks,
  ListTodo,
  LogOut,
  Menu,
  LockKeyhole,
  MessageSquare,
  PanelLeft,
  PieChart,
  Route,
  Search,
  Settings2,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  TerminalSquare,
  X,
  UserCog,
  UserRound,
  UserSquare2,
  Users,
} from "lucide-react";

type RoleKey = "student" | "teacher" | "admin";

type MenuItem = {
  path: string;
  label: string;
  icon: React.ComponentType<{ className?: string; strokeWidth?: number | string }>;
};

type RoleConfig = {
  brand: string;
  roleLabel: string;
  basePath: string;
  user: string;
  userMeta: string;
  avatar: string;
  accent: string;
  activeGradient: string;
  courseLine: string;
  searchHint: string;
  sections: Array<{ title: string; items: MenuItem[] }>;
  statusTitle: string;
  statusText: string;
};

const ROLE_CONFIG: Record<RoleKey, RoleConfig> = {
  student: {
    brand: "智学工坊",
    roleLabel: "学生端",
    basePath: "/student",
    user: "李明",
    userMeta: "学生 / 大二",
    avatar: "李",
    accent: "text-cyan-300",
    activeGradient: "bg-[linear-gradient(110deg,#2563EB,#06B6D4)]",
    courseLine: "当前课程：数据库系统原理与 Web 项目实践",
    searchHint: "搜索学习任务、资源或知识点",
    statusTitle: "今日学习路径已更新",
    statusText: "根据最近测评结果，建议先巩固事务隔离级别。",
    sections: [
      {
        title: "我的学习",
        items: [
          { path: "/student", label: "我的学习首页", icon: LayoutDashboard },
          { path: "/student/profile", label: "我的画像", icon: UserSquare2 },
          { path: "/student/learning-path", label: "学习路径", icon: Route },
          { path: "/student/tasks", label: "学习任务", icon: ListTodo },
          { path: "/student/resources", label: "推荐资源", icon: Library },
          { path: "/student/tutor", label: "AI 学习辅导", icon: Bot },
          { path: "/student/feedback", label: "测评与反馈", icon: MessageSquare },
          { path: "/student/report", label: "学习报告", icon: LineChart },
        ],
      },
    ],
  },
  teacher: {
    brand: "智学工坊",
    roleLabel: "教师端",
    basePath: "/teacher",
    user: "张老师",
    userMeta: "教师 / 课程负责人",
    avatar: "张",
    accent: "text-blue-300",
    activeGradient: "bg-[linear-gradient(110deg,#2563EB,#7C3AED)]",
    courseLine: "当前课程：数据库系统原理与 Web 项目实践",
    searchHint: "搜索学生、资源、审核任务",
    statusTitle: "待处理事项 4 项",
    statusText: "资源审核、薄弱点干预、反馈跟进等待处理。",
    sections: [
      {
        title: "教学工作流",
        items: [
          { path: "/teacher", label: "教学工作台", icon: LayoutDashboard },
          { path: "/teacher/courses", label: "我的课程", icon: BookOpen },
          { path: "/teacher/students", label: "学生画像", icon: Users },
          { path: "/teacher/agent-workbench", label: "智能体工作台", icon: Bot },
          { path: "/teacher/resources", label: "学习资源库", icon: Library },
          { path: "/teacher/review", label: "审核中心", icon: CheckSquare },
          { path: "/teacher/tasks", label: "学习任务", icon: ListChecks },
          { path: "/teacher/knowledge-base", label: "课程知识库", icon: Database },
          { path: "/teacher/analytics", label: "教学分析", icon: BarChart3 },
        ],
      },
    ],
  },
  admin: {
    brand: "EduAgent Studio",
    roleLabel: "管理端",
    basePath: "/admin",
    user: "王教授",
    userMeta: "管理员 / 平台治理",
    avatar: "王",
    accent: "text-emerald-300",
    activeGradient: "bg-[linear-gradient(110deg,#0F172A,#2563EB)]",
    courseLine: "平台范围：全部课程与系统服务",
    searchHint: "搜索用户、课程、调用记录",
    statusTitle: "平台治理正常",
    statusText: "模型服务、内容安全、调用审计均处于可控状态。",
    sections: [
      {
        title: "系统治理",
        items: [
          { path: "/admin", label: "系统总览", icon: LayoutDashboard },
          { path: "/admin/users", label: "用户管理", icon: Users },
          { path: "/admin/roles", label: "角色权限", icon: LockKeyhole },
          { path: "/admin/courses", label: "课程管理", icon: BookOpen },
          { path: "/admin/resources", label: "资源管理", icon: Library },
        ],
      },
      {
        title: "AI 治理",
        items: [
          { path: "/admin/model-config", label: "模型配置", icon: Settings2 },
          { path: "/admin/agent-config", label: "智能体配置", icon: Bot },
          { path: "/admin/prompts", label: "提示词模板", icon: TerminalSquare },
          { path: "/admin/audit", label: "调用审计", icon: ActivitySquare },
          { path: "/admin/costs", label: "成本统计", icon: PieChart },
          { path: "/admin/governance", label: "内容安全", icon: ShieldAlert },
          { path: "/admin/logs", label: "操作日志", icon: History },
        ],
      },
    ],
  },
};

// 角色切换已禁用：强制角色隔离，不允许用户随意切换角色
// 如需切换角色，请先退出登录再以其他账号登录

function getRoleFromUser(user: { roles?: string[] } | null): RoleKey {
  if (!user?.roles) return "student";
  if (user.roles.includes("admin")) return "admin";
  if (user.roles.includes("teacher")) return "teacher";
  if (user.roles.includes("student_member")) return "student";
  return "student";
}

function isActivePath(currentPath: string, itemPath: string) {
  if (itemPath === "/student" || itemPath === "/teacher" || itemPath === "/admin") {
    return currentPath === itemPath;
  }

  return currentPath === itemPath || currentPath.startsWith(`${itemPath}/`);
}

export function Layout() {
  useRouterGuard();
  const location = useLocation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);
  const role = getRoleFromUser(user);
  const config = ROLE_CONFIG[role];
  const allItems = config.sections.flatMap((section) => section.items);
  const activeItem = allItems.find((item) => isActivePath(location.pathname, item.path));
  const pageTitle = activeItem?.label ?? config.roleLabel;

  const navContainerRef = React.useRef<HTMLElement | null>(null);
  const itemRefs = React.useRef<Record<string, HTMLAnchorElement | null>>({});
  const [indicator, setIndicator] = React.useState<{ top: number; height: number; opacity: number }>({
    top: 0,
    height: 0,
    opacity: 0,
  });

  const realName = user?.real_name || user?.username || '游客';
  const firstChar = realName.charAt(0).toUpperCase();
  const roleLabelMap: Record<string, string> = {
    student: '学生 / 在读',
    teacher: '教师 / 课程负责人',
    admin: '管理员 / 平台治理',
  };
  const userMeta = roleLabelMap[role];

  async function handleLogout() {
    await logout();
    navigate('/login', { replace: true });
  }

  React.useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  // 滑动指示器跟随当前激活项
  React.useLayoutEffect(() => {
    const updateIndicator = () => {
      const container = navContainerRef.current;
      if (!container) return;
      const activeEl = activeItem ? itemRefs.current[activeItem.path] : null;
      if (!activeEl) {
        setIndicator((prev) => ({ ...prev, opacity: 0 }));
        return;
      }
      const containerRect = container.getBoundingClientRect();
      const itemRect = activeEl.getBoundingClientRect();
      const top = itemRect.top - containerRect.top + (itemRect.height - itemRect.height * 0.6) / 2;
      setIndicator({ top, height: itemRect.height * 0.6, opacity: 1 });
    };
    updateIndicator();
    window.addEventListener('resize', updateIndicator);
    return () => window.removeEventListener('resize', updateIndicator);
  }, [activeItem?.path, role]);

  const renderNavigation = (onNavigate?: () => void) => (
    <nav
      ref={navContainerRef}
      className="custom-scrollbar relative mt-4 flex-1 overflow-y-auto px-3 pb-4 edu-mount-fade"
      aria-label={`${config.roleLabel}导航`}
    >
      <span
        className="edu-nav-indicator"
        style={{ top: indicator.top, height: indicator.height, opacity: indicator.opacity }}
        aria-hidden
      />
      {config.sections.map((section) => (
        <div key={section.title} className="mb-5">
          <div className="mb-2 px-2 text-[11px] font-bold uppercase tracking-[0.12em] text-slate-500">
            {section.title}
          </div>
          <div className="space-y-1">
            {section.items.map((item) => {
              const isActive = isActivePath(location.pathname, item.path);
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === config.basePath}
                  onClick={onNavigate}
                  ref={(el) => {
                    itemRefs.current[item.path] = el;
                  }}
                  className={`group relative flex min-h-11 items-center gap-3 rounded-xl px-3 text-sm font-medium transition-all duration-200 hover:translate-x-[2px] ${
                    isActive
                      ? `${config.activeGradient} text-white shadow-[0_12px_28px_rgba(37,99,235,0.25)]`
                      : "text-slate-400 hover:bg-white/[0.07] hover:text-white"
                  }`}
                >
                  <Icon
                    className={`h-[18px] w-[18px] shrink-0 transition-transform duration-200 ${isActive ? "" : "group-hover:scale-110"}`}
                    strokeWidth={isActive ? 2.35 : 2}
                  />
                  <span className="truncate">{item.label}</span>
                </NavLink>
              );
            })}
          </div>
        </div>
      ))}
    </nav>
  );

  return (
    <div className="min-h-dvh w-full overflow-x-hidden bg-[#F6F8FC] text-[#0F172A] lg:flex lg:h-screen lg:overflow-hidden">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[1000] focus:rounded-lg focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-blue-700 focus:shadow-lg"
      >
        跳转到主内容
      </a>

      <aside className="relative z-20 hidden h-full w-[248px] shrink-0 flex-col overflow-hidden bg-[#0F172A] text-white shadow-[18px_0_40px_rgba(15,23,42,0.16)] lg:flex">
        <div className="absolute inset-x-0 top-0 h-44 bg-[linear-gradient(135deg,rgba(37,99,235,0.34),rgba(124,58,237,0.16),transparent_74%)]" />

        <div className="relative flex h-16 shrink-0 items-center gap-3 border-b border-white/10 px-5">
          <div className="grid h-10 w-10 place-items-center rounded-2xl border border-white/20 bg-white/10 shadow-[0_12px_30px_rgba(37,99,235,0.25)] backdrop-blur">
            <div className="relative">
              <Bot className="h-5 w-5 text-white" strokeWidth={2.2} />
              <span
                className={`absolute -right-1 -top-1 h-2 w-2 rounded-full ring-2 ring-[#0F172A] ${role === "admin" ? "bg-emerald-300" : role === "student" ? "bg-cyan-300" : "bg-blue-300"}`}
              />
            </div>
          </div>
          <div className="min-w-0">
            <div className="truncate text-[15px] font-bold leading-5">{config.brand}</div>
            <div className="truncate text-[11px] font-semibold uppercase tracking-[0.16em] text-blue-200/80">
              {config.roleLabel}
            </div>
          </div>
        </div>

        <div className="relative mx-3 mt-4 rounded-2xl border border-white/10 bg-white/[0.06] p-3">
          <div className="mb-2 flex items-center gap-2 text-[12px] font-semibold text-blue-100">
            {role === "student" ? <GraduationCap className="h-3.5 w-3.5 text-cyan-300" /> : role === "teacher" ? <Sparkles className="h-3.5 w-3.5 text-blue-300" /> : <UserCog className="h-3.5 w-3.5 text-emerald-300" />}
            {config.statusTitle}
          </div>
          <p className="text-[11px] leading-4 text-slate-300">{config.statusText}</p>
        </div>

        {renderNavigation()}

        <div className="relative border-t border-white/10 p-3">
          <div className="rounded-2xl border border-emerald-300/20 bg-emerald-400/10 p-3">
            <div className="flex items-center gap-2 text-xs font-bold text-emerald-100">
              <ShieldCheck className="h-4 w-4 text-emerald-300" />
              角色权限已隔离
            </div>
            <p className="mt-1 text-[11px] leading-4 text-emerald-100/70">当前只展示{config.roleLabel}相关任务与数据。</p>
          </div>
        </div>
      </aside>

      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button className="absolute inset-0 bg-slate-950/45" aria-label="关闭菜单" onClick={() => setIsMobileMenuOpen(false)} />
          <aside className="absolute inset-y-0 left-0 flex w-[min(88vw,340px)] flex-col overflow-hidden bg-[#0F172A] text-white shadow-[18px_0_52px_rgba(15,23,42,0.28)]">
            <div className="absolute inset-x-0 top-0 h-44 bg-[linear-gradient(135deg,rgba(37,99,235,0.34),rgba(124,58,237,0.16),transparent_74%)]" />
            <div className="relative flex min-h-16 items-center justify-between gap-3 border-b border-white/10 px-4">
              <div className="flex min-w-0 items-center gap-3">
                <div className="grid h-10 w-10 shrink-0 place-items-center rounded-2xl border border-white/20 bg-white/10">
                  <Bot className="h-5 w-5 text-white" />
                </div>
                <div className="min-w-0">
                  <div className="truncate text-[15px] font-bold leading-5">{config.brand}</div>
                  <div className="truncate text-[11px] font-semibold uppercase tracking-[0.16em] text-blue-200/80">{config.roleLabel}</div>
                </div>
              </div>
              <button
                className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-white/10 bg-white/[0.06] text-slate-200"
                aria-label="关闭菜单"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="relative mx-3 mt-4 rounded-2xl border border-white/10 bg-white/[0.06] p-3">
              <div className="mb-2 flex items-center gap-2 text-[12px] font-semibold text-blue-100">
                <UserRound className="h-3.5 w-3.5 text-blue-300" />
                {config.user} · {userMeta}
              </div>
              <p className="text-[11px] leading-4 text-slate-300">{config.courseLine}</p>
            </div>

            {renderNavigation(() => setIsMobileMenuOpen(false))}

            <div className="relative border-t border-white/10 p-3">
              <button
                onClick={async () => { await handleLogout(); setIsMobileMenuOpen(false) }}
                className="flex min-h-11 items-center gap-3 rounded-xl px-3 text-sm font-bold text-slate-300 transition hover:bg-white/[0.07] hover:text-white"
              >
                <LogOut className="h-[18px] w-[18px]" />
                退出登录
              </button>
            </div>
          </aside>
        </div>
      )}

      <div className="min-w-0 lg:flex lg:flex-1 lg:flex-col">
        <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-[#E2E8F0] bg-white/[0.94] px-4 backdrop-blur-xl lg:hidden">
          <div className="flex min-w-0 items-center gap-3">
            <button
              className="grid h-11 w-11 shrink-0 place-items-center rounded-xl border border-slate-200 bg-white text-slate-600 shadow-sm"
              aria-label="打开菜单"
              onClick={() => setIsMobileMenuOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="min-w-0">
              <h1 className="truncate text-base font-black text-slate-950">{pageTitle}</h1>
              <div className="mt-0.5 flex items-center gap-1.5 text-[11px] font-bold text-blue-700">
                <CircleDot className="h-3 w-3 text-blue-500" />
                {config.roleLabel}
              </div>
            </div>
          </div>
          <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[linear-gradient(135deg,#EFF6FF,#F5F3FF)] text-sm font-black text-blue-700 ring-1 ring-blue-100">
            {firstChar}
          </div>
        </header>

        <header className="sticky top-0 z-10 hidden h-16 shrink-0 items-center justify-between border-b border-[#E2E8F0] bg-white/[0.92] px-6 backdrop-blur-xl lg:flex">
          <div className="flex min-w-0 items-center gap-4">
            <button
              className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 bg-white text-slate-600 shadow-sm transition hover:border-blue-200 hover:text-blue-700"
              aria-label="切换侧边栏"
            >
              <PanelLeft className="h-[18px] w-[18px]" />
            </button>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h1 className="truncate text-lg font-bold text-[#0F172A]">{pageTitle}</h1>
                <span className="hidden rounded-full bg-blue-50 px-2.5 py-1 text-[11px] font-bold text-blue-700 ring-1 ring-blue-100 lg:inline-flex">
                  {config.roleLabel}
                </span>
              </div>
              <div className="mt-0.5 hidden items-center gap-1.5 text-xs font-medium text-slate-500 md:flex">
                <CircleDot className="h-3 w-3 text-blue-500" />
                {config.courseLine}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative hidden lg:block">
              <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="search"
                aria-label={config.searchHint}
                className="edu-focus-ring h-10 w-[312px] rounded-xl border border-slate-200 bg-slate-50/80 pl-10 pr-10 text-sm text-slate-700"
              />
              <Command className="pointer-events-none absolute right-3.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-300" />
            </div>

            <button
              className="relative grid h-10 w-10 place-items-center rounded-xl border border-slate-200 bg-white text-slate-500 shadow-sm transition hover:border-blue-200 hover:text-blue-700"
              aria-label="查看通知"
            >
              <Bell className="h-[18px] w-[18px]" />
              <span className="absolute right-2.5 top-2.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white" />
            </button>

            <div className="hidden h-8 w-px bg-slate-200 sm:block" />

            <button onClick={handleLogout} className="flex h-11 items-center gap-3 rounded-2xl border border-slate-200 bg-white px-2.5 py-1.5 shadow-sm transition hover:border-blue-200">
              <div className="hidden text-right sm:block">
                <div className="text-sm font-bold leading-4 text-slate-800">{realName}</div>
                <div className="mt-0.5 text-[11px] font-semibold text-blue-700">{userMeta}</div>
              </div>
              <div className="grid h-8 w-8 place-items-center rounded-xl bg-[linear-gradient(135deg,#EFF6FF,#F5F3FF)] text-sm font-black text-blue-700 ring-1 ring-blue-100">
                {firstChar}
              </div>
              <ChevronDown className="h-4 w-4 text-slate-400" />
            </button>
          </div>
        </header>

        <main id="main-content" className="custom-scrollbar min-h-[calc(100dvh-56px)] overflow-x-hidden overflow-y-auto p-4 sm:p-5 lg:min-h-0 lg:flex-1 lg:overflow-auto lg:p-6">
          <Outlet />
        </main>
      </div>
      <Toaster position="top-right" richColors />
    </div>
  );
}
