import React from "react";
import { Database, FileUp, GitBranch, Layers3, SearchCheck, AlertCircle, Upload, FileText, Loader2, RefreshCw, Search, CheckCircle2, XCircle, Link2, BookOpen } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { knowledgeApi, type Material, type SearchResult, type MaterialChunk, type KpChunkLink } from "@/lib/api/knowledge";
import { learningApi } from "@/lib/api";
import { DetailDrawer, PageHeader, PageShell, ProgressBar, SearchInput, StatCard, StatusBadge, primaryButton, secondaryButton, useInlineToast, EmptyState } from "../components/common/ProductUI";

export function TeacherKnowledgeBase() {
  const [query, setQuery] = React.useState("");
  const [selectedMaterial, setSelectedMaterial] = React.useState<Material | null>(null);
  const [selectedChunks, setSelectedChunks] = React.useState<MaterialChunk[]>([]);
  const [searchResults, setSearchResults] = React.useState<SearchResult[]>([]);
  const [activePanel, setActivePanel] = React.useState<"documents" | "graph" | "search" | "bindings">("documents");
  const [uploading, setUploading] = React.useState(false);
  const [parsing, setParsing] = React.useState<number | null>(null);
  const [searching, setSearching] = React.useState(false);
  const [pendingLinks, setPendingLinks] = React.useState<KpChunkLink[]>([]);
  const [verifying, setVerifying] = React.useState<number | null>(null);
  const { toast, showToast } = useInlineToast();
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // 资料列表
  const { data: materials, loading: materialsLoading, refresh: refreshMaterials } = useApi(() => knowledgeApi.listMaterials(), []);

  // 待审核的知识点-Chunk匹配
  const { data: pendingKpLinks, loading: linksLoading, refresh: refreshLinks } = useApi(
    () => knowledgeApi.getPendingKpChunkLinks(courseList?.[0]?.id),
    [courseList]
  );

  // 课程列表（用于关联）
  const { data: courseList } = useApi(() => learningApi.listCourses(), []);

  // 知识点列表
  const { data: knowledgePoints } = useApi(() => {
    if (!courseList?.length) return Promise.resolve([]);
    return learningApi.getLearningPath(courseList[0].id).then(p => p.nodes);
  }, [courseList]);

  // 统计
  const stats = [
    { label: "课程资料", value: String(materials?.length ?? 0), hint: "已上传", icon: FileUp, tone: "blue" as const },
    { label: "知识点", value: String(knowledgePoints?.length ?? 0), hint: "含依赖关系", icon: GitBranch, tone: "purple" as const },
    { label: "知识片段", value: String(materials?.reduce((acc, m) => acc + m.chunk_count, 0) ?? 0), hint: "可追溯引用", icon: Layers3, tone: "emerald" as const },
    { label: "待解析", value: String(materials?.filter(m => m.status === 'pending').length ?? 0), hint: "需解析", icon: AlertCircle, tone: "orange" as const },
  ];

  // 状态映射
  const statusMap: Record<Material['status'], string> = {
    pending: '待解析',
    parsing: '解析中',
    parsed: '已解析',
    failed: '解析失败',
  };

  const statusBadgeClass = (status: Material['status']) => {
    switch (status) {
      case 'pending': return 'bg-orange-50 text-orange-700 ring-orange-100';
      case 'parsing': return 'bg-blue-50 text-blue-700 ring-blue-100';
      case 'parsed': return 'bg-emerald-50 text-emerald-700 ring-emerald-100';
      case 'failed': return 'bg-red-50 text-red-700 ring-red-100';
    }
  };

  // 处理文件上传
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    // 如果有选中课程，关联课程ID
    if (courseList?.length) {
      formData.append('course_id', String(courseList[0].id));
    }

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
    setParsing(material.id);
    try {
      await knowledgeApi.parseMaterial(material.id);
      showToast('解析任务已启动');
      // 轮询状态
      const poll = async () => {
        const updated = await knowledgeApi.getMaterial(material.id);
        if (updated.status === 'parsed' || updated.status === 'failed') {
          refreshMaterials();
          setParsing(null);
        } else {
          setTimeout(poll, 2000);
        }
      };
      setTimeout(poll, 2000);
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
      const chunks = await knowledgeApi.getMaterialChunks(material.id);
      setSelectedChunks(chunks);
    } catch (err) {
      console.error(err);
      setSelectedChunks([]);
    }
  };

  // 检索
  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    try {
      const results = await knowledgeApi.search(query, courseList?.[0]?.id);
      setSearchResults(results);
    } catch (err) {
      showToast('检索失败，请重试');
      console.error(err);
    } finally {
      setSearching(false);
    }
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
        eyebrow="Course Knowledge Base"
        title="课程知识库"
        description="管理课程文档、知识点、知识片段和检索证据，为智能体生成资源提供可信依据。"
        icon={Database}
        action={
          <label className={`${primaryButton} cursor-pointer`}>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.md,.docx,.pptx"
              className="hidden"
              onChange={handleFileUpload}
              disabled={uploading}
            />
            {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
            {uploading ? '上传中...' : '上传资料'}
          </label>
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
            ) : materials?.length === 0 ? (
              <EmptyState
                title="暂无资料"
                description="上传 PDF、Markdown、Word 或 PPT 文档，系统将自动解析并构建知识库。"
                action={
                  <label className={`${secondaryButton} cursor-pointer`}>
                    <input
                      type="file"
                      accept=".pdf,.md,.docx,.pptx"
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
              materials?.map((doc) => (
                <div key={doc.id} className="w-full rounded-2xl border p-4 text-left transition">
                  <button
                    onClick={() => handleViewMaterial(doc)}
                    className={`w-full rounded-2xl border p-4 text-left transition ${
                      selectedMaterial?.id === doc.id ? "border-blue-200 bg-blue-50" : "border-slate-100 bg-white hover:border-blue-200"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0 flex-1">
                        <h3 className="truncate text-sm font-black leading-5 text-slate-900">{doc.file_name}</h3>
                        <p className="mt-1 text-xs text-slate-500">{doc.file_type.toUpperCase()} · {Math.round(doc.file_size / 1024)}KB</p>
                      </div>
                      <StatusBadge status={statusMap[doc.status]} />
                    </div>
                    <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                      <span className="font-bold text-slate-500">{doc.chunk_count} 片段</span>
                      <span className="font-bold text-slate-500">{doc.page_count ? `${doc.page_count} 页` : '-'}</span>
                    </div>
                  </button>
                  {doc.status === 'pending' && (
                    <button
                      onClick={() => handleParse(doc)}
                      disabled={parsing === doc.id}
                      className={`mt-2 flex w-full items-center justify-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-3 py-2 text-xs font-bold text-blue-700 transition hover:bg-blue-100 disabled:opacity-50`}
                    >
                      {parsing === doc.id ? (
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
            <button onClick={() => showToast("知识点编辑面板已打开")} className={secondaryButton}>编辑知识点</button>
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
              <h3 className="mb-3 text-sm font-black text-slate-950">文档片段 - {selectedMaterial.file_name}</h3>
              <div className="custom-scrollbar max-h-[200px] space-y-2 overflow-y-auto">
                {selectedChunks.length === 0 ? (
                  <p className="text-xs text-slate-500">暂无片段，请先解析文档</p>
                ) : (
                  selectedChunks.map((chunk) => (
                    <div key={chunk.id} className="rounded-xl border border-slate-100 bg-white p-3">
                      <div className="mb-1 flex items-center justify-between">
                        <span className="text-[11px] font-black text-slate-400">
                          片段 {chunk.chunk_index + 1}
                          {chunk.page_num !== null && ` · 第 ${chunk.page_num} 页`}
                        </span>
                        {chunk.knowledge_point_name && (
                          <span className="rounded-full bg-purple-50 px-2 py-0.5 text-[10px] font-bold text-purple-700">
                            {chunk.knowledge_point_name}
                          </span>
                        )}
                      </div>
                      <p className="line-clamp-3 text-xs leading-5 text-slate-600">{chunk.content}</p>
                      {chunk.keywords.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {chunk.keywords.slice(0, 5).map((kw) => (
                            <span key={kw} className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500">{kw}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
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
              disabled={searching || !query.trim()}
              className={`${primaryButton} mt-auto disabled:opacity-50`}
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
                      <h3 className="text-sm font-black text-slate-900 truncate max-w-[180px]">{result.file_name}</h3>
                    </div>
                    <span className="text-xs font-black text-blue-700">{Math.round(result.score * 100)}%</span>
                  </div>
                  {result.page_num !== null && (
                    <p className="mb-2 text-[11px] text-slate-400">页码: {result.page_num}</p>
                  )}
                  <p className="line-clamp-4 text-xs leading-5 text-slate-600">{result.content}</p>
                  {result.knowledge_point_name && (
                    <div className="mt-2">
                      <span className="rounded bg-purple-50 px-2 py-0.5 text-[10px] font-bold text-purple-700">
                        知识点: {result.knowledge_point_name}
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
