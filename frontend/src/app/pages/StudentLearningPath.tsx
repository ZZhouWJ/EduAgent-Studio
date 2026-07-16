import React from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Network, Target } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { learningApi } from "@/lib/api/learning";
import { profilesApi } from "@/lib/api/profiles";
import { LearningPathGraph, KpNode } from "@/app/components/learning/LearningPathGraph";

export function StudentLearningPath() {
  const navigate = useNavigate();
  const { data: profileData } = useApi(() => profilesApi.getMyProfile(), []);
  const profileId = profileData?.profile_id;
  const courseId = profileData?.course_id;

  const { data: pathData, loading } = useApi(
    () => (profileId && courseId ? learningApi.getLearningPath(courseId, profileId) : Promise.resolve(null)),
    [profileId, courseId]
  );

  // 转换为列表格式
  const knowledgePoints: KpNode[] = React.useMemo(() => {
    if (!pathData?.nodes) return [];
    return pathData.nodes.map((node) => ({
      kp_id: node.kp_id,
      kp_name: node.kp_name || node.name,
      mastery: node.mastery_level ?? 0,
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
      .filter((n) => n.status_label === "当前学习点" || n.status_label === "薄弱" || n.status_label === "待学习")
      .slice(0, 5)
      .map((node) => ({
        kp_id: node.kp_id,
        kp_name: node.kp_name || node.name,
        mastery: (node.mastery_level ?? 0),
        status_label: node.status_label,
        difficulty: node.difficulty_level,
      }));
  }, [pathData]);

  const handleNodeClick = React.useCallback(
    (kpId: number) => {
      const point = knowledgePoints.find((item) => item.kp_id === kpId);
      const params = new URLSearchParams({ kp_id: String(kpId) });
      if (point?.kp_name) params.set("kp_name", point.kp_name);
      navigate(`/student/resources?${params.toString()}`);
    },
    [knowledgePoints, navigate]
  );

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
    { kp_id: 7, kp_name: "事务隔离级别基础理解", mastery: 0.32, status_label: "当前学习点", difficulty: "advanced" },
    { kp_id: 6, kp_name: "并发控制案例学习", mastery: 0.42, status_label: "薄弱", difficulty: "advanced" },
    { kp_id: 5, kp_name: "事务", mastery: 0.35, status_label: "薄弱", difficulty: "intermediate" },
    { kp_id: 3, kp_name: "多表连接补强", mastery: 0.6, status_label: "待学习", difficulty: "intermediate" },
    { kp_id: 8, kp_name: "索引优化", mastery: 0.65, status_label: "待学习", difficulty: "advanced" },
  ];

  const displayCurrentKpId = currentRecommendKpId ?? displayTodayPath[0]?.kp_id;

  // 颜色
  const masteryColor = (m: number) =>
    m >= 0.75 ? "text-emerald-600" : m >= 0.5 ? "text-orange-500" : "text-red-500";
  const masteryBg = (m: number) =>
    m >= 0.75 ? "bg-emerald-50 border-emerald-200" : m >= 0.5 ? "bg-orange-50 border-orange-200" : "bg-red-50 border-red-200";
  const statusBadge = (label: string) => {
    if (label === "当前学习点") return "bg-blue-100 text-blue-700";
    if (label === "薄弱") return "bg-red-100 text-red-600";
    return "bg-slate-100 text-slate-600";
  };
  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <div className="flex items-start justify-end gap-4">
        <button
          type="button"
          onClick={() => displayCurrentKpId && handleNodeClick(displayCurrentKpId)}
          disabled={!displayCurrentKpId}
          className="inline-flex h-11 items-center gap-2 rounded-xl bg-blue-600 px-5 text-sm font-black text-white shadow-[0_14px_30px_rgba(37,99,235,0.22)] disabled:cursor-not-allowed disabled:opacity-60"
        >
          继续学习当前推荐资源
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>

      {/* 知识图谱 */}
      <div className="edu-card p-4">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Network className="h-5 w-5 text-blue-600" />
          知识图谱
          {loading && <span className="ml-3 text-sm font-normal text-slate-400">加载中...</span>}
        </h3>
        {displayNodes.length === 0 && !loading ? (
          <div className="text-center py-12 text-slate-400">暂无知识点数据</div>
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
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${masteryBg(kp.mastery)} ${masteryColor(kp.mastery)}`}>
                {Math.round(kp.mastery * 100)}%
              </span>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${statusBadge(kp.status_label ?? "")}`}>
                {kp.status_label === "当前学习点" ? "当前推荐"
                  : kp.status_label === "薄弱" ? "薄弱点" : "待学习"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
