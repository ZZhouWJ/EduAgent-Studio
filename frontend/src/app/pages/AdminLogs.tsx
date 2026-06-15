import React from "react";
import { ActivitySquare, Download, FileClock, LogIn, Settings2, ShieldAlert } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { logsApi, OperationLog, LoginLog } from "@/lib/api";
import { DetailDrawer, PageHeader, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, useInlineToast } from "@/components/common/ProductUI";

const logTabs = ["全部", "登录日志", "资源日志", "审核日志", "画像日志", "系统配置日志"];

function mapOpLog(l: OperationLog) {
  return {
    id: String(l.log_id),
    time: l.created_at ? new Date(l.created_at).toLocaleString("zh-CN") : "-",
    actor: l.real_name || l.username,
    role: "-",
    type: l.action_type,
    object: l.action_desc || l.target_type || "-",
    ip: l.ip_address ?? "-",
    result: "成功",
    risk: "低",
    raw: l,
  };
}

function mapLoginLog(l: LoginLog) {
  return {
    id: String(l.log_id),
    time: l.login_time ? new Date(l.login_time).toLocaleString("zh-CN") : "-",
    actor: l.real_name || l.username,
    role: "-",
    type: "登录",
    object: l.login_status === "success" ? "登录成功" : `登录失败: ${l.failure_reason ?? "未知"}`,
    ip: l.ip_address ?? "-",
    result: l.login_status === "success" ? "成功" : "失败",
    risk: l.login_status === "failed" ? "高" : "低",
    raw: l,
  };
}

export function AdminLogs() {
  const [query, setQuery] = React.useState("");
  const [type, setType] = React.useState("全部");
  const [risk, setRisk] = React.useState("全部");
  const [selected, setSelected] = React.useState<ReturnType<typeof mapOpLog> | null>(null);
  const { toast, showToast } = useInlineToast();

  const opLogsState = useApi(() => logsApi.operationLogs({ page: 1, page_size: 50 }), []);
  const loginLogsState = useApi(() => logsApi.loginLogs({ page: 1, page_size: 50 }), []);

  const opLogs = (opLogsState.data?.items ?? []).map(mapOpLog);
  const loginLogs = (loginLogsState.data?.items ?? []).map(mapLoginLog);

  const combinedLogs = type === "全部" || type === "登录日志"
    ? (type === "登录日志" ? loginLogs : [...loginLogs, ...opLogs])
    : opLogs.filter((l) => l.type === type);

  const filtered = combinedLogs.filter((log) => {
    const typeMatch = type === "全部" || (type === "登录日志" ? log.type === "登录" : log.type === type);
    const riskMatch = risk === "全部" || log.risk === risk;
    const keywordMatch = `${log.actor}${log.object}${log.ip}`.toLowerCase().includes(query.toLowerCase());
    return typeMatch && riskMatch && keywordMatch;
  });

  const stats = [
    { label: "操作日志", value: `${opLogsState.data?.total ?? "-"}`, hint: "持续写入", icon: FileClock, tone: "blue" as const },
    { label: "登录次数", value: `${loginLogsState.data?.total ?? "-"}`, hint: "含学生端", icon: LogIn, tone: "cyan" as const },
    { label: "资源操作", value: `${opLogs.filter((l) => l.type.includes("资源") || l.type.includes("生成")).length || "-"}`, hint: "生成与审核", icon: ActivitySquare, tone: "purple" as const },
    { label: "审核操作", value: `${opLogs.filter((l) => l.type.includes("审核")).length || "-"}`, hint: "教师复核", icon: ShieldAlert, tone: "emerald" as const },
    { label: "配置变更", value: `${opLogs.filter((l) => l.type.includes("配置")).length || "-"}`, hint: "模型与模板", icon: Settings2, tone: "orange" as const },
    { label: "异常操作", value: `${loginLogs.filter((l) => l.risk === "高").length || "-"}`, hint: "已拦截", icon: ShieldAlert, tone: "red" as const },
  ];

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader eyebrow="Operation Logs" title="操作日志" description="记录用户登录、资源生成、教师审核、画像更新和系统配置变更。" icon={FileClock} action={<button onClick={() => showToast("操作日志已导出为模拟文件")} className={primaryButton}><Download className="h-4 w-4" />导出日志</button>} />
      <section className="grid grid-cols-6 gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4">
        <div className="mb-4"><SegmentedControl value={type} options={logTabs} onChange={setType} /></div>
        <div className="flex flex-wrap items-end gap-4"><SearchInput label="搜索操作人、对象或 IP" value={query} onChange={setQuery} /><SegmentedControl value={risk} options={["全部", "低", "高"]} onChange={setRisk} /></div>
      </section>
      <section className="edu-card overflow-hidden rounded-2xl">
        {opLogsState.loading && loginLogsState.loading ? (
          <div className="flex items-center justify-center py-16"><div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" /></div>
        ) : filtered.length === 0 ? (
          <div className="flex items-center justify-center py-16 text-sm text-slate-400">暂无日志数据</div>
        ) : (
          <table className="w-full text-left text-sm"><thead className="bg-slate-50 text-xs font-black text-slate-500"><tr>{["时间", "操作人", "角色", "操作类型", "操作对象", "IP", "结果", "风险等级", "操作"].map((h) => <th key={h} className="px-4 py-3">{h}</th>)}</tr></thead><tbody className="divide-y divide-slate-100">{filtered.map((log) => <tr key={log.id} className="bg-white hover:bg-blue-50/40"><td className="px-4 py-4 font-mono text-xs">{log.time}</td><td className="px-4 py-4 font-black text-slate-900">{log.actor}</td><td className="px-4 py-4">{log.role}</td><td className="px-4 py-4">{log.type}</td><td className="max-w-[280px] truncate px-4 py-4">{log.object}</td><td className="px-4 py-4 font-mono text-xs">{log.ip}</td><td className="px-4 py-4">{log.result}</td><td className="px-4 py-4"><StatusBadge status={log.risk === "高" ? "高风险" : "低风险"} /></td><td className="px-4 py-4"><button onClick={() => setSelected(log)} className="text-xs font-black text-blue-700">详情</button></td></tr>)}</tbody></table>
        )}
      </section>
      {selected && <DetailDrawer title="日志详情" subtitle={`${selected.actor} / ${selected.type}`} open={!!selected} onClose={() => setSelected(null)}>
        {[
          ["操作对象", selected.object],
          ["来源 IP", selected.ip],
          ["执行结果", selected.result],
          ["风险等级", selected.risk],
          ["审计说明", "该日志已写入审计链路，可用于问题追踪、权限复核和安全治理。"],
        ].map(([title, desc]) => <div key={title} className="mb-3 rounded-2xl border border-slate-100 bg-white p-4"><h3 className="text-sm font-black text-slate-900">{title}</h3><p className="mt-2 text-sm leading-6 text-slate-600">{desc}</p></div>)}
      </DetailDrawer>}
      {toast}
    </div>
  );
}
