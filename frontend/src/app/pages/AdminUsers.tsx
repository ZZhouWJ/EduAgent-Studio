import React from "react";
import { KeyRound, Plus, Save, ShieldCheck, UserCog, Users } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { usersApi, User } from "@/lib/api";
import { DetailDrawer, ModalShell, PageHeader, PageShell, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, notify } from "../components/common/ProductUI";

function mapUser(u: User) {
  const roleMap: Record<string, string> = {
    admin: "管理员",
    teacher: "教师",
    student_member: "学生",
  };
  const primaryRole = u.roles?.[0] ?? "学生";
  return {
    id: String(u.user_id),
    name: u.real_name ?? u.username,
    username: u.username,
    role: roleMap[primaryRole] ?? primaryRole,
    department: u.email ?? "—",
    course: "—",
    lastLogin: u.last_login_at ? new Date(u.last_login_at).toLocaleString("zh-CN") : "尚未登录",
    status: u.status === "active" ? "启用" : "停用",
    rawStatus: u.status,
    raw: u,
  };
}

function RoleEditModal({ user, onClose, onSuccess }: {
  user: ReturnType<typeof mapUser>;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const rolesState = useApi(() => usersApi.listRoles(), []);
  const roles = rolesState.data ?? [];
  const [selectedRole, setSelectedRole] = React.useState(user.raw.roles?.[0] ?? "student_member");
  const [saving, setSaving] = React.useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const role = roles.find((r) => r.role_code === selectedRole);
      if (!role) {
        notify.warning("未找到对应角色");
        return;
      }
      await usersApi.updateRoles(Number(user.id), [role.role_id]);
      notify.success("角色已更新");
      onSuccess();
      onClose();
    } catch (e) {
      notify.error("更新失败：" + String(e));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl">
        <h3 className="mb-4 text-lg font-black text-slate-950">编辑角色</h3>
        <p className="mb-4 text-sm text-slate-500">为「{user.name}」分配角色</p>
        <div className="mb-5 space-y-2">
          {roles.map((r) => (
            <label key={r.role_id} className="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 p-3 transition hover:border-blue-200 has-[:checked]:border-blue-400 has-[:checked]:bg-blue-50">
              <input type="radio" name="edit-role" value={r.role_code} checked={selectedRole === r.role_code} onChange={() => setSelectedRole(r.role_code)} className="h-4 w-4 accent-blue-600" />
              <span className="text-sm font-bold text-slate-700">{r.role_name}</span>
            </label>
          ))}
        </div>
        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 cursor-pointer rounded-xl border border-slate-200 py-2.5 text-sm font-bold text-slate-600 transition hover:bg-slate-50">取消</button>
          <button onClick={handleSave} disabled={saving} className="flex min-h-11 flex-1 cursor-pointer items-center justify-center rounded-xl bg-blue-600 py-2.5 text-sm font-black text-white transition hover:bg-blue-700 disabled:opacity-60">
            {saving ? "保存中..." : "保存"}
          </button>
        </div>
      </div>
    </div>
  );
}

