import React from "react";
import { BadgeCheck, Boxes, Component, LayoutPanelTop, Palette, Ruler, Type } from "lucide-react";

const COLORS = [
  ["Primary Blue", "#2563EB"],
  ["Agent Purple", "#7C3AED"],
  ["Success Green", "#10B981"],
  ["Warning Orange", "#F59E0B"],
  ["Danger Red", "#EF4444"],
  ["Info Cyan", "#06B6D4"],
  ["Page Background", "#F6F8FC"],
  ["Sidebar Background", "#0F172A"],
];

const TOKENS = [
  ["侧边栏宽度", "248px"],
  ["顶部栏高度", "64px"],
  ["页面 Padding", "24px"],
  ["卡片间距", "16 / 20 / 24px"],
  ["普通卡片圆角", "16px"],
  ["重点区域圆角", "24px"],
  ["按钮高度", "40 / 44px"],
  ["输入框高度", "40 / 44px"],
];

const COMPONENTS = [
  "Page Header",
  "Role Switch",
  "Stat Card",
  "Workflow Timeline",
  "Resource Card",
  "Agent Step Card",
  "Evidence Card",
  "Risk Queue Item",
  "Permission Badge",
  "Chart Card",
  "Empty State",
  "Review Panel",
];

export function DesignSystemUpdate() {
  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <section className="edu-card relative overflow-hidden rounded-[24px] p-7">
        <div className="absolute inset-0 edu-grid-bg opacity-45" />
        <div className="relative">
          <div className="mb-4 flex w-fit items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700">
            <Boxes className="h-3.5 w-3.5" />
            Design System Update
          </div>
          <h1 className="text-2xl font-black text-slate-950">V2 产品级设计系统更新</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            在 V1 蓝紫科技教育风格基础上，补充角色化信息架构、权限边界、长期使用工作流和组件复用规范。
          </p>
        </div>
      </section>

      <section className="grid grid-cols-[0.9fr_1.1fr] gap-6">
        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <Palette className="h-5 w-5 text-blue-700" />
            色彩 Token
          </h2>
          <div className="grid grid-cols-2 gap-3">
            {COLORS.map(([name, value]) => (
              <div key={name} className="flex items-center gap-3 rounded-xl border border-slate-100 bg-white p-3">
                <div className="h-9 w-9 rounded-xl ring-1 ring-slate-200" style={{ backgroundColor: value }} />
                <div>
                  <div className="text-sm font-black text-slate-900">{name}</div>
                  <div className="font-mono text-xs font-bold text-slate-400">{value}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <Ruler className="h-5 w-5 text-purple-700" />
            布局与尺寸
          </h2>
          <div className="grid grid-cols-2 gap-3">
            {TOKENS.map(([name, value]) => (
              <div key={name} className="rounded-xl border border-slate-100 bg-slate-50/70 p-4">
                <div className="text-xs font-bold text-slate-400">{name}</div>
                <div className="mt-1 text-lg font-black text-slate-900">{value}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-3 gap-6">
        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <Type className="h-5 w-5 text-slate-700" />
            字体层级
          </h2>
          <div className="space-y-4">
            <div>
              <div className="text-xs font-bold text-slate-400">页面大标题</div>
              <div className="mt-1 text-[28px] font-black leading-9 text-slate-950">28 / 36 · 700+</div>
            </div>
            <div>
              <div className="text-xs font-bold text-slate-400">卡片标题</div>
              <div className="mt-1 text-lg font-black text-slate-900">18 / 26 · 600+</div>
            </div>
            <div>
              <div className="text-xs font-bold text-slate-400">正文</div>
              <div className="mt-1 text-sm leading-6 text-slate-600">14 / 22 · 400</div>
            </div>
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <Component className="h-5 w-5 text-blue-700" />
            组件清单
          </h2>
          <div className="flex flex-wrap gap-2">
            {COMPONENTS.map((item) => (
              <span key={item} className="rounded-lg bg-blue-50 px-2.5 py-1 text-xs font-bold text-blue-700 ring-1 ring-blue-100">
                {item}
              </span>
            ))}
          </div>
        </div>

        <div className="edu-card rounded-2xl p-6">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
            <LayoutPanelTop className="h-5 w-5 text-emerald-700" />
            角色差异
          </h2>
          <div className="space-y-3">
            {[
              ["学生端", "路径感、陪伴感、学习目标清晰。"],
              ["教师端", "效率、审核、班级洞察和教学决策。"],
              ["管理端", "治理、稳定性、成本、安全和系统监控。"],
            ].map(([role, desc]) => (
              <div key={role} className="rounded-xl border border-slate-100 bg-white p-3">
                <div className="text-sm font-black text-slate-900">{role}</div>
                <div className="mt-1 text-xs leading-5 text-slate-500">{desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="edu-card rounded-2xl p-6">
        <h2 className="mb-5 flex items-center gap-2 text-lg font-black text-slate-950">
          <BadgeCheck className="h-5 w-5 text-emerald-700" />
          Cursor / Vue3 + Element Plus 还原标注
        </h2>
        <div className="grid grid-cols-5 gap-4">
          {[
            "Auto Layout 对应 flex/grid",
            "组件命名按角色与业务域",
            "同类卡片统一 padding 与 radius",
            "SVG 图标使用 Lucide 线性风格",
            "主操作按钮每页最多一个",
          ].map((item) => (
            <div key={item} className="rounded-2xl border border-slate-100 bg-slate-50 p-4 text-sm font-bold leading-6 text-slate-700">
              {item}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
