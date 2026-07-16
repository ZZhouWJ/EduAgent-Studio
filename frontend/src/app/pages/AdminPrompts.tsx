import React from "react";
import { Copy, FileText, History, Play, Plus, ScrollText } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { promptsApi, PromptRenderResult, PromptTaskType, PromptTemplate, PromptVersion } from "@/lib/api";
import { DetailDrawer, ModalShell, PageHeader, SearchInput, SegmentedControl, StatCard, StatusBadge, primaryButton, secondaryButton, notify } from "../components/common/ProductUI";

function mapTemplate(t: PromptTemplate) {
  return {
    id: String(t.template_id),
    name: t.template_name,
    agent: t.type_name,
    version: t.current_version_no ? `v${t.current_version_no}` : "未发布",
    enabled: t.is_active,
    updatedAt: t.updated_at ? new Date(t.updated_at).toLocaleString("zh-CN", { year: "numeric", month: "2-digit", day: "2-digit" }) : "-",
    raw: t,
  };
}

function mapVersion(v: PromptVersion) {
  return {
    id: String(v.prompt_version_id),
    no: `v${v.version_no}`,
    note: v.change_note ?? "-",
    active: v.is_active,
    createdAt: v.created_at ? new Date(v.created_at).toLocaleString("zh-CN", { year: "numeric", month: "2-digit", day: "2-digit" }) : "-",
    creator: v.creator_real_name ?? "-",
    raw: v,
  };
}

