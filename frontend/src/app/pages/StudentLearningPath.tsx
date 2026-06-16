import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, BookOpenCheck, CheckCircle2, CircleDot, Clock3, Code2, Network, Route, Target } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi } from "@/lib/api";

const stateClass: Record<string, string> = {
  done: "border-emerald-200 bg-emerald-50 text-emerald-700",
  warn: "border-yellow-200 bg-yellow-50 text-yellow-700",
  weak: "border-red-200 bg-red-50 text-red-700",
  current: "border-blue-300 bg-blue-600 text-white shadow-[0_14px_30px_rgba(37,99,235,0.22)]",
  next: "border-slate-200 bg-white text-slate-600",
};

export function StudentLearningPath() {
  const { data: coursesData } = useApi(() => learningApi.listCourses(), []);
  const courseId = coursesData?.[0]?.id;
  const { data: pathData, loading } = useApi(
    () => (courseId ? learningApi.getLearningPath(courseId) : Promise.resolve(null)),
    [courseId]
  );

  const pathNodes = React.useMemo(() => {
    return (pathData?.nodes ?? []).map((node) => ({
      name: node.kp_name || node.name,
      state: node.status_label === "已掌握" ? "done"
        : node.status_label === "薄弱点" ? "weak"
        : node.status_label === "当前学习点" ? "current"
        : node.mastery_level < 50 ? "weak"
        : node.mastery_level < 80 ? "warn"
        : "done",
    }));
  }, [pathData]);

  const pathSteps = React.useMemo(() => {
    return (pathData?.nodes ?? [])
      .filter((n) => n.status_label === "当前学习点" || n.status_label === "薄弱点" || n.status_label === "待学习")
      .slice(0, 4)
      .map((node) => ({
        title: node.kp_name || node.name,
        reason: node.description || "根据画像推荐",
        resource: node.kp_name ? `${node.kp_name}相关学习资源` : "推荐学习资源",
        time: node.estimated_hours ? `${node.estimated_hours} 小时` : "30 分钟",
        status: node.status_label === "当前学习点" ? "当前推荐" : node.status_label,
      }));
  }, [pathData]);

  const displayNodes = pathNodes.length > 0 ? pathNodes : [
    { name: "关系模型", state: "done" },
    { name: "SQL 查询", state: "done" },
    { name: "多表连接", state: "warn" },
    { name: "子查询", state: "done" },
    { name: "事务", state: "weak" },
    { name: "并发控制", state: "weak" },
    { name: "事务隔离级别", state: "current" },
    { name: "索引优化", state: "warn" },
    { name: "Web 数据库项目实践", state: "next" },
  ];

  const displaySteps = pathSteps.length > 0 ? pathSteps : [
    { title: "多表连接补强", reason: "先补齐事务案例中的查询依赖", resource: "SQL 多表连接分层练习题", time: "25 分钟", status: "进行中" },
    { title: "事务隔离级别基础理解", reason: "当前主要薄弱点，掌握度 32%", resource: "事务隔离级别图解讲义", time: "35 分钟", status: "当前推荐" },
    { title: "并发控制案例学习", reason: "通过银行转账案例理解脏读、幻读", resource: "银行转账并发动画脚本", time: "20 分钟", status: "待学习" },
    { title: "综合实验实践", reason: "将知识迁移到 Web 数据库项目", resource: "FastAPI + PostgreSQL 实操案例", time: "45 分钟", status: "待学习" },
  ];
  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <section className="flex items-start justify-between gap-6">
        <div>
          <div className="mb-2 flex w-fit items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700">
            <Route className="h-3.5 w-3.5" />
            个性化学习路径
          </div>
          <h1 className="text-2xl font-black text-slate-950">学习路径</h1>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-500">
            系统根据画像、测评和课程知识依赖，规划从薄弱点到项目实践的最短学习路径。
          </p>
        </div>
        <Link to="/student/resources" className="inline-flex h-11 items-center gap-2 rounded-xl bg-blue-600 px-5 text-sm font-black text-white shadow-[0_14px_30px_rgba(37,99,235,0.22)]">
          继续学习当前推荐资源
          <ArrowRight className="h-4 w-4" />
        </Link>
      </section>

      <section className="grid grid-cols-[1.35fr_0.85fr] gap-6">
        <div className="edu-card rounded-2xl p-6">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-black text-slate-950">知识点路径图谱</h2>
              <p className="mt-1 text-sm text-slate-500">颜色同时配合文字状态展示，避免只靠颜色表达。</p>
            </div>
            <Network className="h-5 w-5 text-slate-300" />
          </div>

          <div className="relative rounded-[24px] border border-slate-100 bg-slate-50/70 p-8">
            <div className="absolute inset-0 edu-grid-bg opacity-50" />
            {loading ? (
              <div className="text-center py-8 text-slate-400">加载学习路径中...</div>
            ) : (
              <>
                <div className="relative grid grid-cols-3 gap-5">
                  {displayNodes.map((node, index) => (
                    <div key={node.name} className="relative">
                      {index < displayNodes.length - 1 && index % 3 !== 2 && (
                        <div className="absolute left-full top-1/2 h-px w-5 bg-slate-200" />
                      )}
                      <div className={`rounded-2xl border p-4 ${stateClass[node.state]}`}>
                        <div className="mb-2 flex items-center justify-between">
                          <CircleDot className="h-4 w-4" />
                          <span className="text-[11px] font-black">0{index + 1}</span>
                        </div>
                        <div className="text-sm font-black">{node.name}</div>
                        <div className="mt-1 text-[11px] font-bold opacity-80">
                          {node.state === "done" ? "已掌握" : node.state === "warn" ? "待巩固" : node.state === "weak" ? "薄弱点" : node.state === "current" ? "当前学习点" : "后续实践"}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-5 grid grid-cols-4 gap-3">
                  {[
                    ["已掌握", "绿色"],
                    ["待巩固", "黄色"],
                    ["薄弱点", "红色"],
                    ["当前学习点", "蓝色"],
                  ].map(([label, color]) => (
                    <div key={label} className="rounded-xl border border-slate-100 bg-white p-3">
                      <div className="text-xs font-bold text-slate-400">{color}</div>
                      <div className="mt-1 text-sm font-black text-slate-800">{label}</div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <Target className="h-5 w-5 text-blue-600" />
            当前推荐路径
          </h2>
          <div className="space-y-4">
            {displaySteps.map((step, index) => (
              <div key={step.title} className="rounded-2xl border border-slate-100 bg-white p-4">
                <div className="mb-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="grid h-7 w-7 place-items-center rounded-lg bg-blue-50 text-xs font-black text-blue-700 ring-1 ring-blue-100">{index + 1}</span>
                    <h3 className="text-sm font-black text-slate-900">{step.title}</h3>
                  </div>
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-bold text-slate-600">{step.status}</span>
                </div>
                <p className="text-xs leading-5 text-slate-500">推荐原因：{step.reason}</p>
                <div className="mt-3 grid grid-cols-[1fr_auto] gap-3 rounded-xl bg-slate-50 p-3">
                  <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
                    {index === 3 ? <Code2 className="h-4 w-4 text-emerald-600" /> : <BookOpenCheck className="h-4 w-4 text-blue-600" />}
                    {step.resource}
                  </div>
                  <div className="flex items-center gap-1 text-xs font-bold text-slate-500">
                    <Clock3 className="h-3.5 w-3.5" />
                    {step.time}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
