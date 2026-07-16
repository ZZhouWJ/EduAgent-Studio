import React from "react";
import {
  BookOpenCheck,
  Check,
  GraduationCap,
  KeyRound,
  Layers3,
  LockKeyhole,
  ShieldCheck,
  Users,
} from "lucide-react";
import { Permission, Role, usersApi } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import {
  EmptyState,
  PageHeader,
  PageShell,
  SearchInput,
  SegmentedControl,
  StatCard,
  StatusBadge,
  secondaryButton,
} from "../components/common/ProductUI";

const ROLE_PRESENTATION: Record<string, {
  icon: React.ComponentType<{ className?: string }>;
  tone: string;
  iconTone: string;
}> = {
  student_member: {
    icon: GraduationCap,
    tone: "border-cyan-100 bg-cyan-50/50",
    iconTone: "bg-cyan-100 text-cyan-700",
  },
  teacher: {
    icon: BookOpenCheck,
    tone: "border-blue-100 bg-blue-50/50",
    iconTone: "bg-blue-100 text-blue-700",
  },
  admin: {
    icon: ShieldCheck,
    tone: "border-emerald-100 bg-emerald-50/50",
    iconTone: "bg-emerald-100 text-emerald-700",
  },
};

function roleUserCount(role: Role, users: Array<{ roles?: string[] }>) {
  return users.filter((user) => user.roles?.includes(role.role_code)).length;
}

function PermissionCard({
  permission,
  roleNames,
}: {
  permission: Permission;
  roleNames: Record<string, string>;
}) {
  return (
    <article className="edu-card edu-card-hover min-w-0 rounded-2xl p-4 sm:p-5">
      <div className="flex items-start gap-3">
        <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-slate-100 text-slate-700 ring-1 ring-slate-200">
          <KeyRound className="h-4.5 w-4.5" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-black text-slate-900">{permission.permission_name}</h3>
            <span className="rounded-lg bg-slate-100 px-2 py-1 font-mono text-[11px] font-bold text-slate-600">
              {permission.permission_code}
            </span>
          </div>
          <p className="mt-2 text-xs leading-5 text-slate-500">{permission.description || "—"}</p>
          <div className="mt-3 flex flex-wrap gap-2" aria-label="拥有该能力的角色">
            {permission.role_codes.map((roleCode) => (
              <span
                key={roleCode}
                className="inline-flex min-h-7 items-center gap-1.5 rounded-full bg-white px-2.5 text-[11px] font-black text-slate-700 ring-1 ring-slate-200"
              >
                <Check className="h-3 w-3 text-emerald-600" />
                {roleNames[roleCode] ?? roleCode}
              </span>
            ))}
          </div>
        </div>
      </div>
    </article>
  );
}