export function AdminUsers() {
  const [query, setQuery] = React.useState("");
  const [roleFilter, setRoleFilter] = React.useState("全部");
  const [statusFilter, setStatusFilter] = React.useState("全部");
  const [selected, setSelected] = React.useState<ReturnType<typeof mapUser> | null>(null);
  const [open, setOpen] = React.useState(false);
  const [roleEditUser, setRoleEditUser] = React.useState<ReturnType<typeof mapUser> | null>(null);
  const [newUsername, setNewUsername] = React.useState("");
  const [newRealName, setNewRealName] = React.useState("");
  const [newPassword, setNewPassword] = React.useState("");
  const [newRoleId, setNewRoleId] = React.useState<number | null>(null);
  const [creating, setCreating] = React.useState(false);

  const pageState = useApi(() => usersApi.list({ page: 1, page_size: 100, keyword: query || undefined }), [query]);
  const rolesState = useApi(() => usersApi.listRoles(), []);

  const rows = (pageState.data?.items ?? []).map(mapUser);
  const filtered = rows.filter((user) => {
    const roleMap: Record<string, string> = { "管理员": "admin", "教师": "teacher", "学生": "student_member" };
    const roleMatch = roleFilter === "全部" || (roleMap[roleFilter] && user.raw.roles?.[0] === roleMap[roleFilter]);
    const statusMatch = statusFilter === "全部" || user.status === statusFilter;
    const keywordMatch = `${user.name}${user.username}${user.department}`.toLowerCase().includes(query.toLowerCase());
    return roleMatch && statusMatch && keywordMatch;
  });

  const stats = [
    { label: "用户总数", value: `${pageState.data?.total ?? "-"}`, hint: "全平台", icon: Users, tone: "blue" as const },
    { label: "学生数", value: `${rows.filter((u) => u.raw.roles?.[0] === "student_member").length}`, hint: "学习端", icon: Users, tone: "cyan" as const },
    { label: "教师数", value: `${rows.filter((u) => u.raw.roles?.[0] === "teacher").length}`, hint: "教学端", icon: ShieldCheck, tone: "purple" as const },
    { label: "管理员数", value: `${rows.filter((u) => u.raw.roles?.[0] === "admin").length}`, hint: "治理端", icon: UserCog, tone: "emerald" as const },
    { label: "禁用账号", value: `${rows.filter((u) => u.status === "停用").length}`, hint: "需复核", icon: KeyRound, tone: "red" as const },
    { label: "启用账号", value: `${rows.filter((u) => u.status === "启用").length}`, hint: "正常", icon: ShieldCheck, tone: "blue" as const },
  ];

  const toggleStatus = async (userId: string, currentStatus: string) => {
    const newStatus = currentStatus === "active" ? "disabled" : "active";
    try {
      await usersApi.updateStatus(Number(userId), newStatus);
      notify.success(`账号已${newStatus === "active" ? "启用" : "停用"}`);
      pageState.refetch();
    } catch (e) {
      notify.error("操作失败：" + String(e));
    }
  };

  const handleAddUser = async () => {
    if (!newUsername.trim() || !newRealName.trim()) {
      notify.warning("请填写用户名和姓名");
      return;
    }
    if (newPassword.length < 8) {
      notify.warning("初始密码至少 8 位");
      return;
    }
    if (new TextEncoder().encode(newPassword).length > 72) {
      notify.warning("初始密码过长，请缩短后重试");
      return;
    }
    if (!newRoleId) {
      notify.warning("请选择角色");
      return;
    }
    setCreating(true);
    try {
      await usersApi.create({
        username: newUsername.trim(),
        password: newPassword,
        real_name: newRealName.trim(),
        role_ids: [newRoleId],
      });
      notify.success(`用户 ${newUsername.trim()} 已创建`);
      setNewUsername("");
      setNewRealName("");
      setNewPassword("");
      setNewRoleId(null);
      setOpen(false);
      pageState.refetch();
    } catch (e) {
      notify.error("创建失败：" + String(e));
    } finally {
      setCreating(false);
    }
  };

  return (
    <PageShell>
      <PageHeader title="用户管理" description="管理学生、教师和管理员账号，维护角色权限和账号状态。" icon={Users} action={<button onClick={() => setOpen(true)} className={`${primaryButton} cursor-pointer`}><Plus className="h-4 w-4" />新增用户</button>} />
      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6 xl:gap-4">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="edu-card rounded-2xl p-4">
        <div className="flex flex-wrap items-end gap-4">
          <SearchInput label="搜索用户、用户名或院系" value={query} onChange={setQuery} />
          <SegmentedControl value={roleFilter} options={["全部", "学生", "教师", "管理员"]} onChange={setRoleFilter} />
          <SegmentedControl value={statusFilter} options={["全部", "启用", "停用"]} onChange={setStatusFilter} />
        </div>
      </section>
      <section className="edu-card overflow-hidden rounded-2xl">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs font-black text-slate-500">
            <tr>{["姓名", "用户名", "角色", "所属院系", "关联课程", "最近登录", "状态", "操作"].map((h) => <th key={h} className="px-4 py-3">{h}</th>)}</tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {pageState.loading ? (
              <tr><td colSpan={8} className="px-4 py-12 text-center text-sm text-slate-400">加载中...</td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={8} className="px-4 py-12 text-center text-sm text-slate-400">暂无用户数据</td></tr>
            ) : (
              filtered.map((user) => (
                <tr key={user.id} className="cursor-pointer bg-white hover:bg-blue-50/40">
                  <td className="px-4 py-4 font-black text-slate-900">{user.name}</td>
                  <td className="px-4 py-4 font-mono text-xs font-bold text-slate-500">{user.username}</td>
                  <td className="px-4 py-4">{user.role}</td>
                  <td className="px-4 py-4">{user.department}</td>
                  <td className="max-w-[260px] truncate px-4 py-4">{user.course}</td>
                  <td className="px-4 py-4 text-slate-500">{user.lastLogin}</td>
                  <td className="px-4 py-4"><StatusBadge status={user.status} /></td>
                  <td className="px-4 py-4">
                    <div className="flex gap-2">
                      <button onClick={() => setSelected(user)} className="cursor-pointer text-xs font-black text-blue-700 hover:text-blue-800">查看</button>
                      <button onClick={() => setRoleEditUser(user)} className="cursor-pointer text-xs font-black text-purple-700 hover:text-purple-800">编辑角色</button>
                      <button onClick={() => toggleStatus(user.id, user.rawStatus)} className="cursor-pointer text-xs font-black text-orange-700 hover:text-orange-800">{user.status === "启用" ? "停用" : "启用"}</button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>

      {selected && (
        <DetailDrawer title={selected.name} subtitle={`${selected.role} / ${selected.department}`} open={!!selected} onClose={() => setSelected(null)}>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: "姓名", value: selected.name },
                { label: "用户名", value: selected.username },
                { label: "角色", value: selected.role },
                { label: "最近登录", value: selected.lastLogin },
              ].map(({ label, value }) => (
                <div key={label} className="rounded-xl bg-slate-50 p-3">
                  <div className="text-xs font-bold text-slate-400">{label}</div>
                  <div className="mt-1 text-sm font-black text-slate-900">{value}</div>
                </div>
              ))}
            </div>
          </div>
        </DetailDrawer>
      )}

      {roleEditUser && (
        <RoleEditModal
          user={roleEditUser}
          onClose={() => setRoleEditUser(null)}
          onSuccess={() => pageState.refetch()}
        />
      )}

      <ModalShell title="新增用户" open={open} onClose={() => setOpen(false)}>
        <div className="space-y-4">
          <label className="block text-sm font-bold text-slate-700">
            用户名
            <input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" value={newUsername} onChange={(e) => setNewUsername(e.target.value)} placeholder="输入用户名" />
          </label>
          <label className="block text-sm font-bold text-slate-700">
            姓名
            <input className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" value={newRealName} onChange={(e) => setNewRealName(e.target.value)} placeholder="输入真实姓名" />
          </label>
          <label className="block text-sm font-bold text-slate-700">
            初始密码
            <input type="password" autoComplete="new-password" minLength={8} maxLength={72} className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="至少 8 位" />
          </label>
          <label className="block text-sm font-bold text-slate-700">
            角色
            <select className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm" value={newRoleId ?? ""} onChange={(e) => setNewRoleId(Number(e.target.value) || null)}>
              <option value="">请选择角色</option>
              {(rolesState.data ?? []).map((role) => <option key={role.role_id} value={role.role_id}>{role.role_name}</option>)}
            </select>
          </label>
        </div>
        <div className="mt-5 flex justify-end gap-3">
          <button onClick={() => setOpen(false)} className={`${secondaryButton} cursor-pointer`}>取消</button>
          <button onClick={handleAddUser} disabled={creating} className={`${primaryButton} cursor-pointer disabled:opacity-60`}><Save className="h-4 w-4" />{creating ? "创建中..." : "创建用户"}</button>
        </div>
      </ModalShell>
    </PageShell>
  );
}
