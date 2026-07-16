import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  AlertTriangle,
  Book,
  Brain,
  CheckCircle2,
  Clock,
  History,
  Library,
  LoaderCircle,
  MessageSquare,
  RefreshCw,
  Send,
  Sparkles,
  Target,
  User,
  Wrench,
  XCircle,
} from "lucide-react";
import { useApi } from "@/lib/useApi";
import { profilesApi } from "@/lib/api";
import type {
  DialogMessage,
  ProfileDetail,
  ProfileExtraction,
} from "@/lib/api/profiles";
import { notify } from "@/lib/toast";
import { PageHero } from "../components/common/PageHero";

type FeedbackRecord = Awaited<ReturnType<typeof profilesApi.getFeedbackHistory>>[number];

const EXTRACTION_LABELS: Array<[keyof ProfileExtraction, string]> = [
  ["learning_goal", "学习目标"],
  ["knowledge_base", "知识基础"],
  ["current_level", "当前水平"],
  ["cognitive_style", "认知风格"],
  ["weak_points", "薄弱点"],
  ["error_prone_points", "易错点"],
  ["interests", "兴趣方向"],
  ["resource_preferences", "资源偏好"],
  ["weekly_hours", "每周时长"],
  ["time_constraints", "时间约束"],
  ["practice_level", "实践水平"],
  ["motivation", "学习动机"],
];

function extractionItems(extraction: ProfileExtraction | null) {
  if (!extraction) return [];
  return EXTRACTION_LABELS.flatMap(([field, label]) => {
    const raw = extraction[field];
    if (raw == null || raw === "" || (Array.isArray(raw) && raw.length === 0)) return [];
    const value = Array.isArray(raw)
      ? raw.join("、")
      : field === "weekly_hours"
        ? `${raw} 小时`
        : String(raw);
    return [{ field, label, value }];
  });
}

function profilePointNames(points: ProfileDetail["strong_points"] | ProfileDetail["weak_points"]) {
  return points.map((point) => point.kp_name || point.name || "未命名知识点");
}

function formatPercent(value: number) {
  const normalized = value <= 1 ? value * 100 : value;
  return `${Math.round(normalized)}%`;
}

function uniqueStrings(values: string[]) {
  return [...new Set(values.filter(Boolean))];
}

