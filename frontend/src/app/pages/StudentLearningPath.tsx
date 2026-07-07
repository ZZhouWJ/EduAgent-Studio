import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, BookOpenCheck, Clock3, Code2, Network, Route, Target } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi } from "@/lib/api/learning";
import { profilesApi } from "@/lib/api/profiles";
import { LearningPathGraph, KpNode } from "@/app/components/learning/LearningPathGraph";

const stateClass: Record<string, string> = {
  done: "border-emerald-200 bg-emerald-50 text-emerald-700",
  warn: "border-yellow-200 bg-yellow-50 text-yellow-700",
  weak: "border-red-200 bg-red-50 text-red-700",
  current: "border-blue-300 bg-blue-600 text-white shadow-[0_14px_30px_rgba(37,99,235,0.22)]",
  next: "border-slate-200 bg-white text-slate-600",
};

export function StudentLearningPath() {
  const navigate = useNavigate();
  const { data: coursesData } = useApi(() => learningApi.listCourses(), []);
  const courseId = coursesData?.[0]?.id;
  const { data: pathData, loading } = useApi(
    () => (courseId ? learningApi.getLearningPath(courseId) : Promise.resolve(null)),
    [courseId]
  );

  // 转换为图谱组件需要的格式
  const knowledgePoints: KpNode[] = React.useMemo(() => {
    if (!pathData?.nodes) return [];
    return pathData.nodes.map((node) => ({
      kp_id: node.kp_id,
      kp_name: node.kp_name || node.name,
      mastery: (node.mastery_level ?? 0) / 100,
      difficulty_level: node.difficulty_level,
      description: node.description,
      dependencies: pathData.edges
        .filter((e) => e.target === node.kp_id)
        .map((e) => e.source),
    }));
  }, [pathData]);

  const currentRecommendKpId = React.useMemo(() => {
    if (!pathData?.nodes) return undefined;
    const currentNode = pathData.nodes.find((n) => n.status_label === "当前学习点");
    return currentNode?.kp_id;
  }, [pathData]);

  // 今日学习顺序列表
  const todayPath = React.useMemo(() => {
    if (!pathData?.nodes) return [];
    return pathData.nodes
      .filter((n) => n.status_label === "当前学习点" || n.status_label === "薄弱点" || n.status_label === "待学习")
      .slice(0, 5)
      .map((node) => ({
        kp_id: node.kp_id,
        kp_name: node.kp_name || node.name,
        mastery: (node.mastery_level ?? 0) / 100,
        status_label: node.status_label,
      }));
  }, [pathData]);

  const handleNodeClick = React.useCallback(
    (kpId: number) => {
      // 跳转到资源页面，带kp_id参数
      navigate(`/student/resources?kp_id=${kpId}`);
    },
    [navigate]
  );

  // Mock 数据（当API无返回时）
  const displayNodes: KpNode[] = knowledgePoints.length > 0 ? knowledgePoints : [
    { kp_id: 1, kp_name: "关系模型", mastery: 0.9, description: "数据库基础概念" },
    { kp_id: 2, kp_name: "SQL 查询", mastery: 0.85, description: "SELECT/INSERT/UPDATE/DELETE" },
    { kp_id: 3, kp_name: "多表连接", mastery: 0.6, description: "INNER/LEFT/RIGHT JOIN" },
    { kp_id: 4, kp_name: "子查询", mastery: 0.78, description: "嵌套查询语法" },
    { kp_id: 5, kp_name: "事务", mastery: 0.35, description: "ACID特性与控制语句" },
    { kp_id: 6, kp_name: "并发控制", mastery: 0.42, description: "锁机制与隔离级别" },
    { kp_id: 7, kp_name: "事务隔离级别", mastery: 0.32, description: "读已提交/可重复读等" },
    { kp_id: 8, kp_name: "索引优化", mastery: 0.65, description: "B树/Hash索引与优化" },
    { kp_id: 9, kp_name: "Web数据库实践", mastery: 0.5, description: "FastAPI+PostgreSQL项目" },
  ];

  const displayTodayPath = todayPath.length > 0 ? todayPath : [
    { kp_id: 7, kp_name: "事务隔离级别基础理解", mastery: 0.32, status_label: "当前学习点" },
    { kp_id: 6, kp_name: "并发控制案例学习", mastery: 0.42, status_label: "薄弱点" },
    { kp_id: 5, kp_name: "事务", mastery: 0.35, status_label: "薄弱点" },
    { kp_id: 3, kp_name: "多表连接补强", mastery: 0.6, status_label: "待学习" },
    { kp_id: 8, kp_name: "索引优化", mastery: 0.65, status_label: "待学习" },
  ];

  const displayCurrentKpId = currentRecommendKpId ?? displayTodayPath[0]?.kp_id;

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

      <div className="space-y-4">
        {/* 图谱区 */}
        <div className="edu-card p-4">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Network className="h-5 w-5 text-blue-600" />
            知识图谱
          </h3>
          {loading ? (
            <div className="text-center py-8 text-slate-400">加载学习路径中...</div>
          ) : (
            <LearningPathGraph
              nodes={displayNodes}
              currentKpId={displayCurrentKpId}
              onNodeClick={handleNodeClick}
            />
          )}
        </div>

        {/* 今日学习顺序 */}
        <div className="edu-card p-4">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Target className="h-5 w-5 text-blue-600" />
            今日学习顺序
          </h3>
          <div className="space-y-2">
            {displayTodayPath.map((kp, i) => (
              <div
                key={kp.kp_id}
                className="flex items-center gap-3 p-3 rounded-xl border border-slate-100 hover:border-blue-200 hover:bg-blue-50/50 transition-colors cursor-pointer"
                onClick={() => handleNodeClick(kp.kp_id)}
              >
                <span className="w-7 h-7 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm font-bold">
                  {i + 1}
                </span>
                <span className="font-medium flex-1">{kp.kp_name}</span>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                  kp.mastery >= 0.75
                    ? 'bg-green-100 text-green-700'
                    : kp.mastery >= 0.5
                    ? 'bg-orange-100 text-orange-700'
                    : 'bg-red-100 text-red-700'
                }`}>
                  {Math.round(kp.mastery * 100)}%
                </span>
                <span className="text-xs text-slate-500">
                  {kp.status_label === "当前学习点"
                    ? "当前推荐"
                    : kp.status_label === "薄弱点"
                    ? "薄弱点"
                    : "待学习"}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