export function AdminRoles() {
  const [query, setQuery] = React.useState("");
  const [moduleFilter, setModuleFilter] = React.useState("全部");
  const rolesState = useApi(() => usersApi.listRoles(), []);
  const permissionsState = useApi(() => usersApi.listPermissions(), []);
  const usersState = useApi(() => usersApi.list({ page: 1, page_size: 500 }), []);

  const roles = rolesState.data ?? [];
  const permissions = permissionsState.data ?? [];
  const users = usersState.data?.items ?? [];
  const moduleLabels = Array.from(new Set(permissions.map((item) => item.module_label)));
  const moduleOptions = ["全部", ...moduleLabels];
  const roleNames = Object.fromEntries(roles.map((role) => [role.role_code, role.role_name]));
  const normalizedQuery = query.trim().toLowerCase();
  const filteredPermissions = permissions.filter((permission) => {
    const moduleMatch = moduleFilter === "全部" || permission.module_label === moduleFilter;
    const queryMatch = !normalizedQuery || [
      permission.permission_name,
      permission.permission_code,
      permission.description ?? "",
      permission.module_label,
    ].some((value) => value.toLowerCase().includes(normalizedQuery));
    return moduleMatch && queryMatch;
  });
  const hasError = rolesState.error || permissionsState.error || usersState.error;
  const loading = rolesState.loading || permissionsState.loading || usersState.loading;

  const retryAll = () => {
    rolesState.refetch();
    permissionsState.refetch();
    usersState.refetch();
  };

  return (
    <PageShell>
      <PageHeader
        eyebrow="访问控制"
        title="角色与权限"
        description="查看平台角色边界和实际产品能力。用户角色由管理员在用户管理页分配，个人账号不能自行提权。"
        icon={LockKeyhole}
      />

      <section className="grid grid-cols-2 gap-3 sm:grid-cols-4 xl:gap-4">
        <StatCard label="平台角色" value={loading ? "-" : String(roles.length)} hint="固定角色模型" icon={ShieldCheck} tone="emerald" />
        <StatCard label="能力项" value={loading ? "-" : String(permissions.length)} hint="与产品功能同步" icon={KeyRound} tone="blue" />
        <StatCard label="能力模块" value={loading ? "-" : String(moduleLabels.length)} hint="学习、教学与治理" icon={Layers3} tone="purple" />
        <StatCard label="已分配用户" value={loading ? "-" : String(users.length)} hint="账号与角色记录" icon={Users} tone="cyan" />
      </section>

      {hasError ? (
        <EmptyState
          title="角色权限加载失败"
          description="无法读取访问控制数据，请检查后端服务后重试。"
          action={<button className={secondaryButton} onClick={retryAll}>重新加载</button>}
        />
      ) : (
        <>
          <section aria-labelledby="role-overview-title">
            <div className="mb-3 flex items-end justify-between gap-4">
              <div>
                <h2 id="role-overview-title" className="text-lg font-black text-slate-950">角色边界</h2>
                <p className="mt-1 text-sm text-slate-500">三个角色互相隔离，权限遵循最小授权原则。</p>
              </div>
            </div>
            <div className="grid gap-4 lg:grid-cols-3">
              {roles.map((role) => {
                const presentation = ROLE_PRESENTATION[role.role_code] ?? ROLE_PRESENTATION.student_member;
                const Icon = presentation.icon;
                const capabilityCount = permissions.filter((permission) => permission.role_codes.includes(role.role_code)).length;
                return (
                  <article key={role.role_id} className={`rounded-2xl border p-5 ${presentation.tone}`}>
                    <div className="flex items-start justify-between gap-4">
                      <div className={`grid h-11 w-11 shrink-0 place-items-center rounded-xl ${presentation.iconTone}`}>
                        <Icon className="h-5 w-5" />
                      </div>
                      <StatusBadge status={role.status === "active" ? "启用" : "停用"} />
                    </div>
                    <h3 className="mt-4 text-lg font-black text-slate-950">{role.role_name}</h3>
                    <p className="mt-2 min-h-10 text-sm leading-5 text-slate-600">{role.description || "—"}</p>
                    <div className="mt-5 grid grid-cols-2 gap-3 border-t border-slate-200/70 pt-4">
                      <div>
                        <div className="text-xs font-bold text-slate-500">已分配用户</div>
                        <div className="mt-1 text-xl font-black tabular-nums text-slate-950">{roleUserCount(role, users)}</div>
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-500">能力数量</div>
                        <div className="mt-1 text-xl font-black tabular-nums text-slate-950">{capabilityCount}</div>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          </section>

          <section aria-labelledby="capability-title">
            <div className="mb-4 flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
              <div>
                <h2 id="capability-title" className="text-lg font-black text-slate-950">能力目录</h2>
                <p className="mt-1 text-sm text-slate-500">按模块检索每项能力及其授权角色。</p>
              </div>
              <div className="flex w-full flex-col gap-3 sm:flex-row xl:w-auto xl:min-w-[720px]">
                <SearchInput label="搜索能力名称、代码或说明" value={query} onChange={setQuery} />
                <SegmentedControl value={moduleFilter} options={moduleOptions} onChange={setModuleFilter} />
              </div>
            </div>

            {loading ? (
              <div className="grid gap-3 md:grid-cols-2">
                {Array.from({ length: 6 }).map((_, index) => (
                  <div key={index} className="h-36 animate-pulse rounded-2xl border border-slate-100 bg-slate-100" />
                ))}
              </div>
            ) : filteredPermissions.length === 0 ? (
              <EmptyState title="没有匹配的能力" description="调整搜索词或模块筛选后重试。" />
            ) : (
              <div className="grid gap-3 md:grid-cols-2">
                {filteredPermissions.map((permission) => (
                  <PermissionCard key={permission.permission_id} permission={permission} roleNames={roleNames} />
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </PageShell>
  );
}
