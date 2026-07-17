import React from "react";
import { useSearchParams } from "react-router-dom";
import { Database, FileUp, GitBranch, Layers3, AlertCircle, Upload, Loader2, RefreshCw, Search, CheckCircle2, XCircle, Link2, BookOpen } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { knowledgeApi, type Material, type SearchResult, type MaterialChunk } from "@/lib/api/knowledge";
import { learningApi } from "@/lib/api";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { PageHeader, PageShell, ProgressBar, SearchInput, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast, EmptyState } from "../components/common/ProductUI";

function parseChunkTerms(value: string | null | undefined): string[] {
  if (!value) return [];

  try {
    const parsed = JSON.parse(value);
    if (Array.isArray(parsed)) {
      return parsed.map(String).map((term) => term.trim()).filter(Boolean);
    }
  } catch {
    // Older records may store terms as comma- or whitespace-separated text.
  }

  return value.split(/[,，\s]+/).map((term) => term.trim()).filter(Boolean);
}

export function TeacherKnowledgeBase() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = React.useState("");
  const [selectedMaterial, setSelectedMaterial] = React.useState<Material | null>(null);
  const [selectedChunks, setSelectedChunks] = React.useState<MaterialChunk[]>([]);
  const [searchResults, setSearchResults] = React.useState<SearchResult[]>([]);
  const [activePanel, setActivePanel] = React.useState<"documents" | "graph" | "search" | "bindings">("documents");
  const [uploading, setUploading] = React.useState(false);
  const [parsing, setParsing] = React.useState<number | null>(null);
  const [searching, setSearching] = React.useState(false);
  const [verifying, setVerifying] = React.useState<number | null>(null);
  const [selectedCourseId, setSelectedCourseId] = React.useState<number | null>(null);
  const { toast, showToast } = useInlineToast();
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const pollTimeoutRef = React.useRef<number | null>(null);
  const mountedRef = React.useRef(true);

  // 课程列表（用于关联）
  const { data: courseList } = useApi(() => learningApi.listCourses(), []);

  React.useEffect(() => {
    if (!courseList?.length) {
      setSelectedCourseId(null);
      return;
    }
    const requestedCourseId = Number(searchParams.get("course"));
    if (requestedCourseId && courseList.some((course) => course.id === requestedCourseId)) {
      setSelectedCourseId(requestedCourseId);
      return;
    }
    if (!courseList.some((course) => course.id === selectedCourseId)) {
      setSelectedCourseId(courseList[0].id);
    }
  }, [courseList, searchParams, selectedCourseId]);

  React.useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (pollTimeoutRef.current !== null) window.clearTimeout(pollTimeoutRef.current);
    };
  }, []);

  // 待审核的知识点-Chunk匹配
  const { data: pendingKpLinks, loading: linksLoading, refetch: refreshLinks } = useApi(
    () => selectedCourseId
      ? knowledgeApi.getPendingKpChunkLinks(selectedCourseId)
      : Promise.resolve([]),
    [selectedCourseId]
  );

  // 资料列表（有课程 ID 时才请求，返回 data 字段）
  const { data: materialsData, loading: materialsLoading, refetch: refreshMaterials } = useApi(
    () => selectedCourseId
      ? knowledgeApi.listMaterials(selectedCourseId)
      : Promise.resolve([] as Material[]),
    [selectedCourseId]
  );

  // 知识点列表
  const { data: knowledgePoints } = useApi(() => {
    if (!selectedCourseId) return Promise.resolve([]);
    return learningApi.getLearningPath(selectedCourseId).then(p => p.nodes);
  }, [selectedCourseId]);

  // 统计
  const stats = [
    { label: "课程资料", value: String(materialsData?.length ?? 0), hint: "已上传", icon: FileUp, tone: "blue" as const },
    { label: "知识点", value: String(knowledgePoints?.length ?? 0), hint: "含依赖关系", icon: GitBranch, tone: "purple" as const },
    { label: "知识片段", value: String(materialsData?.reduce((acc, m) => acc + (m.total_chunks ?? 0), 0) ?? 0), hint: "可追溯引用", icon: Layers3, tone: "emerald" as const },
    { label: "待解析", value: String(materialsData?.filter(m => m.status === 'pending').length ?? 0), hint: "需解析", icon: AlertCircle, tone: "orange" as const },
  ];

  // 状态映射
  const statusMap: Record<Material['status'], string> = {
    pending: '待解析',
    parsing: '解析中',
    parsed: '已解析',
    failed: '解析失败',
  };

  // 处理文件上传
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    if (!selectedCourseId) {
      showToast('请先选择课程');
      return;
    }
    formData.append('course_id', String(selectedCourseId));

    setUploading(true);
    try {
      await knowledgeApi.uploadMaterial(formData);
      showToast('资料上传成功');
      refreshMaterials();
    } catch (err) {
      showToast('上传失败，请重试');
      console.error(err);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // 解析资料
  const handleParse = async (material: Material) => {
    if (pollTimeoutRef.current !== null) window.clearTimeout(pollTimeoutRef.current);
    setParsing(material.material_id);
    try {
      await knowledgeApi.parseMaterial(material.material_id);
      showToast('解析任务已启动');
      let attempts = 0;
      const poll = async () => {
        try {
          const updated = await knowledgeApi.getMaterial(material.material_id);
          if (!mountedRef.current) return;
          if (updated.status === 'parsed' || updated.status === 'failed') {
            await refreshMaterials();
            setParsing(null);
            if (updated.status === 'failed') showToast('资料解析失败，请检查文件内容');
            return;
          }
        } catch (err) {
          console.error(err);
        }

        attempts += 1;
        if (attempts >= 60) {
          setParsing(null);
          showToast('解析仍在后台进行，请稍后刷新查看');
          return;
        }
        pollTimeoutRef.current = window.setTimeout(poll, 2000);
      };
      pollTimeoutRef.current = window.setTimeout(poll, 2000);
    } catch (err) {
      showToast('解析失败，请重试');
      setParsing(null);
      console.error(err);
    }
  };

  // 查看资料详情（包含 chunks）
  const handleViewMaterial = async (material: Material) => {
    setSelectedMaterial(material);
    try {
      const chunks = await knowledgeApi.getMaterialChunks(material.material_id);
      setSelectedChunks(chunks);
    } catch (err) {
      console.error(err);
      setSelectedChunks([]);
    }
  };

  // 检索
  const handleSearch = async () => {
    if (!query.trim() || !selectedCourseId) return;
    setSearching(true);
    try {
      const results = await knowledgeApi.search(query, selectedCourseId);
      setSearchResults(results);
    } catch (err) {
      showToast('检索失败，请重试');
      console.error(err);
    } finally {
      setSearching(false);
    }
  };

  const handleCourseChange = (value: string) => {
    if (pollTimeoutRef.current !== null) window.clearTimeout(pollTimeoutRef.current);
    pollTimeoutRef.current = null;
    setParsing(null);
    setSelectedMaterial(null);
    setSelectedChunks([]);
    setSearchResults([]);
    const courseId = Number(value);
    setSelectedCourseId(courseId);
    const next = new URLSearchParams(searchParams);
    next.set("course", String(courseId));
    setSearchParams(next, { replace: true });
  };

  // 确认/拒绝知识点-Chunk绑定
  const handleVerifyLink = async (linkId: number, status: 'confirmed' | 'rejected') => {
    setVerifying(linkId);
    try {
      await knowledgeApi.verifyKpChunkLink(linkId, status);
      showToast(status === 'confirmed' ? '已确认该绑定' : '已拒绝该绑定');
      refreshLinks();
    } catch (err) {
      showToast('操作失败，请重试');
    } finally {
      setVerifying(null);
    }
  };

  return (
    <PageShell>
      <PageHeader
        eyebrow=""
        title="课程知识库"
        description="管理课程文档、知识点、知识片段和检索证据，为智能体生成资源提供可信依据。"
        icon={Database}
        action={
          <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row">
            <Select value={selectedCourseId ? String(selectedCourseId) : undefined} onValueChange={handleCourseChange}>
              <SelectTrigger className="h-10 min-w-48 rounded-xl bg-white">
                <SelectValue placeholder="选择课程" />
              </SelectTrigger>
              <SelectContent>
                {courseList?.map((course) => (
                  <SelectItem key={course.id} value={String(course.id)}>{course.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <label className={`${primaryButton} cursor-pointer ${!selectedCourseId ? 'pointer-events-none opacity-50' : ''}`}>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.md,.markdown,.docx,.pptx,.txt,.text"
                className="hidden"
                onChange={handleFileUpload}
                disabled={uploading || !selectedCourseId}
              />
              {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
              {uploading ? '上传中...' : '上传资料'}
            </label>
          </div>
        }
      />

      <section className="grid grid-cols-2 gap-3 sm:grid-cols-4 xl:grid-cols-4 xl:gap-4">
        {stats.map((stat) => <StatCard key={stat.label} {...stat} />)}
      </section>

      <div className="grid grid-cols-4 gap-1 rounded-2xl bg-slate-100 p-1 lg:hidden">
        {[
          ["documents", "文档"],
          ["graph", "结构"],
          ["bindings", "绑定"],
          ["search", "检索"],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setActivePanel(key as typeof activePanel)}
            className={`min-h-11 rounded-xl text-sm font-black transition ${
              activePanel === key ? "bg-white text-blue-700 shadow-sm" : "text-slate-500"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <section className="grid min-h-0 grid-cols-1 gap-4 lg:min-h-[650px] lg:grid-cols-[0.82fr_1fr_0.9fr] lg:gap-6">
        {/* 左侧：课程资料列表 */}
        <div className={`edu-card rounded-2xl p-5 ${activePanel === "documents" ? "block" : "hidden lg:block"}`}>
          <h2 className="mb-4 text-base font-black text-slate-950">课程资料列表</h2>
          <div className="custom-scrollbar max-h-[570px] space-y-3 overflow-y-auto pr-1">
            {materialsLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
              </div>
            ) : materialsData?.length === 0 ? (
              <EmptyState
                title="暂无资料"
                description="上传 PDF、Markdown、Word 或 PPT 文档，系统将自动解析并构建知识库。"
                action={
                  <label className={`${secondaryButton} cursor-pointer`}>
                    <input
                      type="file"
                      accept=".pdf,.md,.markdown,.docx,.pptx,.txt,.text"
                      className="hidden"
                      onChange={handleFileUpload}
                      disabled={uploading}
                    />
                    <Upload className="h-4 w-4" />
                    上传资料
                  </label>
                }
              />
            ) : (
              materialsData?.map((doc) => (
                <div key={doc.material_id} className="w-full space-y-2">
                  <button
                    onClick={() => handleViewMaterial(doc)}
                    className={`w-full rounded-2xl border p-4 text-left transition ${
                      selectedMaterial?.material_id === doc.material_id ? "border-blue-200 bg-blue-50" : "border-slate-100 bg-white hover:border-blue-200"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0 flex-1">
                        <h3 className="truncate text-sm font-black leading-5 text-slate-900">{doc.filename}</h3>
                        <p className="mt-1 text-xs text-slate-500">
                          {doc.file_type.toUpperCase()} · {doc.total_chars > 0 ? `${doc.total_chars.toLocaleString("zh-CN")} 字` : "待统计字数"}
                        </p>
                      </div>
                      <StatusBadge status={statusMap[doc.status]} />
                    </div>
                    <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                      <span className="font-bold text-slate-500">{doc.total_chunks ?? 0} 片段</span>
                      <span className="font-bold text-slate-500">v{doc.material_version ?? 1}</span>
                    </div>
                  </button>
                  {doc.status === 'pending' && (
                    <button
                      onClick={() => handleParse(doc)}
                      disabled={parsing === doc.material_id}
                      className={`mt-2 flex w-full items-center justify-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-3 py-2 text-xs font-bold text-blue-700 transition hover:bg-blue-100 disabled:opacity-50`}
                    >
                      {parsing === doc.material_id ? (
                        <><Loader2 className="h-3 w-3 animate-spin" /> 解析中...</>
                      ) : (
                        <><RefreshCw className="h-3 w-3" /> 解析资料</>
                      )}
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* 中间：知识点图谱和文档 chunk */}
        <div className={`edu-card rounded-2xl p-5 sm:p-6 ${activePanel === "graph" ? "block" : "hidden lg:block"}`}>
          <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-base font-black text-slate-950">知识点结构</h2>
          </div>
          <div className="relative rounded-[20px] border border-slate-100 bg-slate-50/70 p-4 sm:rounded-[24px] sm:p-6">
            <div className="absolute inset-0 edu-grid-bg opacity-50" />
            <div className="relative grid grid-cols-1 gap-3 sm:grid-cols-2">
              {knowledgePoints && knowledgePoints.length > 0 ? (
                knowledgePoints.slice(0, 8).map((point, index) => (
                  <div key={point.id} className="rounded-2xl border border-slate-100 bg-white p-4">
                    <div className="mb-2 flex items-center justify-between">
                      <span className="text-[11px] font-black text-slate-400">KP{String(index + 1).padStart(2, '0')}</span>
                      <span className={`h-2 w-2 rounded-full ${point.mastery_level >= 0.75 ? 'bg-emerald-500' : point.mastery_level >= 0.5 ? 'bg-orange-500' : 'bg-red-500'}`} />
                    </div>
                    <div className="text-sm font-black text-slate-900">{point.kp_name}</div>
                    <div className="mt-3">
                      <ProgressBar value={point.mastery_level * 100} tone={point.mastery_level >= 0.75 ? "emerald" : point.mastery_level >= 0.5 ? "orange" : "red"} />
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-2 py-8 text-center text-sm text-slate-500">
                  暂无知识点数据
                </div>
              )}
            </div>
          </div>

          {/* 文档 Chunk 列表 */}
          {selectedMaterial && (
            <div className="mt-5">
              <h3 className="mb-3 text-sm font-black text-slate-950">文档片段 - {selectedMaterial.filename}</h3>
              <div className="custom-scrollbar max-h-[200px] space-y-2 overflow-y-auto">
                {selectedChunks.length === 0 ? (
                  <p className="text-xs text-slate-500">暂无片段，请先解析文档</p>
                ) : (
                  selectedChunks.map((chunk) => {
                    const terms = parseChunkTerms(chunk.bm25_terms);
                    return (
                      <div key={chunk.chunk_id} className="rounded-xl border border-slate-100 bg-white p-3">
                        <div className="mb-1 flex items-center justify-between">
                          <span className="text-[11px] font-black text-slate-400">
                            片段 {chunk.chunk_index + 1}
                            {chunk.source_page !== null && ` · 第 ${chunk.source_page} 页`}
                          </span>
                          {chunk.kp_id !== null && (
                            <span className="rounded-full bg-purple-50 px-2 py-0.5 text-[10px] font-bold text-purple-700">
                              KP {chunk.kp_id}
                            </span>
                          )}
                        </div>
                        <p className="line-clamp-3 text-xs leading-5 text-slate-600">{chunk.content}</p>
                        {terms.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {terms.slice(0, 5).map((kw) => (
                              <span key={kw} className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500">{kw}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          )}
        </div>

        {/* 右侧：检索测试与证据预览 */}
        <div className={`edu-card rounded-2xl p-5 ${activePanel === "search" ? "block" : "hidden lg:block"}`}>
          <h2 className="mb-4 text-base font-black text-slate-950">检索测试</h2>
          <div className="flex gap-2">
            <SearchInput label="测试问题" value={query} onChange={setQuery} />
            <button
              onClick={handleSearch}
              disabled={searching || !query.trim() || !selectedCourseId}
              className={`${primaryButton} mt-auto disabled:opacity-50`}
              aria-label={searching ? "正在检索知识库" : "执行知识库检索"}
              title={searching ? "正在检索" : "执行检索"}
            >
              {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            </button>
          </div>
          {searchResults.length > 0 ? (
            <div className="mt-5 space-y-3">
              {searchResults.map((result, index) => (
                <div key={result.chunk_id} className="rounded-2xl border border-slate-100 bg-white p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-black text-blue-700">#{index + 1}</span>
                      <h3 className="text-sm font-black text-slate-900 truncate max-w-[180px]">
                        {materialsData?.find(material => material.material_id === result.material_id)?.filename ?? `Chunk ${result.chunk_id}`}
                      </h3>
                    </div>
                    <span className="text-xs font-black text-blue-700">相对相关度 {Math.round(result.relative_score * 100)}%</span>
                  </div>
                  <p className="mb-2 text-[11px] text-slate-400">
                    Chunk {result.chunk_id}{result.page_num !== null && ` · 第 ${result.page_num} 页`}
                  </p>
                  <p className="line-clamp-4 text-xs leading-5 text-slate-600">{result.content}</p>
                  {result.title && (
                    <div className="mt-2">
                      <span className="rounded bg-purple-50 px-2 py-0.5 text-[10px] font-bold text-purple-700">
                        知识点: {result.title}
                      </span>
                    </div>
                  )}
                  {result.keywords.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {result.keywords.slice(0, 5).map((kw) => (
                        <span key={kw} className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500">{kw}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : query && !searching ? (
            <div className="mt-5 rounded-2xl border border-slate-100 bg-white p-4 text-center text-sm text-slate-500">
              输入问题并点击搜索按钮开始检索
            </div>
          ) : null}
        </div>
      </section>

      {/* 知识点绑定管理面板 */}
      <section className={`edu-card rounded-2xl p-5 ${activePanel === "bindings" ? "block" : "hidden lg:block"}`}>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-black text-slate-950 flex items-center gap-2">
            <Link2 className="h-4 w-4" />
            知识点-Chunk 绑定管理
          </h2>
          <span className="text-xs text-slate-500">
            {pendingKpLinks?.length ?? 0} 条待审核
          </span>
        </div>

        {linksLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
          </div>
        ) : pendingKpLinks && pendingKpLinks.length > 0 ? (
          <div className="custom-scrollbar max-h-[500px] space-y-3 overflow-y-auto pr-1">
            {pendingKpLinks.map((link) => (
              <div key={link.link_id} className="rounded-2xl border border-slate-100 bg-white p-4">
                <div className="mb-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="rounded bg-purple-50 px-2 py-0.5 text-[10px] font-bold text-purple-700">
                      {link.kp_name}
                    </span>
                    <span className="text-xs text-slate-400">←</span>
                    <span className="rounded bg-blue-50 px-2 py-0.5 text-[10px] font-bold text-blue-700 truncate max-w-[150px]">
                      {link.material_filename}
                    </span>
                    <span className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
                      link.match_method === 'bm25' ? 'bg-slate-100 text-slate-600' :
                      link.match_method === 'embedding' ? 'bg-green-50 text-green-700' :
                      'bg-orange-50 text-orange-700'
                    }`}>
                      {link.match_method}
                    </span>
                  </div>
                  <span className="text-xs font-black text-blue-700">
                    {Math.round(link.relevance_score * 100)}%
                  </span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleVerifyLink(link.link_id, 'confirmed')}
                    disabled={verifying === link.link_id}
                    className="flex items-center gap-1 rounded-xl bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-700 transition hover:bg-emerald-100 disabled:opacity-50"
                  >
                    <CheckCircle2 className="h-3 w-3" />
                    {verifying === link.link_id ? '处理中...' : '确认'}
                  </button>
                  <button
                    onClick={() => handleVerifyLink(link.link_id, 'rejected')}
                    disabled={verifying === link.link_id}
                    className="flex items-center gap-1 rounded-xl bg-red-50 px-3 py-1.5 text-xs font-bold text-red-700 transition hover:bg-red-100 disabled:opacity-50"
                  >
                    <XCircle className="h-3 w-3" />
                    拒绝
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <BookOpen className="mb-3 h-8 w-8 text-slate-300" />
            <p className="text-sm text-slate-500">暂无待审核的绑定</p>
            <p className="mt-1 text-xs text-slate-400">上传并解析课程资料后，系统将自动匹配知识点</p>
          </div>
        )}
      </section>

      {toast}
    </PageShell>
  );
}
