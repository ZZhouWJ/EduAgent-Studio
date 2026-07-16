import React from "react";
import { useNavigate } from "react-router-dom";
import { Bot, CheckCircle2, ClipboardCheck, FileWarning, Gauge, LockKeyhole, ShieldAlert, ShieldCheck, SlidersHorizontal } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { platformSettingsApi, resourcesApi, statisticsApi, type GovernanceSettingsUpdate } from "@/lib/api";
import { notify } from "@/lib/toast";
import { ModalShell, primaryButton, secondaryButton } from "../components/common/ProductUI";

const DEFAULT_FORM: GovernanceSettingsUpdate = {
  fact_consistency_threshold: 80,
  citation_coverage_threshold: 75,
  hourly_call_limit: 50,
  sensitive_content_enabled: true,
};

export function AdminGovernance() {
  const navigate = useNavigate();
  const [editorOpen, setEditorOpen] = React.useState(false);
  const [saving, setSaving] = React.useState(false);
  const [form, setForm] = React.useState<GovernanceSettingsUpdate>(DEFAULT_FORM);

  const pendingState = useApi(
    () => resourcesApi.list({ status: "pending_review", page: 1, page_size: 100 }),
    [],
  );
  const modelCallsState = useApi(() => statisticsApi.modelCalls(), []);
  const resourcesState = useApi(() => statisticsApi.getResourceStats(), []);
  const settingsState = useApi(() => platformSettingsApi.getGovernance(), []);

  const pendingList = pendingState.data?.items ?? [];
  const modelCalls = modelCallsState.data ?? [];
  const governance = settingsState.data;
  const rejectedResourceCount = resourcesState.data?.rejected ?? 0;
  const abnormalCallCount = modelCalls.reduce(
    (total, model) => total + Number(model.failed_count || 0) + Number(model.timeout_count || 0),
    0,
  );
  const blockedCallCount = modelCalls.reduce(
    (total, model) => total + Number(model.blocked_count || 0),
    0,
  );

  const riskQueue = pendingList.slice(0, 4).map((resource) => ({
    id: resource.resource_id,
    courseId: resource.course_id,
    title: resource.resource_title || "待审核资源",
    level: "待复核",
    course: resource.course_name || "未分配课程",
    reason: "生成内容已提交人工复核，审核通过后才会向学生开放。",
  }));

  const stats = [
    { label: "已退回资源", value: String(rejectedResourceCount), Icon: ShieldAlert, cls: "bg-red-50 text-red-700 ring-red-100" },
    { label: "待复核资源", value: String(resourcesState.data?.pending ?? 0), Icon: ClipboardCheck, cls: "bg-orange-50 text-orange-700 ring-orange-100" },
    { label: "异常调用", value: String(abnormalCallCount), Icon: Gauge, cls: "bg-slate-100 text-slate-700 ring-slate-200" },
    { label: "已拦截调用", value: String(blockedCallCount), Icon: ShieldCheck, cls: "bg-emerald-50 text-emerald-700 ring-emerald-100" },
  ];

  const governanceRules = [
    ["事实一致性阈值", governance ? `≥ ${governance.fact_consistency_threshold}%` : "—", "低于阈值必须进入教师复核"],
    ["引用覆盖率阈值", governance ? `≥ ${governance.citation_coverage_threshold}%` : "—", "课程讲义和实验案例强制启用"],
    ["高频调用限制", governance ? `${governance.hourly_call_limit} 次 / 小时` : "—", "超限进入审计队列"],
    ["敏感内容检测", governance ? (governance.sensitive_content_enabled ? "启用" : "停用") : "—", "输出前后双重扫描"],
  ];

  const governanceActions = [
    ["待教师复核", `${resourcesState.data?.pending ?? 0} 条资源在课程审核队列`],
    ["调用拦截记录", `${blockedCallCount} 次模型调用被治理策略拦截`],
    ["资源审核通过率", `${((resourcesState.data?.pass_rate ?? 0) * 100).toFixed(1)}% 的已审资源通过复核`],
    ["审核通过资源", `${resourcesState.data?.approved ?? 0} 条资源已通过人工审核`],
  ];

  const openEditor = () => {
    if (!governance) {
      notify.error(settingsState.error ? "治理规则加载失败" : "治理规则正在加载");
      return;
    }
    setForm({
      fact_consistency_threshold: governance.fact_consistency_threshold,
      citation_coverage_threshold: governance.citation_coverage_threshold,
      hourly_call_limit: governance.hourly_call_limit,
      sensitive_content_enabled: governance.sensitive_content_enabled,
    });
    setEditorOpen(true);
  };

  const saveGovernance = async () => {
    setSaving(true);
    try {
      await platformSettingsApi.updateGovernance(form);
      await settingsState.refetch();
      setEditorOpen(false);
      notify.success("治理规则已保存");
    } catch (error) {
      notify.error("保存失败：" + (error instanceof Error ? error.message : String(error)));
    } finally {
      setSaving(false);
    }
  };

  const setThreshold = (
    key: "fact_consistency_threshold" | "citation_coverage_threshold",
    value: number,
  ) => {
    setForm((current) => ({
      ...current,
      [key]: Math.min(100, Math.max(0, value)),
    }));
  };

  const statsLoading = resourcesState.loading || modelCallsState.loading;

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <section className="edu-card relative overflow-hidden rounded-2xl p-7">
        <div className="relative flex flex-col items-start justify-between gap-6 sm:flex-row">
          <div>
            <div className="mb-4 flex w-fit items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-600">
              <ShieldAlert className="h-3.5 w-3.5" />
              内容治理
            </div>
            <h1 className="text-2xl font-semibold text-slate-900">内容安全与治理监控</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              聚合低可信资源、高风险生成内容、异常调用记录和治理规则，确保自动生成内容可控、可追溯、可复核。
            </p>
          </div>
          <button
            onClick={openEditor}
            disabled={settingsState.loading}
            className="inline-flex min-h-10 cursor-pointer items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 disabled:cursor-wait disabled:opacity-60"
          >
            更新治理规则
            <SlidersHorizontal className="h-4 w-4" />
          </button>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map(({ label, value, Icon, cls }) => (
          <div key={label} className="edu-card rounded-2xl p-5">
            <div className={`mb-4 grid h-11 w-11 place-items-center rounded-xl ring-1 ${cls}`}>
              <Icon className="h-5 w-5" />
            </div>
            <div className="text-sm font-semibold text-slate-500">{label}</div>
            <div className="mt-1 text-3xl font-black text-slate-950">{statsLoading ? "..." : value}</div>
          </div>
        ))}
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <FileWarning className="h-5 w-5 text-red-600" />
            风险队列
          </h2>
          {riskQueue.length > 0 ? (
            <div className="space-y-3">
              {riskQueue.map((risk) => (
                <div key={risk.id} className="grid grid-cols-[1fr_auto] items-start gap-4 rounded-2xl border border-slate-100 bg-white p-4 transition hover:border-red-200">
                  <div>
                    <h3 className="text-sm font-black text-slate-900">{risk.title}</h3>
                    <p className="mt-1 text-xs leading-5 text-slate-500">{risk.reason}</p>
                    <p className="mt-2 text-xs font-bold text-slate-400">{risk.course}</p>
                  </div>
                  <div className="flex flex-col items-end gap-5">
                    <span className={`rounded-full px-2 py-1 text-[11px] font-black ${
                      risk.level === "中风险" ? "bg-orange-50 text-orange-700" : "bg-slate-100 text-slate-600"
                    }`}>
                      {risk.level}
                    </span>
                    <button
                      onClick={() => navigate(`/admin/resources?course=${risk.courseId}&resource=${risk.id}`)}
                      className="cursor-pointer text-xs font-black text-blue-700 hover:text-blue-800"
                    >
                      查看详情
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-slate-200 px-4 py-12 text-center text-sm text-slate-400">
              当前没有待复核风险事项
            </div>
          )}
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <LockKeyhole className="h-5 w-5 text-slate-700" />
            治理规则
          </h2>
          <div className="space-y-3">
            {governanceRules.map(([name, value, desc]) => (
              <div key={name} className="rounded-2xl border border-slate-100 bg-slate-50/70 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div className="text-sm font-black text-slate-900">{name}</div>
                  <div className="shrink-0 rounded-full bg-white px-2 py-1 text-xs font-black text-blue-700 ring-1 ring-blue-100">{value}</div>
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
              {["生成前约束", "输出后检测", "人工复核"].map((step) => (
                <span key={step} className="rounded-lg bg-white py-2 ring-1 ring-blue-100">{step}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="edu-card rounded-2xl p-6">
        <h2 className="mb-4 text-lg font-black text-slate-950">治理运行记录</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {governanceActions.map(([title, desc]) => (
            <div key={title} className="rounded-2xl border border-slate-100 bg-white p-4">
              <CheckCircle2 className="mb-3 h-5 w-5 text-emerald-600" />
              <h3 className="text-sm font-black text-slate-900">{title}</h3>
              <p className="mt-2 text-xs leading-5 text-slate-500">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <ModalShell title="更新治理规则" open={editorOpen} onClose={() => !saving && setEditorOpen(false)}>
        <div className="space-y-5">
          {[
            {
              key: "fact_consistency_threshold" as const,
              label: "事实一致性阈值",
              description: "低于该评分的生成内容自动进入人工复核。",
            },
            {
              key: "citation_coverage_threshold" as const,
              label: "引用覆盖率阈值",
              description: "要求生成内容中可追溯引用的最低覆盖比例。",
            },
          ].map((field) => (
            <label key={field.key} className="block rounded-2xl border border-slate-100 bg-slate-50/70 p-4">
              <span className="flex items-center justify-between gap-4 text-sm font-black text-slate-900">
                {field.label}
                <span className="tabular-nums text-blue-700">{form[field.key]}%</span>
              </span>
              <span className="mt-1 block text-xs leading-5 text-slate-500">{field.description}</span>
              <input
                type="range"
                min="0"
                max="100"
                value={form[field.key]}
                onChange={(event) => setThreshold(field.key, Number(event.target.value))}
                className="mt-4 h-2 w-full cursor-pointer accent-blue-600"
              />
            </label>
          ))}

          <label className="block rounded-2xl border border-slate-100 bg-slate-50/70 p-4 text-sm font-black text-slate-900">
            每账号每小时调用上限
            <span className="mt-1 block text-xs font-medium leading-5 text-slate-500">
              超过上限的调用将被拦截并写入审计日志。
            </span>
            <div className="mt-3 flex items-center gap-3">
              <input
                type="number"
                min="1"
                max="10000"
                value={form.hourly_call_limit}
                onChange={(event) => setForm((current) => ({
                  ...current,
                  hourly_call_limit: Math.min(10000, Math.max(1, Number(event.target.value) || 1)),
                }))}
                className="edu-focus-ring h-11 w-32 rounded-xl border border-slate-200 bg-white px-3 tabular-nums"
              />
              <span className="text-sm font-semibold text-slate-500">次 / 小时</span>
            </div>
          </label>

          <div className="flex items-center justify-between gap-4 rounded-2xl border border-slate-100 bg-slate-50/70 p-4">
            <div>
              <div className="text-sm font-black text-slate-900">敏感内容检测</div>
              <p className="mt-1 text-xs leading-5 text-slate-500">在模型输出前后执行敏感信息扫描。</p>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={form.sensitive_content_enabled}
              onClick={() => setForm((current) => ({
                ...current,
                sensitive_content_enabled: !current.sensitive_content_enabled,
              }))}
              className={`relative h-7 w-12 shrink-0 cursor-pointer rounded-full transition ${
                form.sensitive_content_enabled ? "bg-blue-600" : "bg-slate-300"
              }`}
            >
              <span className={`absolute top-1 h-5 w-5 rounded-full bg-white shadow-sm transition ${
                form.sensitive_content_enabled ? "left-6" : "left-1"
              }`} />
            </button>
          </div>
        </div>

        <div className="mt-6 flex flex-col justify-end gap-3 sm:flex-row">
          <button
            type="button"
            onClick={() => setEditorOpen(false)}
            disabled={saving}
            className={`${secondaryButton} cursor-pointer disabled:cursor-not-allowed disabled:opacity-60`}
          >
            取消
          </button>
          <button
            type="button"
            onClick={saveGovernance}
            disabled={saving}
            className={`${primaryButton} cursor-pointer disabled:cursor-wait disabled:opacity-60`}
          >
            {saving ? "正在保存..." : "保存规则"}
          </button>
        </div>
      </ModalShell>
    </div>
  );
}