export function AdminPrompts() {
  const [query, setQuery] = React.useState("");
  const [taskTypeFilter, setTaskTypeFilter] = React.useState("全部");
  const [selected, setSelected] = React.useState<ReturnType<typeof mapTemplate> | null>(null);
  const [modalMode, setModalMode] = React.useState<"create" | "edit" | null>(null);
  const [historyOpen, setHistoryOpen] = React.useState(false);
  const [promptContent, setPromptContent] = React.useState("");
  const [changeNote, setChangeNote] = React.useState("");
  const [saving, setSaving] = React.useState(false);

  const [newTemplateName, setNewTemplateName] = React.useState("");
  const [newTaskTypeId, setNewTaskTypeId] = React.useState<number | "">("");
  const [creatingTemplate, setCreatingTemplate] = React.useState(false);
  const [previewOpen, setPreviewOpen] = React.useState(false);
  const [previewVersionId, setPreviewVersionId] = React.useState<number | null>(null);
  const [previewValues, setPreviewValues] = React.useState<Record<string, string>>({});
  const [previewResult, setPreviewResult] = React.useState<PromptRenderResult | null>(null);
  const [previewLoading, setPreviewLoading] = React.useState(false);
  const [previewError, setPreviewError] = React.useState("");

  const taskTypesState = useApi(() => promptsApi.getTaskTypes(), []);
  const templatesState = useApi(() => promptsApi.getTemplates({ page: 1, page_size: 100, keyword: query || undefined }), [query]);
  const templates = React.useMemo(
    () => (templatesState.data?.items ?? []).map(mapTemplate),
    [templatesState.data]
  );

  React.useEffect(() => {
    setSelected((current) => {
      if (templates.length === 0) return null;
      return templates.find((item) => item.id === current?.id) ?? templates[0];
    });
  }, [templates]);

  const versionsState = useApi(
    () => selected ? promptsApi.getVersions(Number(selected.id)) : Promise.resolve([] as PromptVersion[]),
    [selected?.id]
  );

  React.useEffect(() => {
    if (versionsState.data?.length && versionsState.data[0]?.prompt_content) {
      setPromptContent(versionsState.data[0].prompt_content);
    }
  }, [versionsState.data]);

  const taskTypeOptions = ["全部", ...Array.from(new Set(templates.map((t) => t.agent)))];
  const filtered = templates.filter((item) => {
    const typeMatch = taskTypeFilter === "全部" || item.agent === taskTypeFilter;
    const keywordMatch = `${item.name}${item.agent}${item.version}`.toLowerCase().includes(query.toLowerCase());
    return typeMatch && keywordMatch;
  });

  const selectedTemplate = selected ?? filtered[0] ?? null;
  const versions = (versionsState.data ?? []).map(mapVersion);
  const activeVersion = versions.find((v) => v.active) ?? versions[0];

  const stats = [
    { label: "模板总数", value: `${templatesState.data?.total ?? "-"}`, hint: "覆盖主流程", icon: FileText, tone: "blue" as const },
    { label: "已启用模板", value: `${templates.filter((p) => p.enabled).length}`, hint: "可被调用", icon: ScrollText, tone: "emerald" as const },
    { label: "最近更新", value: templates[0]?.updatedAt ?? "-", hint: "最新模板", icon: History, tone: "slate" as const },
    { label: "关联任务类型", value: `${taskTypeOptions.length - 1}`, hint: "覆盖范围", icon: Play, tone: "cyan" as const },
  ];

  const handleSelectTemplate = (t: ReturnType<typeof mapTemplate>) => {
    setSelected(t);
    setHistoryOpen(false);
    setPromptContent("");
    setChangeNote("");
    setPreviewOpen(false);
    setPreviewResult(null);
    setPreviewValues({});
  };

  const handleSaveVersion = async () => {
    if (!selected) return;
    setSaving(true);
    try {
      await promptsApi.createVersion(Number(selected.id), {
        prompt_content: promptContent,
        change_note: changeNote || "更新 Prompt 内容",
      });
      notify.success("版本已保存");
      versionsState.refetch();
      templatesState.refetch();
      setModalMode(null);
      setChangeNote("");
    } catch (e) {
      notify.error("保存失败：" + String(e));
    } finally {
      setSaving(false);
    }
  };

  const handleCopyTemplate = async () => {
    const content = activeVersion?.raw?.prompt_content ?? promptContent;
    try {
      await navigator.clipboard.writeText(content);
      notify.success("Prompt 内容已复制到剪贴板");
    } catch {
      notify.error("复制失败，请手动复制");
    }
  };

  const handleActivateVersion = async (templateId: string, versionId: string) => {
    try {
      await promptsApi.activateVersion(Number(templateId), Number(versionId));
      notify.success("版本已激活");
      versionsState.refetch();
      templatesState.refetch();
    } catch (e) {
      notify.error("激活失败：" + String(e));
    }
  };

  const handleCreateTemplate = async () => {
    if (!newTemplateName.trim() || !newTaskTypeId) {
      notify.warning("请填写模板名称并选择任务类型");
      return;
    }
    setCreatingTemplate(true);
    try {
      const created = await promptsApi.createTemplate({
        template_name: newTemplateName.trim(),
        task_type_id: newTaskTypeId as number,
      });
      notify.success(`模板「${newTemplateName}」已创建`);
      templatesState.refetch();
      setNewTemplateName("");
      setNewTaskTypeId("");
      setModalMode(null);
      const mapped = mapTemplate(created);
      setSelected(mapped);
    } catch (e) {
      notify.error("创建失败：" + String(e));
    } finally {
      setCreatingTemplate(false);
    }
  };

  const renderPreview = async (versionId: number, variables: Record<string, string>) => {
    if (!selectedTemplate) return;
    setPreviewLoading(true);
    setPreviewError("");
    try {
      const result = await promptsApi.renderTemplate(Number(selectedTemplate.id), {
        version_id: versionId,
        variables,
      });
      setPreviewResult(result);
    } catch (e) {
      setPreviewError(String(e));
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleOpenPreview = () => {
    const versionId = activeVersion?.raw.prompt_version_id;
    if (!versionId) {
      notify.warning("当前模板尚无可渲染版本");
      return;
    }
    setPreviewVersionId(versionId);
    setPreviewValues({});
    setPreviewResult(null);
    setPreviewOpen(true);
    void renderPreview(versionId, {});
  };

  const handlePreviewVersionChange = (versionId: number) => {
    setPreviewVersionId(versionId);
    setPreviewValues({});
    setPreviewResult(null);
    void renderPreview(versionId, {});
  };

  const handleCopyPreview = async () => {
    if (!previewResult) return;
    try {
      await navigator.clipboard.writeText(previewResult.rendered_content);
      notify.success("渲染结果已复制到剪贴板");
    } catch {
      notify.error("复制失败，请手动复制");
    }
  };

  const taskTypes: PromptTaskType[] = taskTypesState.data ?? [];

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-6">
      <PageHeader
        title="提示词模板"
        description="管理资源生成、画像诊断、教师审核和防幻觉检查等场景的提示词模板。"
        icon={FileText}
        action={<button onClick={() => setModalMode("create")} className={`${primaryButton} cursor-pointer`}><Plus className="h-4 w-4" />新建模板</button>}
      />
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
      <section className="grid grid-cols-[360px_1fr] gap-6">
        <aside className="edu-card rounded-2xl p-5">
          <div className="mb-4 space-y-4">
            <SearchInput label="搜索模板" value={query} onChange={setQuery} />
            <SegmentedControl value={taskTypeFilter} options={taskTypeOptions} onChange={setTaskTypeFilter} />
          </div>
          {templatesState.loading ? (
            <div className="flex items-center justify-center py-8"><div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" /></div>
          ) : filtered.length === 0 ? (
            <div className="py-8 text-center text-sm text-slate-400">暂无模板数据</div>
          ) : (
            <div className="custom-scrollbar max-h-[590px] space-y-2 overflow-y-auto pr-1">
              {filtered.map((item) => (
                <button key={item.id} onClick={() => handleSelectTemplate(item)} className={`w-full cursor-pointer rounded-2xl border p-4 text-left transition ${selectedTemplate?.id === item.id ? "border-blue-200 bg-blue-50" : "border-slate-100 bg-white hover:border-blue-200"}`}>
                  <div className="flex items-center justify-between gap-3"><h3 className="text-sm font-black text-slate-900">{item.name}</h3><StatusBadge status={item.enabled ? "启用" : "停用"} /></div>
                  <p className="mt-2 text-xs font-semibold text-slate-500">{item.agent} / {item.version}</p>
                </button>
              ))}
            </div>
          )}
        </aside>
        <main className="edu-card rounded-2xl p-6">
          {!selectedTemplate ? (
            <div className="flex items-center justify-center py-16 text-sm text-slate-400">请选择一个模板</div>
          ) : (
            <>
              <div className="mb-5 flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-xl font-black text-slate-950">{selectedTemplate.name}</h2>
                  <p className="mt-1 text-sm text-slate-500">{selectedTemplate.agent} / {selectedTemplate.version} / {selectedTemplate.updatedAt}</p>
                </div>
                <StatusBadge status={selectedTemplate.enabled ? "启用" : "停用"} />
              </div>
              <div className="mb-5 rounded-2xl border border-slate-100 bg-slate-950 p-5 font-mono text-sm leading-6 text-slate-200">
                {(promptContent || activeVersion?.raw?.prompt_content) ?? "通过版本历史选择加载内容"}
              </div>
              <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
                <button onClick={() => setModalMode("edit")} className={`${primaryButton} cursor-pointer`}>编辑模板</button>
                <button onClick={handleCopyTemplate} className={`${secondaryButton} cursor-pointer`}><Copy className="h-4 w-4" />复制模板</button>
                <button onClick={() => setHistoryOpen(true)} className={`${secondaryButton} cursor-pointer`}>版本历史</button>
                <button onClick={handleOpenPreview} disabled={!activeVersion} className={`${secondaryButton} cursor-pointer disabled:cursor-not-allowed disabled:opacity-50`}><Play className="h-4 w-4" />渲染预览</button>
              </div>
            </>
          )}
        </main>
      </section>

      {/* Edit Modal */}
      <ModalShell title={modalMode === "create" ? "新建提示词模板" : "编辑提示词模板"} open={modalMode !== null} onClose={() => setModalMode(null)}>
        <div className="space-y-4">
          {modalMode === "create" ? (
            <>
              <label className="block text-sm font-bold text-slate-700">
                模板名称
                <input
                  className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm"
                  value={newTemplateName}
                  onChange={(e) => setNewTemplateName(e.target.value)}
                  placeholder="输入模板名称"
                />
              </label>
              <label className="block text-sm font-bold text-slate-700">
                任务类型
                <select
                  className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm"
                  value={newTaskTypeId}
                  onChange={(e) => setNewTaskTypeId(Number(e.target.value) || "")}
                >
                  <option value="">请选择任务类型</option>
                  {taskTypes.map((tt) => (
                    <option key={tt.task_type_id} value={tt.task_type_id}>{tt.type_name}</option>
                  ))}
                </select>
              </label>
            </>
          ) : selectedTemplate ? (
            <>
              <label className="block text-sm font-bold text-slate-700">
                Prompt 内容
                <textarea
                  className="edu-focus-ring mt-2 h-40 w-full resize-none rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm leading-6"
                  value={promptContent}
                  onChange={(e) => setPromptContent(e.target.value)}
                  placeholder="输入 Prompt 内容..."
                />
              </label>
              <label className="block text-sm font-bold text-slate-700">
                变更说明
                <input
                  className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm"
                  value={changeNote}
                  onChange={(e) => setChangeNote(e.target.value)}
                  placeholder="简要描述本次修改（选填）"
                />
              </label>
            </>
          ) : null}
          <div className="flex justify-end gap-3">
            <button onClick={() => setModalMode(null)} className={`${secondaryButton} cursor-pointer`}>取消</button>
            {modalMode === "edit" ? (
              <button onClick={handleSaveVersion} disabled={saving} className={`${primaryButton} cursor-pointer disabled:opacity-60`}>
                {saving ? "保存中..." : "保存新版本"}
              </button>
            ) : (
              <button onClick={handleCreateTemplate} disabled={creatingTemplate} className={`${primaryButton} cursor-pointer disabled:opacity-60`}>
                {creatingTemplate ? "创建中..." : "创建模板"}
              </button>
            )}
          </div>
        </div>
      </ModalShell>

      <ModalShell title="Prompt 渲染预览" open={previewOpen} onClose={() => setPreviewOpen(false)}>
        <div className="space-y-5">
          <label className="block text-sm font-bold text-slate-700">
            模板版本
            <select
              className="edu-focus-ring mt-2 h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm"
              value={previewVersionId ?? ""}
              onChange={(event) => handlePreviewVersionChange(Number(event.target.value))}
            >
              {versions.map((version) => (
                <option key={version.id} value={version.id}>{version.no}{version.active ? "（当前）" : ""}</option>
              ))}
            </select>
          </label>

          {previewLoading && !previewResult ? (
            <div className="flex items-center justify-center py-10"><div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" /></div>
          ) : previewError ? (
            <div className="rounded-xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{previewError}</div>
          ) : previewResult ? (
            <>
              <section>
                <div className="mb-3 flex items-center justify-between gap-3">
                  <h3 className="text-sm font-black text-slate-900">模板变量</h3>
                  <span className="text-xs font-semibold text-slate-500">
                    {Object.keys(previewValues).length}/{previewResult.required_variables.length} 已填写
                  </span>
                </div>
                {previewResult.required_variables.length === 0 ? (
                  <div className="rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-sm text-slate-500">此版本不包含变量</div>
                ) : (
                  <div className="grid gap-3 sm:grid-cols-2">
                    {previewResult.required_variables.map((name: string) => (
                      <label key={name} className="block text-xs font-bold text-slate-600">
                        <code>{name}</code>
                        <textarea
                          className="edu-focus-ring mt-1.5 min-h-20 w-full resize-y rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm leading-5 text-slate-800"
                          value={previewValues[name] ?? ""}
                          onChange={(event) => setPreviewValues((current) => ({ ...current, [name]: event.target.value }))}
                          placeholder={`输入 ${name}`}
                        />
                      </label>
                    ))}
                  </div>
                )}
              </section>

              <div className="flex justify-end">
                <button
                  onClick={() => previewVersionId && void renderPreview(previewVersionId, previewValues)}
                  disabled={previewLoading}
                  className={`${primaryButton} cursor-pointer disabled:cursor-not-allowed disabled:opacity-60`}
                >
                  <Play className="h-4 w-4" />{previewLoading ? "渲染中..." : "生成预览"}
                </button>
              </div>

              <section>
                <div className="mb-3 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-black text-slate-900">渲染结果</h3>
                    {previewResult.missing_variables.length > 0 && (
                      <span className="rounded-full bg-amber-50 px-2 py-1 text-[11px] font-bold text-amber-700">
                        缺少 {previewResult.missing_variables.length} 项
                      </span>
                    )}
                  </div>
                  <button onClick={handleCopyPreview} className={`${secondaryButton} min-h-9 cursor-pointer px-3`}><Copy className="h-4 w-4" />复制</button>
                </div>
                <pre className="custom-scrollbar max-h-80 overflow-auto whitespace-pre-wrap break-words rounded-xl bg-slate-950 p-4 text-xs leading-6 text-slate-200">{previewResult.rendered_content}</pre>
              </section>
            </>
          ) : null}
        </div>
      </ModalShell>

      {/* Version History Drawer */}
      <DetailDrawer title="版本历史" subtitle={selectedTemplate?.name ?? ""} open={historyOpen} onClose={() => setHistoryOpen(false)}>
        {versionsState.loading ? (
          <div className="py-8 text-center text-sm text-slate-400">加载中...</div>
        ) : versions.length === 0 ? (
          <div className="py-8 text-center text-sm text-slate-400">暂无版本历史</div>
        ) : (
          <div className="space-y-3">
            {versions.map((v) => (
              <div key={v.id} className="rounded-2xl border border-slate-100 bg-white p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-slate-700">{v.no}</span>
                    {v.active && <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-bold text-emerald-700">当前版本</span>}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">{v.createdAt} / {v.creator}</span>
                    {!v.active && selectedTemplate && (
                      <button
                        onClick={() => handleActivateVersion(selectedTemplate.id, v.id)}
                        className="cursor-pointer rounded-lg bg-blue-50 px-2 py-1 text-xs font-bold text-blue-700 transition hover:bg-blue-100"
                      >
                        激活
                      </button>
                    )}
                  </div>
                </div>
                <p className="mt-2 text-xs text-slate-500">{v.note}</p>
              </div>
            ))}
          </div>
        )}
      </DetailDrawer>
    </div>
  );
}