export function StudentProfile() {
  const {
    data: profile,
    loading: profileLoading,
    error: profileError,
    refetch: reloadProfile,
  } = useApi(() => profilesApi.getMyProfile(), []);

  const [updateRecords, setUpdateRecords] = useState<FeedbackRecord[]>([]);
  const [messages, setMessages] = useState<DialogMessage[]>([]);
  const [messageInput, setMessageInput] = useState("");
  const [loadingRecords, setLoadingRecords] = useState(false);
  const [loadingDialog, setLoadingDialog] = useState(false);
  const [sending, setSending] = useState(false);
  const [applyingMessageId, setApplyingMessageId] = useState<number | null>(null);
  const [dialogError, setDialogError] = useState("");
  const messageListRef = useRef<HTMLDivElement>(null);

  const loadRecords = useCallback(async (profileId: number) => {
    setLoadingRecords(true);
    try {
      setUpdateRecords(await profilesApi.getFeedbackHistory(profileId));
    } catch {
      setUpdateRecords([]);
    } finally {
      setLoadingRecords(false);
    }
  }, []);

  const loadDialog = useCallback(async (profileId: number) => {
    setLoadingDialog(true);
    setDialogError("");
    try {
      setMessages(await profilesApi.getDialogHistory(profileId));
    } catch (error) {
      setDialogError(String(error));
    } finally {
      setLoadingDialog(false);
    }
  }, []);

  useEffect(() => {
    if (!profile?.profile_id) {
      setMessages([]);
      setUpdateRecords([]);
      return;
    }
    void loadDialog(profile.profile_id);
    void loadRecords(profile.profile_id);
  }, [loadDialog, loadRecords, profile?.profile_id]);

  useEffect(() => {
    const list = messageListRef.current;
    if (list) list.scrollTop = list.scrollHeight;
  }, [messages, sending]);

  const pendingMessages = useMemo(
    () => messages.filter(
      (message) => message.role === "assistant"
        && !message.is_applied
        && extractionItems(message.extracted_json).length > 0,
    ),
    [messages],
  );

  const handleSend = async () => {
    const content = messageInput.trim();
    if (!content || !profile || sending) return;

    const optimisticId = -Date.now();
    setMessageInput("");
    setSending(true);
    setDialogError("");
    setMessages((current) => [
      ...current,
      {
        message_id: optimisticId,
        profile_id: profile.profile_id,
        role: "student",
        content,
        created_at: new Date().toISOString(),
        extracted_json: null,
        is_applied: false,
      },
    ]);

    try {
      await profilesApi.sendDialogMessage(profile.profile_id, content);
      await loadDialog(profile.profile_id);
    } catch (error) {
      setMessages((current) => current.filter((message) => message.message_id !== optimisticId));
      setMessageInput(content);
      setDialogError(String(error));
      notify.error("消息发送失败，请重试");
    } finally {
      setSending(false);
    }
  };

  const handleApply = async (messageId: number) => {
    if (!profile || applyingMessageId != null) return;
    setApplyingMessageId(messageId);
    try {
      const result = await profilesApi.applyExtraction(profile.profile_id, messageId);
      await Promise.all([loadDialog(profile.profile_id), reloadProfile()]);
      notify.success(result.change_summary || "画像已更新");
    } catch {
      notify.error("画像更新失败，请重试");
    } finally {
      setApplyingMessageId(null);
    }
  };

  if (profileLoading) {
    return (
      <div className="mx-auto max-w-[1500px] space-y-4 py-6" aria-busy="true">
        <div className="h-12 animate-pulse rounded-lg bg-slate-200 motion-reduce:animate-none" />
        <div className="h-96 animate-pulse rounded-lg bg-slate-100 motion-reduce:animate-none" />
      </div>
    );
  }

  if (profileError || !profile) {
    return (
      <div className="mx-auto flex min-h-64 max-w-[1400px] flex-col items-center justify-center gap-3 text-center">
        <div className="text-base font-bold text-slate-700">暂时无法加载学习画像</div>
        <div className="text-sm text-slate-500">请确认账号已绑定课程后重试</div>
        <button
          type="button"
          onClick={() => reloadProfile()}
          className="min-h-11 rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
        >
          重新加载
        </button>
      </div>
    );
  }

  const strongPoints = profilePointNames(profile.strong_points).slice(0, 2);
  const weakPoints = profilePointNames(profile.weak_points).slice(0, 3);
  const masteryPercent = Math.max(0, Math.min(100, Math.round(profile.mastery_score * 100)));
  const dimensions = [
    {
      icon: Book,
      title: "知识基础",
      color: "text-blue-600",
      bg: "bg-blue-50",
      items: uniqueStrings([profile.knowledge_base, ...strongPoints]).slice(0, 3),
      source: "对话信息与测验表现",
    },
    {
      icon: Target,
      title: "目标与动机",
      color: "text-violet-600",
      bg: "bg-violet-50",
      items: uniqueStrings([profile.learning_goal, profile.motivation]),
      source: "学习目标与自述动机",
    },
    {
      icon: Brain,
      title: "认知风格",
      color: "text-indigo-600",
      bg: "bg-indigo-50",
      items: [profile.cognitive_style].filter(Boolean),
      source: "学习对话与行为偏好",
    },
    {
      icon: Library,
      title: "资源偏好",
      color: "text-emerald-600",
      bg: "bg-emerald-50",
      items: profile.resource_preferences.slice(0, 3),
      source: "资源使用与反馈记录",
    },
    {
      icon: AlertTriangle,
      title: "薄弱与易错点",
      color: "text-amber-700",
      bg: "bg-amber-50",
      items: uniqueStrings([...weakPoints, ...profile.error_prone_points]).slice(0, 3),
      source: "测验结果与错误归因",
    },
    {
      icon: XCircle,
      title: "当前水平",
      color: "text-rose-600",
      bg: "bg-rose-50",
      items: [profile.current_level].filter(Boolean),
      source: "综合掌握度评估",
    },
    {
      icon: Clock,
      title: "时间约束",
      color: "text-cyan-700",
      bg: "bg-cyan-50",
      items: [
        profile.time_constraints,
        profile.weekly_hours ? `每周 ${profile.weekly_hours} 小时` : "",
      ].filter(Boolean),
      source: "学习计划与可用时段",
    },
    {
      icon: Wrench,
      title: "实践能力",
      color: "text-teal-700",
      bg: "bg-teal-50",
      items: uniqueStrings([profile.practice_level, ...profile.interests]).slice(0, 3),
      source: "项目实践与兴趣方向",
    },
  ];

  return (
    <div className="mx-auto min-h-full max-w-[1500px] space-y-6 py-6">
      <PageHero
        eyebrow={profile.course_name}
        title="我的学习画像"
        description="AI 分析你的对话、测验和资源交互记录，构建多维度认知模型，持续指导个性化学习。"
        icon={Brain}
        role="student"
      />
      <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm" aria-labelledby="profile-dialog-title">
        <div className="grid min-h-[430px] lg:grid-cols-[minmax(0,1.65fr)_minmax(300px,0.85fr)]">
          <div className="flex min-w-0 flex-col border-b border-slate-200 lg:border-b-0 lg:border-r">
            <div className="flex items-center gap-3 border-b border-slate-100 px-5 py-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white">
                <MessageSquare className="h-5 w-5" />
              </div>
              <div>
                <h2 id="profile-dialog-title" className="font-bold text-slate-900">画像对话</h2>
                <p className="text-sm text-slate-500">学习画像助手</p>
              </div>
              <button
                type="button"
                onClick={() => void loadDialog(profile.profile_id)}
                className="ml-auto flex h-11 w-11 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                aria-label="刷新对话"
                title="刷新对话"
              >
                <RefreshCw className={`h-4 w-4 ${loadingDialog ? "animate-spin motion-reduce:animate-none" : ""}`} />
              </button>
            </div>

            <div ref={messageListRef} className="h-[330px] space-y-4 overflow-y-auto bg-slate-50/60 px-4 py-5 sm:px-6" aria-live="polite">
              {loadingDialog && messages.length === 0 && (
                <div className="flex h-full items-center justify-center text-sm text-slate-500">
                  <LoaderCircle className="mr-2 h-4 w-4 animate-spin motion-reduce:animate-none" />
                  加载对话
                </div>
              )}

              {!loadingDialog && messages.length === 0 && !dialogError && (
                <div className="mx-auto flex h-full max-w-lg flex-col items-center justify-center text-center">
                  <Sparkles className="mb-3 h-7 w-7 text-blue-600" />
                  <p className="font-semibold text-slate-800">开始完善你的学习画像</p>
                  <div className="mt-4 flex flex-wrap justify-center gap-2">
                    {["我的学习目标是...", "我更喜欢通过...学习", "我每周可以学习..."].map((suggestion) => (
                      <button
                        key={suggestion}
                        type="button"
                        onClick={() => setMessageInput(suggestion)}
                        className="min-h-11 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 transition-colors hover:border-blue-300 hover:text-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((message) => (
                <div
                  key={message.message_id}
                  className={`flex ${message.role === "student" ? "justify-end" : "justify-start"}`}
                >
                  <div className={`max-w-[88%] rounded-lg px-4 py-3 text-sm leading-6 shadow-sm sm:max-w-[78%] ${
                    message.role === "student"
                      ? "bg-blue-600 text-white"
                      : "border border-slate-200 bg-white text-slate-700"
                  }`}>
                    {message.role === "assistant" ? (
                      <div className="prose prose-sm prose-slate max-w-none prose-p:my-1 prose-strong:text-slate-900">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    ) : (
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    )}
                    <time className={`mt-1 block text-xs ${message.role === "student" ? "text-blue-100" : "text-slate-400"}`}>
                      {new Date(message.created_at).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })}
                    </time>
                  </div>
                </div>
              ))}

              {sending && (
                <div className="flex justify-start">
                  <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-sm">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500 motion-reduce:animate-none" />
                    正在分析画像信息
                  </div>
                </div>
              )}
            </div>

            <form
              className="border-t border-slate-100 p-4"
              onSubmit={(event) => {
                event.preventDefault();
                void handleSend();
              }}
            >
              <label htmlFor="profile-message" className="sr-only">画像对话消息</label>
              <div className="flex items-end gap-2">
                <textarea
                  id="profile-message"
                  value={messageInput}
                  onChange={(event) => setMessageInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      void handleSend();
                    }
                  }}
                  rows={2}
                  maxLength={1000}
                  placeholder="描述你的目标、基础、偏好或时间安排"
                  className="min-h-12 flex-1 resize-none rounded-lg border border-slate-300 px-3 py-2.5 text-base text-slate-800 outline-none transition-colors placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  disabled={sending}
                />
                <button
                  type="submit"
                  disabled={!messageInput.trim() || sending}
                  className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white transition-colors hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-40"
                  aria-label="发送消息"
                  title="发送消息"
                >
                  {sending ? <LoaderCircle className="h-5 w-5 animate-spin motion-reduce:animate-none" /> : <Send className="h-5 w-5" />}
                </button>
              </div>
              {dialogError && <p className="mt-2 text-sm text-rose-700" role="alert">对话暂时不可用，请刷新后重试</p>}
            </form>
          </div>

          <aside className="bg-white p-5" aria-labelledby="pending-profile-title">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h2 id="pending-profile-title" className="font-bold text-slate-900">待确认更新</h2>
                <p className="mt-1 text-sm text-slate-500">{pendingMessages.length} 条建议</p>
              </div>
              <span className={`rounded-md px-2 py-1 text-xs font-semibold ${
                pendingMessages.length > 0
                  ? "bg-amber-50 text-amber-800"
                  : "bg-emerald-50 text-emerald-700"
              }`}>
                {pendingMessages.length > 0 ? "需确认" : "已同步"}
              </span>
            </div>

            <div className="mt-5 max-h-[390px] space-y-5 overflow-y-auto pr-1">
              {pendingMessages.length === 0 && (
                <div className="flex min-h-52 flex-col items-center justify-center text-center">
                  <CheckCircle2 className="mb-3 h-8 w-8 text-emerald-500" />
                  <p className="font-medium text-slate-700">当前没有待确认更新</p>
                </div>
              )}

              {pendingMessages.map((message) => (
                <div key={message.message_id} className="border-b border-slate-100 pb-5 last:border-0 last:pb-0">
                  <div className="space-y-3">
                    {extractionItems(message.extracted_json).map((item) => (
                      <div key={item.field}>
                        <div className="text-xs font-semibold text-slate-500">{item.label}</div>
                        <div className="mt-1 text-sm leading-6 text-slate-800">{item.value}</div>
                      </div>
                    ))}
                  </div>
                  <button
                    type="button"
                    onClick={() => void handleApply(message.message_id)}
                    disabled={applyingMessageId != null}
                    className="mt-4 flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {applyingMessageId === message.message_id
                      ? <LoaderCircle className="h-4 w-4 animate-spin motion-reduce:animate-none" />
                      : <CheckCircle2 className="h-4 w-4" />}
                    确认更新画像
                  </button>
                </div>
              ))}
            </div>
          </aside>
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-[280px_minmax(0,1fr)]" aria-labelledby="profile-snapshot-title">
        <div className="flex flex-col rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-100">
              <User className="h-7 w-7 text-blue-700" />
            </div>
            <div className="min-w-0">
              <h2 id="profile-snapshot-title" className="truncate text-lg font-bold text-slate-900">{profile.student_name || "学生"}</h2>
              <p className="mt-0.5 text-sm text-slate-500">学号 {profile.student_no || "未设置"}</p>
            </div>
          </div>
          <div className="mt-6">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-slate-600">综合掌握度</span>
              <span className="font-bold tabular-nums text-blue-700">{masteryPercent}%</span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
              <div className="h-full rounded-full bg-blue-600 transition-transform duration-300 motion-reduce:transition-none" style={{ transform: `scaleX(${masteryPercent / 100})`, transformOrigin: "left" }} />
            </div>
          </div>
          <div className="mt-6 border-t border-slate-100 pt-4">
            <div className="text-xs font-semibold text-slate-500">AI 学习建议</div>
            <p className="mt-2 text-sm leading-6 text-slate-700">{profile.ai_suggestions || "完成更多学习活动后生成建议"}</p>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {dimensions.map((dimension) => {
            const Icon = dimension.icon;
            const items = dimension.items.length ? dimension.items : ["待补充"];
            return (
              <article key={dimension.title} className="flex min-h-44 flex-col rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${dimension.bg}`}>
                    <Icon className={`h-4 w-4 ${dimension.color}`} />
                  </div>
                  <h3 className="font-semibold text-slate-900">{dimension.title}</h3>
                </div>
                <div className="mt-4 flex-1 space-y-2">
                  {items.map((item) => (
                    <div key={item} className="flex items-start gap-2 text-sm leading-5 text-slate-700">
                      <span className={`mt-2 h-1.5 w-1.5 shrink-0 rounded-full ${dimension.color.replace("text-", "bg-")}`} />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
                <p className="mt-3 border-t border-slate-100 pt-3 text-xs text-slate-500">{dimension.source}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm" aria-labelledby="profile-history-title">
        <div className="flex items-center gap-3 border-b border-slate-100 px-5 py-4">
          <History className="h-5 w-5 text-blue-600" />
          <div>
            <h2 id="profile-history-title" className="font-bold text-slate-900">画像更新记录</h2>
            <p className="mt-0.5 text-sm text-slate-500">测验、自评与学习反馈</p>
          </div>
          <button
            type="button"
            onClick={() => void loadRecords(profile.profile_id)}
            className="ml-auto flex h-11 w-11 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
            aria-label="刷新更新记录"
            title="刷新更新记录"
          >
            <RefreshCw className={`h-4 w-4 ${loadingRecords ? "animate-spin motion-reduce:animate-none" : ""}`} />
          </button>
        </div>

        <div className="p-5">
          {loadingRecords && updateRecords.length === 0 && (
            <div className="flex min-h-32 items-center justify-center text-sm text-slate-500">
              <LoaderCircle className="mr-2 h-4 w-4 animate-spin motion-reduce:animate-none" />
              加载更新记录
            </div>
          )}
          {!loadingRecords && updateRecords.length === 0 && (
            <div className="flex min-h-32 flex-col items-center justify-center text-center text-sm text-slate-500">
              <History className="mb-2 h-7 w-7 text-slate-300" />
              暂无更新记录
            </div>
          )}
          {updateRecords.length > 0 && (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {updateRecords.map((record) => {
                const createdAt = new Date(record.created_at);
                return (
                  <article key={record.feedback_id} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="text-sm font-semibold text-slate-900">{record.feedback_type_label}</h3>
                        <p className="mt-1 text-xs text-slate-500">{record.course_name}</p>
                      </div>
                      <time className="shrink-0 text-xs tabular-nums text-slate-500">
                        {createdAt.toLocaleDateString("zh-CN", { month: "short", day: "numeric" })}
                      </time>
                    </div>
                    <div className="mt-3 space-y-1 text-sm text-slate-700">
                      {record.quiz_score != null && <p>测验得分：<strong>{formatPercent(record.quiz_score)}</strong></p>}
                      {record.self_mastery != null && <p>自评掌握度：<strong>{formatPercent(record.self_mastery)}</strong></p>}
                      {record.resource_title && <p className="line-clamp-1">关联资源：{record.resource_title}</p>}
                      {record.content && <p className="line-clamp-2 text-slate-600">{record.content}</p>}
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
