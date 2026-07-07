import React from "react";
import { Database, FileUp, GitBranch, Layers3, SearchCheck, AlertCircle } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi } from "@/lib/api";
import { DetailDrawer, PageHeader, PageShell, ProgressBar, SearchInput, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "../components/common/ProductUI";

export function TeacherKnowledgeBase() {
  const [query, setQuery] = React.useState("可重复读和串行化的区别");
  const [selected, setSelected] = React.useState<{ id: string; name: string; type: string; chunks: number; coverage: number; updatedAt: string; owner: string } | null>(null);
  const [tested, setTested] = React.useState(true);
  const [activePanel, setActivePanel] = React.useState<"documents" | "graph" | "search">("documents");
  const { toast, showToast } = useInlineToast();

  // TODO: 后端暂无真正的 RAG 知识库端点，用 learningApi.listCourses() 课程列表作为入口占位
  const { data: courseList, loading } = useApi(() => learningApi.listCourses(), []);

  const stats = [
    { label: "课程文档", value: String(courseList?.length ?? "—"), hint: "结构化解析", icon: FileUp, tone: "blue" as const },
    { label: "知识点", value: "16", hint: "含依赖关系", icon: GitBranch, tone: "purple" as const },
    { label: "知识片段", value: "128", hint: "可追溯引用", icon: Layers3, tone: "emerald" as const },
    { label: "最近检索", value: "42", hint: "今日", icon: SearchCheck, tone: "cyan" as const },
    { label: "引用覆盖率", value: "82%", hint: "高于阈值", icon: Database, tone: "orange" as const },
    { label: "待补充资料", value: "2", hint: "实验说明", icon: AlertCircle, tone: "red" as const },
  ];

  // TODO: 后端暂无知识文档端点，用课程列表做占位展示
  const knowledgeDocuments: Array<{ id: string; name: string; type: string; chunks: number; coverage: number; updatedAt: string; owner: string }> = (courseList ?? []).map((c) => ({
    id: String(c.id),
    name: c.name,
    type: "课程",
    chunks: c.knowledge_point_count,
    coverage: 80,
    updatedAt: "—",
    owner: c.teacher,
  }));

  const knowledgePoints: string[] = [];

  return (
    <PageShell>
      <PageHeader
        eyebrow="Course Knowledge Base"
        title="课程知识库"
        description="管理课程文档、知识点、知识片段和检索证据，为智能体生成资源提供可信依据。"
        icon={Database}
        action={<button onClick={() => showToast("已进入资料上传流程")} className={primaryButton}><FileUp className="h-4 w-4" />上传资料</button>}
      />

      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6 xl:gap-4">
        {stats.map((stat) => <StatCard key={stat.label} {...stat} />)}
      </section>

      <div className="grid grid-cols-3 gap-1 rounded-2xl bg-slate-100 p-1 lg:hidden">
        {[
          ["documents", "文档"],
          ["graph", "结构"],
          ["search", "检索"],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setActivePanel(key as typeof activePanel)}
            className={`min-h-11 rounded-xl text-sm font-black transition ${
              activePanel === key ? "bg-white text-blue-700 shadow-sm" : "text-slate-500"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <section className="grid min-h-0 grid-cols-1 gap-4 lg:min-h-[650px] lg:grid-cols-[0.82fr_1fr_0.9fr] lg:gap-6">
        <div className={`edu-card rounded-2xl p-5 ${activePanel === "documents" ? "block" : "hidden lg:block"}`}>
          <h2 className="mb-4 text-base font-black text-slate-950">课程文档列表</h2>
          <div className="custom-scrollbar max-h-[570px] space-y-3 overflow-y-auto pr-1">
            {knowledgeDocuments.map((doc) => (
              <button key={doc.id} onClick={() => setSelected(doc)} className={`w-full rounded-2xl border p-4 text-left transition ${selected?.id === doc.id ? "border-blue-200 bg-blue-50" : "border-slate-100 bg-white hover:border-blue-200"}`}>
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-sm font-black leading-5 text-slate-900">{doc.name}</h3>
                  <StatusBadge status={doc.coverage > 80 ? "正常" : "待补充"} />
                </div>
                <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
                  <span className="font-bold text-slate-500">{doc.type}</span>
                  <span className="font-bold text-slate-500">{doc.chunks} 片段</span>
                  <span className="font-black text-blue-700">{doc.coverage}%</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className={`edu-card rounded-2xl p-5 sm:p-6 ${activePanel === "graph" ? "block" : "hidden lg:block"}`}>
          <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-base font-black text-slate-950">知识点结构</h2>
            <button onClick={() => showToast("知识点编辑面板已打开")} className={secondaryButton}>编辑知识点</button>
          </div>
          <div className="relative rounded-[20px] border border-slate-100 bg-slate-50/70 p-4 sm:rounded-[24px] sm:p-6">
            <div className="absolute inset-0 edu-grid-bg opacity-50" />
            <div className="relative grid grid-cols-1 gap-3 sm:grid-cols-2">
              {knowledgePoints.map((point, index) => (
                <div key={point} className="rounded-2xl border border-slate-100 bg-white p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-[11px] font-black text-slate-400">0{index + 1}</span>
                    <span className="h-2 w-2 rounded-full bg-blue-500" />
                  </div>
                  <div className="text-sm font-black text-slate-900">{point}</div>
                  <div className="mt-3">
                    <ProgressBar value={68 + (index % 4) * 7} tone={index % 3 === 0 ? "orange" : "blue"} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className={`edu-card rounded-2xl p-5 ${activePanel === "search" ? "block" : "hidden lg:block"}`}>
          <h2 className="mb-4 text-base font-black text-slate-950">检索测试</h2>
          <SearchInput label="测试问题" value={query} onChange={setQuery} />
          <button onClick={() => { setTested(true); showToast("检索测试完成，已返回 3 条证据"); }} className={`${primaryButton} mt-4 w-full`}>运行检索测试</button>
          {tested && (
            <div className="mt-5 space-y-3">
              {knowledgeDocuments.slice(0, 3).map((doc, index) => (
                <div key={doc.id} className="rounded-2xl border border-slate-100 bg-white p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <h3 className="text-sm font-black text-slate-900">命中文档 {index + 1}</h3>
                    <span className="text-xs font-black text-blue-700">{doc.coverage}%</span>
                  </div>
                  <p className="text-xs leading-5 text-slate-500">{doc.name} 中包含隔离级别边界、示例事务和引用建议。</p>
                </div>
              ))}
              <div className="rounded-2xl border border-orange-100 bg-orange-50 p-4">
                <h3 className="text-sm font-black text-orange-900">风险提示</h3>
                <p className="mt-2 text-xs leading-5 text-orange-800">回答串行化性能影响时需引用课程 PPT 页码，避免泛化表述。</p>
              </div>
            </div>
          )}
        </div>
      </section>

      {selected && <DetailDrawer title={selected.name} subtitle={`${selected.owner} / ${selected.updatedAt}`} open={!!selected} onClose={() => setSelected(null)}>
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-3">
            <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs font-bold text-slate-400">类型</div><div className="mt-1 font-black text-slate-900">{selected.type}</div></div>
            <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs font-bold text-slate-400">片段</div><div className="mt-1 font-black text-slate-900">{selected.chunks}</div></div>
            <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs font-bold text-slate-400">覆盖率</div><div className="mt-1 font-black text-blue-700">{selected.coverage}%</div></div>
          </div>
          {["事务隔离级别定义", "银行转账并发异常", "MySQL 默认隔离级别", "案例判断题生成依据"].map((chunk) => (
            <div key={chunk} className="rounded-2xl border border-slate-100 bg-white p-4">
              <h3 className="text-sm font-black text-slate-900">{chunk}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-500">该知识片段可作为讲义生成、测评解析和 AI 学习辅导的引用依据。</p>
            </div>
          ))}
        </div>
      </DetailDrawer>}
      {toast}
    </PageShell>
  );
}
