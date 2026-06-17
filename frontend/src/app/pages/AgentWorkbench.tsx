import React from "react";
import {
  AlertCircle,
  ArrowRight,
  Bot,
  BrainCircuit,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  Database,
  Eye,
  FileText,
  Gauge,
  Layers3,
  Link2,
  Network,
  Play,
  RefreshCcw,
  RotateCcw,
  Route,
  Save,
  ScanSearch,
  Send,
  Settings2,
  ShieldCheck,
  Terminal,
} from "lucide-react";
import { useApi } from "@/lib/useApi";
import { agentsApi, learningApi, modelsApi } from "@/lib/api";
import { useInlineToast } from "../components/common/ProductUI";

const RESOURCE_TYPES = ["课程讲义", "思维导图", "分层练习题", "代码实操案例", "PPT 大纲", "视频/动画脚本"];

// TODO: 后端暂无多智能体执行链路端点，保持静态展示
const AGENT_STEPS = [
  {
    name: "班级诊断智能体",
    status: "已完成",
    summary: "识别数据库 22-1 班薄弱点为“事务隔离级别、多表连接、接口字段设计”。",
    icon: BrainCircuit,
    state: "done",
    evidence: "班级覆盖 128 人",
  },
  {
    name: "学生画像聚合智能体",
    status: "已完成",
    summary: "聚合 12 名重点学生的作业、测评和反馈记录，形成干预分组。",
    icon: Bot,
    state: "done",
    evidence: "画像置信度 88%",
  },
  {
    name: "知识定位智能体",
    status: "已完成",
    summary: "命中课程知识库 5 条证据，关联第 6 章事务与并发控制。",
    icon: ScanSearch,
    state: "done",
    evidence: "证据覆盖 82%",
  },
  {
    name: "路径规划智能体",
    status: "运行中",
    summary: "建议先发布基础图解讲义，再安排判断题测验，最后进入并发案例迁移。",
    icon: Route,
    state: "running",
    evidence: "生成中 64%",
  },
  {
    name: "资源生成智能体",
    status: "等待中",
    summary: "将生成讲义、题库、代码案例、PPT 大纲和视频脚本。",
    icon: Layers3,
    state: "waiting",
    evidence: "排队中",
  },
  {
    name: "测评生成智能体",
    status: "等待中",
    summary: "生成阶段测验、错因标签和答案解析。",
    icon: ClipboardCheck,
    state: "waiting",
    evidence: "排队中",
  },
  {
    name: "教师审核辅助智能体",
    status: "等待中",
    summary: "检查内容准确性、难度适配性和引用来源完整性。",
    icon: ShieldCheck,
    state: "waiting",
    evidence: "排队中",
  },
];

const EVIDENCE = [
  { title: "第 6 章：事务与并发控制", match: "92%" },
  { title: "实验 4：银行转账并发控制实验", match: "85%" },
  { title: "教师 PPT：事务隔离级别第 18-26 页", match: "81%" },
  { title: "课程案例：库存扣减一致性问题", match: "76%" },
];

const LOGS = [
  "班级诊断智能体正在分析数据库 22-1 班最近 3 次测评……",
  "学生画像聚合智能体已圈定 12 名重点学生。",
  "正在检索课程知识库：第 6 章 事务与并发控制。",
  "路径规划智能体正在构建知识依赖图谱。",
];

function stepClasses(state: string) {
  if (state === "done") {
    return {
      icon: "bg-emerald-50 text-emerald-700 ring-emerald-200",
      card: "border-emerald-100 bg-emerald-50/40",
      badge: "bg-emerald-100 text-emerald-700 ring-emerald-200",
    };
  }

  if (state === "running") {
    return {
      icon: "bg-blue-600 text-white ring-blue-200",
      card: "border-blue-200 bg-blue-50/60",
      badge: "bg-blue-100 text-blue-700 ring-blue-200",
    };
  }

  return {
    icon: "bg-slate-100 text-slate-400 ring-slate-200",
    card: "border-slate-100 bg-slate-50/70",
    badge: "bg-slate-100 text-slate-500 ring-slate-200",
  };
}

