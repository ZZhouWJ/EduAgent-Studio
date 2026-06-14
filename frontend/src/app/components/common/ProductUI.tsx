import React from "react";
import { Search, X } from "lucide-react";

type IconComponent = React.ComponentType<{ className?: string; strokeWidth?: number }>;

type PageHeaderProps = {
  eyebrow?: string;
  title: string;
  description: string;
  icon?: IconComponent;
  action?: React.ReactNode;
};

export function PageShell({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`page-shell flex flex-col gap-5 sm:gap-6 ${className}`}>{children}</div>;
}

export function PageHeader({ eyebrow, title, description, icon: Icon, action }: PageHeaderProps) {
  return (
    <section className="edu-card relative overflow-hidden rounded-[20px] p-5 sm:rounded-[24px] sm:p-6 lg:p-7">
      <div className="absolute inset-0 edu-grid-bg opacity-45" />
      <div className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,#2563EB,#7C3AED,#06B6D4)]" />
      <div className="relative flex flex-col items-stretch justify-between gap-5 lg:flex-row lg:items-start lg:gap-6">
        <div className="min-w-0">
          {eyebrow && (
            <div className="mb-4 flex w-fit items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700">
              {Icon && <Icon className="h-3.5 w-3.5" />}
              {eyebrow}
            </div>
          )}
          <h1 className="text-2xl font-black leading-tight text-slate-950 sm:text-[30px]">{title}</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{description}</p>
        </div>
        {action && <div className="flex shrink-0 flex-col gap-2 sm:flex-row lg:justify-end">{action}</div>}
      </div>
    </section>
  );
}

type StatCardProps = {
  label: string;
  value: string;
  hint?: string;
  icon: IconComponent;
  tone?: "blue" | "purple" | "emerald" | "orange" | "red" | "cyan" | "slate";
};

const toneClass: Record<NonNullable<StatCardProps["tone"]>, string> = {
  blue: "bg-blue-50 text-blue-700 ring-blue-100",
  purple: "bg-purple-50 text-purple-700 ring-purple-100",
  emerald: "bg-emerald-50 text-emerald-700 ring-emerald-100",
  orange: "bg-orange-50 text-orange-700 ring-orange-100",
  red: "bg-red-50 text-red-700 ring-red-100",
  cyan: "bg-cyan-50 text-cyan-700 ring-cyan-100",
  slate: "bg-slate-100 text-slate-800 ring-slate-200",
};

