import React from "react";
import { useNavigate } from "react-router";
import { AlertTriangle, Bot, CheckCircle2, ClipboardCheck, FileWarning, Gauge, LockKeyhole, ShieldAlert, ShieldCheck, SlidersHorizontal } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { reviewsApi, statisticsApi } from "@/lib/api";
import { notify } from "@/lib/toast";

const GOVERNANCE_RULES = [
  ["事实一致性阈值", "≥ 80%", "低于阈值必须进入教师复核"],
  ["引用覆盖率阈值", "≥ 75%", "课程讲义和实验案例强制启用"],
  ["高频调用限制", "50 次 / 小时", "超限进入审计队列"],
  ["敏感内容检测", "启用", "输出前后双重扫描"],
];

export function AdminGovernance() {
  const navigate = useNavigate();
  const reviewsState = useApi(() => statisticsApi.reviews(), []);
  const pendingState = useApi(() => reviewsApi.getPending({ page_size: 4 }), []);

  const reviews = reviewsState.data;
  const pendingList = pendingState.data?.items ?? [];
  const highRiskCount = reviews?.top_issue_tags?.filter((t) => t.severity === "high").length ?? 0;

  // Derive risk queue from real pending + top_issue_tags
  const riskQueue = pendingList.slice(0, 4).map((p) => ({
    id: p.request_id,
    title: p.output_title || "待审核资源",
    level: p.request_status === "high_risk" ? "高风险" :
           reviews?.top_issue_tags?.[0]?.severity === "high" ? "中风险" : "低风险",
    owner: p.submitter_real_name || p.submitter_username || "—",
    reason: p.submit_note || "AI 生成内容待人工复核",
  }));

  const finalQueue = riskQueue.length > 0 ? riskQueue : [
    { id: 0, title: "暂无待办风险事项", level: "—", owner: "—", reason: "等待数据" },
  ];

  const stats = [
    { label: "高风险内容", value: String(highRiskCount || "—"), Icon: ShieldAlert, cls: "bg-red-50 text-red-700 ring-red-100" },
    { label: "待复核资源", value: String(reviews?.revision_required_count ?? "—"), Icon: ClipboardCheck, cls: "bg-orange-50 text-orange-700 ring-orange-100" },
    { label: "异常调用", value: "—", Icon: Gauge, cls: "bg-purple-50 text-purple-700 ring-purple-100" },
    { label: "已拦截输出", value: String(reviews?.rejected_count ?? "—"), Icon: ShieldCheck, cls: "bg-emerald-50 text-emerald-700 ring-emerald-100" },
  ];

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      {/* Header */}
      <section className="edu-card relative overflow-hidden rounded-[24px] p-7">
        <div className="absolute inset-0 edu-grid-bg opacity-45" />
        <div className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,#EF4444,#F59E0B,#2563EB)]" />
        <div className="relative flex items-start justify-between gap-6">
          <div>
            <div className="mb-4 flex w-fit cursor-pointer items-center gap-2 rounded-full border border-red-100 bg-red-50 px-3 py-1.5 text-xs font-bold text-red-700">
              <ShieldAlert className="h-3.5 w-3.5" />
              Admin AI Governance
            </div>
            <h1 className="text-2xl font-black text-slate-950">内容安全与 AI 治理监控</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              聚合低可信资源、高风险生成内容、异常调用记录和治理规则，确保 AI 生成内容可控、可追溯、可复核。
            </p>
          </div>
          <button
            onClick={() => notify.info("阈值编辑（演示模式）")}
            className="inline-flex min-h-11 cursor-pointer items-center gap-2 rounded-xl bg-slate-950 px-5 text-sm font-black text-white transition hover:bg-slate-800"
          >
            更新治理规则
            <SlidersHorizontal className="h-4 w-4" />
          </button>
        </div>
      </section>

      {/* KPI Cards */}
      <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map(({ label, value, Icon, cls }) => (
          <div key={label} className="edu-card edu-card-hover cursor-pointer rounded-2xl p-5">
            <div className={`mb-4 grid h-11 w-11 place-items-center rounded-xl ring-1 ${cls}`}>
              <Icon className="h-5 w-5" />
            </div>
            <div className="text-sm font-semibold text-slate-500">{label}</div>
            <div className="mt-1 text-3xl font-black text-slate-950">{reviewsState.loading ? "..." : value}</div>
          </div>
        ))}
      </section>

      {/* Risk Queue + Governance Rules */}
      <section className="grid grid-cols-[1.2fr_0.8fr] gap-6">
        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex cursor-pointer items-center gap-2 text-lg font-black text-slate-950">
            <FileWarning className="h-5 w-5 text-red-600" />
            风险队列
          </h2>
          <div className="space-y-3">
            {finalQueue.map((risk) => (
              <div key={risk.id} className="grid grid-cols-[1fr_auto] cursor-pointer items-start gap-4 rounded-2xl border border-slate-100 bg-white p-4 transition hover:border-red-200">
                <div>
                  <h3 className="text-sm font-black text-slate-900">{risk.title}</h3>
                  <p className="mt-1 text-xs leading-5 text-slate-500">{risk.reason}</p>
                  <p className="mt-2 text-xs font-bold text-slate-400">{risk.owner}</p>
                </div>
                <div className="flex flex-col items-end justify-between">
                  <span className={`rounded-full px-2 py-1 text-[11px] font-black ${
                    risk.level === "高风险" ? "bg-red-50 text-red-700" :
                    risk.level === "中风险" ? "bg-orange-50 text-orange-700" :
                    "bg-slate-100 text-slate-600"
                  }`}>
                    {risk.level}
                  </span>
                  <button
                    onClick={() => navigate(`/admin/audit?request=${risk.id}`)}
                    className="cursor-pointer text-xs font-black text-blue-700 hover:text-blue-800"
                  >
                    查看详情
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex cursor-pointer items-center gap-2 text-lg font-black text-slate-950">
            <LockKeyhole className="h-5 w-5 text-slate-700" />
            治理规则
          </h2>
          <div className="space-y-3">
            {GOVERNANCE_RULES.map(([name, value, desc]) => (
              <div key={name} className="rounded-2xl border border-slate-100 bg-slate-50/70 p-4">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-black text-slate-900">{name}</div>
                  <div className="rounded-full bg-white px-2 py-1 text-xs font-black text-blue-700 ring-1 ring-blue-100">{value}</div>
                </div>
                <p className="mt-2 text-xs leading-5 text-slate-500">{desc}</p>
              </div>
            ))}
          </div>
          <div className="mt-5 rounded-2xl border border-blue-100 bg-blue-50 p-4">
            <div className="mb-2 flex items-center gap-2 text-sm font-black text-blue-900">
              <Bot className="h-4 w-4" />
              AI 自检链路
            </div>
            <div className="grid grid-cols-3 gap-2 text-center text-xs font-bold text-blue-700">
              {["生成前约束", "输出后检测", "人工复核"].map((s) => (
                <span key={s} className="rounded-lg bg-white py-2 ring-1 ring-blue-100">{s}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Governance Actions */}
      <section className="edu-card rounded-2xl p-6">
        <h2 className="mb-4 text-lg font-black text-slate-950">治理动作记录</h2>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {[
            ["已通知教师复核", `${pendingList.length} 条资源进入课程负责人队列`],
            ["已限制异常调用", "3 个账号进入观察名单"],
            ["已更新 Prompt 规则", "新增事实一致性提示约束"],
            ["已归档优秀资源", "42 条资源成为课程模板"],
          ].map(([title, desc]) => (
            <div key={title} className="rounded-2xl border border-slate-100 bg-white p-4">
              <CheckCircle2 className="mb-3 h-5 w-5 text-emerald-600" />
              <h3 className="text-sm font-black text-slate-900">{title}</h3>
              <p className="mt-2 text-xs leading-5 text-slate-500">{desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