export function AgentWorkbench() {
  const { toast, showToast } = useInlineToast();
  const { data: courseList } = useApi(() => learningApi.listCourses(), []);
  const { data: modelData } = useApi(() => modelsApi.getModels({ status: "active" }), []);

  // TODO: agentsApi.generate() 需要课程ID、学生ID、知识点ID等参数，暂未接入表单状态

  const activeModel = modelData?.items?.[0]?.display_name ?? "讯飞星火";
  const defaultCourse = courseList?.[0]?.name ?? "数据库系统原理与 Web 项目实践";
  return (
    <div className="page-shell flex min-h-0 flex-col">
      <div className="flex shrink-0 flex-col items-stretch justify-between gap-4 lg:flex-row lg:items-start lg:gap-6">
        <div className="min-w-0">
          <div className="mb-2 flex w-fit items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-600">
            <Network className="h-3.5 w-3.5" />
            资源生成工作台
          </div>
          <h1 className="text-2xl font-semibold text-slate-900">资源生成工作台</h1>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-500">
            面向课程、班级和重点学生群体，组织班级诊断、画像聚合、知识定位、路径规划、资源生成、测评生成与教师审核辅助等环节协同工作。
          </p>
        </div>

        <div className="grid shrink-0 grid-cols-1 gap-2 text-sm sm:grid-cols-3 lg:max-w-[620px]">
          {[
            ["当前课程", defaultCourse],
            ["生成对象", "数据库 22-1 班 / 李明等 12 人"],
            ["模型模式", activeModel],
          ].map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm">
              <div className="text-[11px] font-bold text-slate-400">{label}</div>
              <div className="mt-1 max-w-[190px] truncate text-xs font-black text-slate-800">{value}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex min-h-0 flex-1 flex-col gap-4 xl:flex-row xl:gap-6">
        <aside className="custom-scrollbar w-full shrink-0 xl:w-[300px] xl:overflow-y-auto xl:pb-6">
          <div className="edu-card rounded-2xl p-5">
            <div className="mb-5 flex items-center justify-between border-b border-slate-100 pb-4">
              <div className="flex items-center gap-2">
                <Settings2 className="h-5 w-5 text-slate-700" />
                <h2 className="text-base font-semibold text-slate-900">生成上下文</h2>
              </div>
              <span className="rounded-full bg-slate-100 px-2 py-1 text-[11px] font-semibold text-slate-600">教师端</span>
            </div>

            <div className="space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-bold text-slate-700">选择课程</label>
                <select className="edu-focus-ring h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-700">
                  {courseList?.length ? (
                    courseList.map((c) => <option key={c.id}>{c.name}</option>)
                  ) : (
                    <option>数据库系统原理与 Web 项目实践</option>
                  )}
                </select>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-bold text-slate-700">班级 / 学生群体</label>
                <select className="edu-focus-ring h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-700">
                  <option>数据库 22-1 班 · 重点学生 12 人</option>
                  <option>数据库 22-2 班 · 全班巩固</option>
                  <option>项目实践组 · 冲刺训练</option>
                </select>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-bold text-slate-700">指定学生</label>
                <select className="edu-focus-ring h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-700">
                  <option>李明等 12 人 · 掌握度低于 50%</option>
                  <option>仅李明 · 掌握度 64%</option>
                  <option>不指定学生 · 按班级统一生成</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-bold text-slate-700">选择知识点</label>
                <div className="space-y-2">
                  {["事务隔离级别", "SQL 多表连接", "接口字段设计"].map((tag, index) => (
                    <label key={tag} className="flex min-h-10 cursor-pointer items-center gap-2 rounded-xl border border-blue-100 bg-blue-50/60 px-3">
                      <input type="checkbox" defaultChecked className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
                      <span className="flex-1 text-sm font-semibold text-slate-700">{tag}</span>
                      <span className="text-[11px] font-bold text-blue-700">{[32, 46, 61][index]}%</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-bold text-slate-700">资源类型</label>
                <div className="grid grid-cols-2 gap-2">
                  {RESOURCE_TYPES.map((type, index) => (
                    <button
                      key={type}
                      className={`min-h-10 rounded-xl border px-2 text-xs font-semibold transition ${
                        index === 0
                          ? "border-slate-300 bg-slate-100 text-slate-800"
                          : "border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50"
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-bold text-slate-700">难度</label>
                <div className="grid grid-cols-3 gap-2 rounded-2xl bg-slate-100 p-1">
                  {["基础", "标准", "进阶"].map((item, index) => (
                    <button
                      key={item}
                      className={`h-9 rounded-xl text-sm font-bold transition ${
                        index === 0 ? "bg-white text-blue-700 shadow-sm" : "text-slate-500 hover:text-slate-800"
                      }`}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-bold text-slate-700">生成目标</label>
                <textarea
                  className="edu-focus-ring h-24 w-full resize-none rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm leading-6 text-slate-700"
                  defaultValue="为事务隔离级别掌握度低于 50% 的学生生成基础图解讲义、分层练习题和案例资源。"
                />
              </div>

              <label className="flex min-h-10 cursor-pointer items-center gap-2 rounded-xl border border-emerald-100 bg-emerald-50/70 px-3">
                <input type="checkbox" defaultChecked className="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" />
                <span className="text-sm font-bold text-emerald-800">启用教师审核前置规则</span>
              </label>
            </div>

            <div className="mt-5 space-y-3 border-t border-slate-100 pt-5">
              <button
                onClick={() => {
                  showToast("生成已启动（API 接入待完成表单状态）");
                }}
                className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-slate-900 text-sm font-semibold text-white transition-colors hover:bg-slate-800"
              >
                <Play className="h-4 w-4" />
                启动生成
              </button>
              <button className="flex min-h-11 w-full items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white text-sm font-bold text-slate-600 transition hover:border-blue-200 hover:text-blue-700">
                <RotateCcw className="h-4 w-4" />
                重置配置
              </button>
            </div>
          </div>
        </aside>

        <section className="flex min-w-0 flex-1 flex-col gap-4">
          <div className="edu-card flex min-h-[540px] flex-col rounded-2xl p-5 xl:min-h-0 xl:flex-1">
            <div className="mb-5 flex flex-col items-start justify-between gap-3 border-b border-slate-100 pb-4 sm:flex-row sm:items-center">
              <div className="flex items-center gap-2">
                <Route className="h-5 w-5 text-slate-700" />
                <h2 className="text-base font-semibold text-slate-900">执行链路</h2>
              </div>
              <div className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                <span className="h-2 w-2 rounded-full bg-blue-600 animate-pulse" />
                运行中 4/7
              </div>
            </div>

            <div className="custom-scrollbar relative flex-1 space-y-3 overflow-y-auto pr-0 sm:pr-2">
              <div className="absolute bottom-4 left-[21px] top-2 w-px bg-slate-200" />
              {AGENT_STEPS.map((step, index) => {
                const Icon = step.icon;
                const cls = stepClasses(step.state);
                return (
                  <div key={step.name} className="relative flex gap-3">
                    <div className={`relative z-10 grid h-11 w-11 shrink-0 place-items-center rounded-2xl ring-1 ${cls.icon}`}>
                      <Icon className={step.state === "running" ? "h-5 w-5 animate-pulse" : "h-5 w-5"} />
                    </div>
                    <div className={`min-w-0 flex-1 rounded-2xl border p-4 ${cls.card}`}>
                      <div className="mb-2 flex items-center justify-between gap-3">
                        <div className="flex min-w-0 items-center gap-2">
                          <span className="text-[11px] font-black text-slate-400">0{index + 1}</span>
                          <h3 className="truncate text-sm font-black text-slate-900">{step.name}</h3>
                        </div>
                        <span className={`shrink-0 rounded-full px-2 py-1 text-[11px] font-black ring-1 ${cls.badge}`}>
                          {step.status}
                        </span>
                      </div>
                      <p className="text-sm leading-6 text-slate-600">{step.summary}</p>
                      <div className="mt-3 flex items-center gap-2 text-xs font-semibold text-slate-500">
                        {step.state === "done" ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> : step.state === "running" ? <Gauge className="h-3.5 w-3.5 text-blue-600" /> : <Clock3 className="h-3.5 w-3.5 text-slate-400" />}
                        {step.evidence}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="h-48 shrink-0 overflow-hidden rounded-2xl border border-slate-200 bg-slate-50">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 text-xs font-semibold text-slate-500">
              <span className="flex items-center gap-2">
                <Terminal className="h-3.5 w-3.5" />
                实时生成日志
              </span>
              <span className="rounded-full bg-slate-200 px-2 py-0.5 text-[11px] text-slate-600">实时</span>
            </div>
            <div className="custom-scrollbar h-[144px] overflow-y-auto p-4 font-mono text-[13px] leading-6">
              {LOGS.map((log, index) => (
                <div key={log} className={index === LOGS.length - 1 ? "flex items-center gap-2 text-slate-700" : "text-slate-500"}>
                  <span className={index === LOGS.length - 1 ? "text-slate-700" : "text-slate-400"}>{index === LOGS.length - 1 ? ">" : "·"}</span>
                  <span>{log}</span>
                  {index === LOGS.length - 1 && <span className="ml-1 h-4 w-1 animate-pulse bg-slate-400" />}
                </div>
              ))}
            </div>
          </div>
        </section>

        <aside className="custom-scrollbar flex w-full shrink-0 flex-col gap-4 xl:w-[380px] xl:overflow-y-auto xl:pb-6">
          <div className="edu-card rounded-2xl p-5">
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-slate-700" />
                <h2 className="text-base font-semibold text-slate-900">资源预览</h2>
              </div>
              <span className="rounded-full bg-slate-100 px-2 py-1 text-[11px] font-semibold text-slate-600">课程讲义</span>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <h3 className="text-lg font-semibold leading-6 text-slate-900">事务隔离级别图解讲义</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                面向数据库课程中事务隔离级别学习困难的学生，通过银行转账案例解释读未提交、读已提交、可重复读、串行化之间的区别。
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {["数据库 22-1 班", "12 名重点学生", "基础"].map((tag) => (
                  <span key={tag} className="rounded-lg bg-white px-2.5 py-1 text-xs font-bold text-slate-600 ring-1 ring-slate-100">
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-3">
              {[
                ["可信度评分", "86%", "text-emerald-700"],
                ["引用覆盖率", "82%", "text-blue-700"],
                ["风险等级", "低", "text-emerald-700"],
                ["教师复核", "建议", "text-orange-700"],
              ].map(([label, value, color]) => (
                <div key={label} className="rounded-xl border border-slate-100 bg-slate-50 p-3">
                  <div className="text-xs font-semibold text-slate-500">{label}</div>
                  <div className={`mt-1 text-xl font-black ${color}`}>{value}</div>
                </div>
              ))}
            </div>

            <div className="mt-4 rounded-2xl border border-orange-100 bg-orange-50 p-3">
              <div className="flex items-start gap-2">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-orange-600" />
                <p className="text-sm leading-5 text-orange-800">建议教师复核 MySQL 默认隔离级别说明，并增加一题脏读判断题。</p>
              </div>
            </div>
          </div>

          <div className="edu-card flex-1 rounded-2xl p-5">
            <div className="mb-4 flex items-center gap-2">
              <Database className="h-5 w-5 text-slate-700" />
              <h2 className="text-base font-black text-slate-950">证据来源</h2>
            </div>

            <div className="space-y-3">
              {EVIDENCE.map((item, index) => (
                <button key={item.title} className="flex w-full items-start gap-3 rounded-xl border border-slate-200 bg-white p-3 text-left transition hover:border-slate-300 hover:bg-slate-50">
                  <div className="grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-slate-100 text-xs font-semibold text-slate-700">
                    {index + 1}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-semibold leading-5 text-slate-800">{item.title}</div>
                    <div className="mt-1 flex items-center gap-1.5 text-xs text-slate-500">
                      <Link2 className="h-3 w-3" />
                      命中率 {item.match}
                    </div>
                  </div>
                  <ArrowRight className="mt-1 h-4 w-4 text-slate-300" />
                </button>
              ))}
            </div>

            <div className="mt-5 grid grid-cols-2 gap-2">
              <button className="flex min-h-11 items-center justify-center gap-2 rounded-xl bg-blue-600 text-sm font-bold text-white transition hover:bg-blue-700">
                <Save className="h-4 w-4" />
                保存资源
              </button>
              <button className="flex min-h-11 items-center justify-center gap-2 rounded-xl bg-orange-50 text-sm font-bold text-orange-700 ring-1 ring-orange-200 transition hover:bg-orange-100">
                <Send className="h-4 w-4" />
                提交审核
              </button>
              <button className="flex min-h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white text-sm font-bold text-slate-600 transition hover:border-blue-200 hover:text-blue-700">
                <RefreshCcw className="h-4 w-4" />
                重新生成
              </button>
              <button className="flex min-h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white text-sm font-bold text-slate-600 transition hover:border-blue-200 hover:text-blue-700">
                <Eye className="h-4 w-4" />
                完整内容
              </button>
            </div>
          </div>
        </aside>
      </div>
      {toast}
    </div>
  );
}
