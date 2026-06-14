import React from "react";
import { Bot, CheckCircle2, GraduationCap, LockKeyhole, ShieldCheck, UserCog, Users } from "lucide-react";

const PERMISSIONS = [
  {
    role: "学生 Student",
    tone: "blue",
    icon: GraduationCap,
    visible: ["我的学习首页", "我的画像", "学习路径", "学习任务", "推荐资源", "AI 学习辅导", "测评与反馈", "学习报告"],
    hidden: ["用户管理", "系统模型成本", "全平台调用审计", "教师审核中心", "其他学生详细数据", "管理员配置项"],
    principle: "陪伴感、路径感、学习目标清晰。",
  },
  {
    role: "教师 Teacher",
    tone: "purple",
    icon: Users,
    visible: ["教学工作台", "我的课程", "学生画像", "智能体工作台", "学习资源库", "审核中心", "学习任务", "课程知识库", "教学分析"],
    hidden: ["系统用户管理", "全平台模型密钥", "全局成本", "管理员系统设置"],
    principle: "效率感、班级洞察、资源审核和教学决策。",
  },
  {
    role: "管理员 Admin",
    tone: "slate",
    icon: UserCog,
    visible: ["系统总览", "用户管理", "角色权限", "课程管理", "资源管理", "模型配置", "智能体配置", "提示词模板", "调用审计", "成本统计", "内容安全", "操作日志"],
    hidden: ["学生个人学习任务入口", "教师单课默认工作流", "无权限课程详情"],
    principle: "治理感、稳定性、成本、安全和系统监控。",
  },
];

const toneClass: Record<string, string> = {
  blue: "bg-blue-50 text-blue-700 ring-blue-100",
  purple: "bg-purple-50 text-purple-700 ring-purple-100",
  slate: "bg-slate-100 text-slate-800 ring-slate-200",
};

export function RolePermissionMap() {
  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <section className="edu-card relative overflow-hidden rounded-[24px] p-7">
        <div className="absolute inset-0 edu-grid-bg opacity-45" />
        <div className="relative">
          <div className="mb-4 flex w-fit items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-bold text-slate-700">
            <LockKeyhole className="h-3.5 w-3.5" />
            Role Permission Map
          </div>
          <h1 className="text-2xl font-black text-slate-950">角色与菜单权限说明</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            V2 产品改版以角色工作台为入口，学生、教师、管理员只看到各自任务相关菜单和数据，降低信息过载和误操作风险。
          </p>
        </div>
      </section>

      <section className="grid grid-cols-3 gap-6">
        {PERMISSIONS.map((group) => {
          const Icon = group.icon;
          return (
            <div key={group.role} className="edu-card rounded-2xl p-6">
              <div className={`mb-4 grid h-12 w-12 place-items-center rounded-2xl ring-1 ${toneClass[group.tone]}`}>
                <Icon className="h-6 w-6" />
              </div>
              <h2 className="text-lg font-black text-slate-950">{group.role}</h2>
              <p className="mt-2 rounded-xl bg-slate-50 p-3 text-sm font-bold leading-6 text-slate-600">{group.principle}</p>

              <div className="mt-5">
                <h3 className="mb-3 flex items-center gap-2 text-sm font-black text-emerald-700">
                  <CheckCircle2 className="h-4 w-4" />
                  可见菜单
                </h3>
                <div className="flex flex-wrap gap-2">
                  {group.visible.map((item) => (
                    <span key={item} className="rounded-lg bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-700 ring-1 ring-emerald-100">
                      {item}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-5">
                <h3 className="mb-3 flex items-center gap-2 text-sm font-black text-slate-700">
                  <ShieldCheck className="h-4 w-4" />
                  不默认展示
                </h3>
                <div className="space-y-2">
                  {group.hidden.map((item) => (
                    <div key={item} className="rounded-lg border border-slate-100 bg-white px-3 py-2 text-xs font-semibold text-slate-500">
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </section>

      <section className="edu-card rounded-2xl p-6">
        <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
          <Bot className="h-5 w-5 text-blue-700" />
          产品主张
        </h2>
        <div className="grid grid-cols-4 gap-4">
          {[
            ["角色清晰", "不同首页、不同菜单、不同任务路径。"],
            ["流程完整", "画像—诊断—规划—生成—审核—学习—反馈—优化。"],
            ["可信可控", "证据追溯、教师复核、模型调用审计。"],
            ["长期可用", "每天登录后都有明确待办和主操作。"],
          ].map(([title, desc]) => (
            <div key={title} className="rounded-2xl border border-slate-100 bg-slate-50/70 p-4">
              <h3 className="text-sm font-black text-slate-900">{title}</h3>
              <p className="mt-2 text-xs leading-5 text-slate-500">{desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
