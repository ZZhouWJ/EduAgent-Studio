const RESOURCE_TYPE_LABELS: Record<string, string> = {
  lecture: "课程讲义",
  mindmap: "思维导图",
  quiz: "练习题",
  case: "案例材料",
  code_case: "代码实操",
  ppt: "PPT 大纲",
  video_script: "视频脚本",
  experiment_report: "实验报告",
  error_analysis: "错题解析",
  learning_card: "学习卡片",
  review: "复习计划",
  test: "阶段测验",
  other: "其他资源",
};

const TASK_TYPE_LABELS: Record<string, string> = {
  exercise: "练习任务",
  quiz: "测验任务",
  project: "项目任务",
  lecture: "课程学习",
  review: "复习任务",
  task: "学习任务",
};

export function resourceTypeLabel(value?: string | null) {
  const normalized = value?.trim() ?? "";
  if (!normalized) return "学习资源";
  return RESOURCE_TYPE_LABELS[normalized.toLowerCase()] ?? normalized;
}

export function taskTypeLabel(value?: string | null) {
  const normalized = value?.trim() ?? "";
  if (!normalized) return "学习任务";
  return TASK_TYPE_LABELS[normalized.toLowerCase()] ?? normalized;
}