export function StatCard({ label, value, hint, icon: Icon, tone = "blue" }: StatCardProps) {
  return (
    <div className="edu-card edu-card-hover rounded-2xl p-4">
      <div className={`mb-4 grid h-10 w-10 place-items-center rounded-xl ring-1 ${toneClass[tone]}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="text-sm font-semibold text-slate-500">{label}</div>
      <div className="mt-1 text-[25px] font-black leading-8 text-slate-950">{value}</div>
      {hint && <div className="mt-1 text-xs font-medium text-slate-400">{hint}</div>}
    </div>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const cls =
    status.includes("正常") || status.includes("完成") || status.includes("启用") || status.includes("成功") || status.includes("通过")
      ? "bg-emerald-50 text-emerald-700 ring-emerald-100"
      : status.includes("风险") || status.includes("异常") || status.includes("禁用") || status.includes("失败")
        ? "bg-red-50 text-red-700 ring-red-100"
        : status.includes("进行") || status.includes("活跃") || status.includes("运行")
          ? "bg-blue-50 text-blue-700 ring-blue-100"
          : "bg-orange-50 text-orange-700 ring-orange-100";

  return <span className={`rounded-full px-2.5 py-1 text-[11px] font-black ring-1 ${cls}`}>{status}</span>;
}

export function ProgressBar({ value, tone = "blue" }: { value: number; tone?: "blue" | "emerald" | "orange" | "red" | "purple" }) {
  const color = {
    blue: "bg-blue-600",
    emerald: "bg-emerald-500",
    orange: "bg-orange-500",
    red: "bg-red-500",
    purple: "bg-purple-600",
  }[tone];

  return (
    <div className="h-2 overflow-hidden rounded-full bg-slate-100">
      <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
    </div>
  );
}

export function SearchInput({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="block min-w-0 flex-1 text-xs font-bold text-slate-500 sm:min-w-[240px]">
      {label}
      <div className="relative mt-1.5">
        <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          aria-label={label}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className="edu-focus-ring h-11 w-full rounded-xl border border-slate-200 bg-slate-50 pl-10 pr-3 text-sm font-medium text-slate-700"
        />
      </div>
    </label>
  );
}

export function SegmentedControl({ value, options, onChange }: { value: string; options: string[]; onChange: (value: string) => void }) {
  return (
    <div className="flex w-full flex-wrap gap-1 rounded-2xl bg-slate-100 p-1 sm:w-auto">
      {options.map((option) => (
        <button
          key={option}
          onClick={() => onChange(option)}
          className={`min-h-10 flex-1 rounded-xl px-3 text-sm font-bold transition sm:flex-none ${
            value === option ? "bg-white text-blue-700 shadow-sm" : "text-slate-500 hover:text-slate-800"
          }`}
        >
          {option}
        </button>
      ))}
    </div>
  );
}

export function DetailDrawer({
  title,
  subtitle,
  open,
  onClose,
  children,
}: {
  title: string;
  subtitle?: string;
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <button className="absolute inset-0 cursor-default bg-slate-950/35" aria-label="关闭详情层" onClick={onClose} />
      <aside className="absolute right-0 top-0 flex h-full w-full flex-col overflow-hidden bg-white shadow-[-18px_0_50px_rgba(15,23,42,0.22)] sm:w-[520px] sm:max-w-[92vw]">
        <div className="border-b border-slate-100 p-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl font-black text-slate-950">{title}</h2>
              {subtitle && <p className="mt-1 text-sm leading-6 text-slate-500">{subtitle}</p>}
            </div>
            <button onClick={onClose} className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 text-slate-500 hover:border-blue-200 hover:text-blue-700" aria-label="关闭详情">
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
        <div className="custom-scrollbar flex-1 overflow-y-auto p-5">{children}</div>
      </aside>
    </div>
  );
}

export function ModalShell({
  title,
  open,
  onClose,
  children,
}: {
  title: string;
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 grid place-items-stretch bg-slate-950/35 p-0 sm:place-items-center sm:p-6">
      <div className="edu-card flex h-full w-full flex-col overflow-hidden rounded-none bg-white sm:h-auto sm:max-h-[92dvh] sm:max-w-[640px] sm:rounded-2xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <h2 className="text-lg font-black text-slate-950">{title}</h2>
          <button onClick={onClose} className="grid h-9 w-9 place-items-center rounded-xl border border-slate-200 text-slate-500 hover:border-blue-200 hover:text-blue-700" aria-label="关闭弹窗">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="custom-scrollbar flex-1 overflow-y-auto p-5">{children}</div>
      </div>
    </div>
  );
}

export function EmptyState({ title, description, action }: { title: string; description: string; action?: React.ReactNode }) {
  return (
    <div className="edu-card rounded-2xl p-8 text-center">
      <h3 className="text-lg font-black text-slate-900">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">{description}</p>
      {action && <div className="mt-5 flex justify-center">{action}</div>}
    </div>
  );
}

export function useInlineToast() {
  const [message, setMessage] = React.useState("");

  React.useEffect(() => {
    if (!message) return;
    const timer = window.setTimeout(() => setMessage(""), 2600);
    return () => window.clearTimeout(timer);
  }, [message]);

  const toast = message ? (
    <div className="fixed bottom-4 left-4 right-4 z-[70] rounded-2xl border border-emerald-100 bg-white px-4 py-3 text-sm font-bold text-slate-800 shadow-[0_18px_46px_rgba(15,23,42,0.18)] sm:left-auto sm:right-6 sm:bottom-6">
      <span className="mr-2 inline-block h-2 w-2 rounded-full bg-emerald-500" />
      {message}
    </div>
  ) : null;

  return { toast, showToast: setMessage };
}

export const primaryButton =
  "inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 text-sm font-black text-white shadow-[0_12px_26px_rgba(37,99,235,0.22)] transition hover:bg-blue-700";

export const secondaryButton =
  "inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-sm font-bold text-slate-700 transition hover:border-blue-200 hover:text-blue-700";
