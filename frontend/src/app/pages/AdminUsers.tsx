import React from "react";
import { KeyRound, Plus, Save, ShieldCheck, UserCog, Users } from "lucide-react";
import { users } from "../data/demoData";
import { DetailDrawer, ModalShell, PageHeader, PageShell, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "../components/common/ProductUI";

export function AdminUsers() {
  const [query, setQuery] = React.useState("");
  const [role, setRole] = React.useState("全部");
  const [status, setStatus] = React.useState("全部");
  const [rows, setRows] = React.useState(users);
  const [selected, setSelected] = React.useState<(typeof users)[number] | null>(null);
  const [open, setOpen] = React.useState(false);
  const { toast, showToast } = useInlineToast();

  const filtered = rows.filter((user) => (role === "全部" || user.role === role) && (status === "全部" || user.status === status) && `${user.name}${user.username}${user.department}`.toLowerCase().includes(query.toLowerCase()));

  const toggleStatus = (id: string) => {
    setRows((current) => current.map((user) => user.id === id ? { ...user, status: user.status === "启用" ? "停用" : "启用" } : user));
    showToast("账号状态已更新");
  };

  const addUser = () => {
    setRows((current) => [{ id: `u-${Date.now()}`, name: "新用户", username: "new_user", role: "学生", department: "计算机学院", course: "数据库系统原理与 Web 项目实践", lastLogin: "尚未登录", status: "启用" }, ...current]);
    setOpen(false);
    showToast("新增用户已保存");
  };

  const stats = [
    { label: "用户总数", value: `${rows.length}`, hint: "全平台", icon: Users, tone: "blue" as const },
    { label: "学生数", value: `${rows.filter((u) => u.role === "学生").length}`, hint: "学习端", icon: Users, tone: "cyan" as const },
    { label: "教师数", value: `${rows.filter((u) => u.role === "教师").length}`, hint: "教学端", icon: ShieldCheck, tone: "purple" as const },
    { label: "管理员数", value: `${rows.filter((u) => u.role === "管理员").length}`, hint: "治理端", icon: UserCog, tone: "emerald" as const },
    { label: "今日新增", value: "5", hint: "含导入账号", icon: Plus, tone: "orange" as const },
    { label: "禁用账号", value: `${rows.filter((u) => u.status === "停用").length}`, hint: "需复核", icon: KeyRound, tone: "red" as const },
  ];

  return (
    <PageShell>
      <PageHeader eyebrow="Admin Users" title="用户管理" description="管理学生、教师和管理员账号，维护角色权限和账号状态。" icon={Users} action={<button onClick={() => setOpen(true)} className={primaryButton}><Plus className="h-4 w-4" />新增用户</button>} />
      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6 xl:gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-wrap items-end gap-4">
          <SearchInput label="搜索用户、用户名或院系" value={query} onChange={setQuery} />
          <SegmentedControl value={role} options={["全部", "学生", "教师", "管理员"]} onChange={setRole} />
          <SegmentedControl value={status} options={["全部", "启用", "停用"]} onChange={setStatus} />
        </div>
      </section>
      <section className="edu-card overflow-hidden rounded-2xl">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs font-black text-slate-500">
            <tr>{["姓名", "用户名", "角色", "所属院系", "关联课程", "最近登录", "状态", "操作"].map((h) => <th key={h} className="px-4 py-3">{h}</th>)}</tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map((user) => (
              <tr key={user.id} className="bg-white hover:bg-blue-50/40">
                <td className="px-4 py-4 font-black text-slate-900">{user.name}</td>
                <td className="px-4 py-4 font-mono text-xs font-bold text-slate-500">{user.username}</td>
                <td className="px-4 py-4">{user.role}</td>
                <td className="px-4 py-4">{user.department}</td>
                <td className="max-w-[260px] truncate px-4 py-4">{user.course}</td>
                <td className="px-4 py-4 text-slate-500">{user.lastLogin}</td>
                <td className="px-4 py-4"><StatusBadge status={user.status} /></td>
                <td className="px-4 py-4">
                  <div className="flex gap-2">
                    <button onClick={() => setSelected(user)} className="text-xs font-black text-blue-700">编辑</button>
                    <button onClick={() => toggleStatus(user.id)} className="text-xs font-black text-orange-700">{user.status === "启用" ? "停用" : "启用"}</button>
                    <button onClick={() => showToast(`已为 ${user.name} 生成重置密码链接`)} className="text-xs font-black text-slate-600">重置密码</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      {selected && <DetailDrawer title={selected.name} subtitle={`${selected.role} / ${selected.department}`} open={!!selected} onClose={() => setSelected(null)}>
        <div className="space-y-4">
          {["姓名", "用户名", "角色", "所属院系", "关联课程", "最近登录"].map((label) => (
            <label key={label} className="block text-sm font-bold text-slate-700">
              {label}
              <input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-700" defaultValue={(selected as Record<string, string>)[label === "所属院系" ? "department" : label === "关联课程" ? "course" : label === "用户名" ? "username" : label === "最近登录" ? "lastLogin" : label === "角色" ? "role" : "name"]} />
            </label>
          ))}
          <button onClick={() => showToast("用户资料已保存")} className={primaryButton}><Save className="h-4 w-4" />保存修改</button>
        </div>
      </DetailDrawer>}
      <ModalShell title="新增用户" open={open} onClose={() => setOpen(false)}>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {["姓名", "用户名", "角色", "所属院系"].map((label) => <label key={label} className="text-sm font-bold text-slate-700">{label}<input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" /></label>)}
        </div>
        <div className="mt-5 flex justify-end gap-3"><button onClick={() => setOpen(false)} className={secondaryButton}>取消</button><button onClick={addUser} className={primaryButton}>保存用户</button></div>
      </ModalShell>
      {toast}
    </PageShell>
  );
}
