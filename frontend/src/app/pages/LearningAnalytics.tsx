import React from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, Tooltip, BarChart, Bar } from "recharts";
import { TrendingUp, Users, Target, BookOpen, PenTool, CheckCircle } from "lucide-react";

const PIE_DATA = [
  { name: '讲义', value: 400, color: '#3b82f6' },
  { name: '题库', value: 300, color: '#8b5cf6' },
  { name: '代码案例', value: 300, color: '#10b981' },
  { name: 'PPT大纲', value: 200, color: '#f59e0b' },
];

const LINE_DATA = [
  { name: 'Mon', calls: 240 }, { name: 'Tue', calls: 139 }, { name: 'Wed', calls: 980 },
  { name: 'Thu', calls: 390 }, { name: 'Fri', calls: 480 }, { name: 'Sat', calls: 380 }, { name: 'Sun', calls: 430 }
];

const BAR_DATA = [
  { name: '事务隔离', score: 38 },
  { name: '多表连接', score: 46 },
  { name: '数据库范式', score: 52 },
  { name: '索引优化', score: 55 },
  { name: '接口设计', score: 61 }
];

export function LearningAnalytics() {
  return (
    <div className="space-y-6 max-w-[1400px] mx-auto pb-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">学习分析看板</h1>
        <p className="text-slate-500 mt-1 text-sm">基于学生画像、资源使用、测评反馈和智能体调用数据分析学习效果。</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {[
          { label: "平均掌握度", val: "76%", icon: Target, c: "text-blue-600", bg: "bg-blue-50" },
          { label: "薄弱知识点数量", val: "18", icon: TrendingUp, c: "text-orange-600", bg: "bg-orange-50" },
          { label: "资源使用次数", val: "1,426", icon: BookOpen, c: "text-purple-600", bg: "bg-purple-50" },
          { label: "测验平均分", val: "72", icon: PenTool, c: "text-emerald-600", bg: "bg-emerald-50" },
          { label: "画像更新次数", val: "386", icon: Users, c: "text-indigo-600", bg: "bg-indigo-50" },
          { label: "审核通过率", val: "92%", icon: CheckCircle, c: "text-cyan-600", bg: "bg-cyan-50" }
        ].map((item, i) => {
          const Icon = item.icon;
          return (
            <div key={i} className="bg-white rounded-xl p-4 shadow-[0_4px_12px_rgba(15,23,42,0.03)] border border-slate-100 flex flex-col justify-center gap-3">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-lg ${item.bg} flex items-center justify-center shrink-0`}>
                  <Icon className={`w-4 h-4 ${item.c}`} />
                </div>
                <div className="text-xs font-medium text-slate-500">{item.label}</div>
              </div>
              <div className="text-2xl font-bold text-slate-900">{item.val}</div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 min-h-[360px] flex flex-col">
          <h3 className="text-base font-bold text-slate-900 mb-6">知识点学习路径图谱</h3>
          <div className="flex-1 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center p-8 relative overflow-hidden">
            {/* Abstract node graph representation */}
            <div className="absolute inset-0 opacity-30 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:20px_20px]"></div>
            
            <div className="relative z-10 w-full h-full flex flex-wrap items-center justify-center gap-6">
              {[
                { name: "关系模型", status: "ok" },
                { name: "SQL 查询", status: "ok" },
                { name: "多表连接", status: "warn" },
                { name: "事务", status: "danger" },
                { name: "并发控制", status: "danger" },
                { name: "事务隔离级别", status: "danger" },
                { name: "Web 项目", status: "ok" }
              ].map((node, i) => (
                <div key={i} className="flex items-center gap-4">
                  <div className={`px-4 py-2 rounded-lg font-bold text-sm shadow-sm border
                    ${node.status === 'ok' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                      node.status === 'warn' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                      'bg-red-50 text-red-700 border-red-200'
                    }`}
                  >
                    {node.name}
                  </div>
                  {i < 6 && <div className="w-8 h-0.5 bg-slate-300"></div>}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Weak spots bar chart */}
        <div className="bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100">
          <h3 className="text-base font-bold text-slate-900 mb-6">薄弱知识点 Top 5</h3>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={BAR_DATA} layout="vertical" margin={{ top: 0, right: 20, left: -20, bottom: 0 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} width={80} />
                <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                <Bar dataKey="score" fill="#ef4444" radius={[0, 4, 4, 0]} barSize={20}>
                  {BAR_DATA.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.score < 40 ? '#ef4444' : '#f59e0b'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100">
          <h3 className="text-base font-bold text-slate-900 mb-2">资源类型分布</h3>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={PIE_DATA} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {PIE_DATA.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100">
          <h3 className="text-base font-bold text-slate-900 mb-2">智能体调用趋势</h3>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={LINE_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94A3B8' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94A3B8' }} />
                <Tooltip />
                <Line type="monotone" dataKey="calls" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-[0_8px_24px_rgba(15,23,42,0.04)] border border-slate-100 flex flex-col justify-between">
          <h3 className="text-base font-bold text-slate-900 mb-4">教师审核质量</h3>
          <div className="space-y-4 flex-1">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-500">通过资源数</span>
                <span className="font-bold text-emerald-600">842</span>
              </div>
              <div className="w-full h-1.5 bg-slate-100 rounded-full"><div className="h-full bg-emerald-500 rounded-full w-[84%]"></div></div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-500">退回修改数</span>
                <span className="font-bold text-orange-600">64</span>
              </div>
              <div className="w-full h-1.5 bg-slate-100 rounded-full"><div className="h-full bg-orange-500 rounded-full w-[16%]"></div></div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-500">高风险资源</span>
                <span className="font-bold text-red-600">12</span>
              </div>
              <div className="w-full h-1.5 bg-slate-100 rounded-full"><div className="h-full bg-red-500 rounded-full w-[5%]"></div></div>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-100">
            <div className="text-xs text-slate-500 text-center">平均审核耗时 <span className="font-bold text-slate-800 text-sm ml-1">4.5 小时</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
