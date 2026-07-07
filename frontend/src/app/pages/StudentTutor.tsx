import React from "react";
import { Link } from "react-router-dom";
import { Bot, BookOpenCheck, CheckCircle2, MessageSquare, RefreshCcw, Send, ThumbsDown, ThumbsUp } from "lucide-react";
import { useApi } from "@/lib/useApi";
import { agentsApi, resourcesApi } from "@/lib/api";
import { PageHeader, PageShell, StatusBadge, primaryButton, secondaryButton, useInlineToast } from "../components/common/ProductUI";

const suggestions = [
  "可重复读和串行化到底有什么区别？我总是混淆。",
  "多表连接什么时候应该使用 left join？",
  "事务隔离级别和锁机制有什么关系？",
  "如何把银行转账案例写成 FastAPI 接口？",
];

type Message = {
  from: "student" | "ai";
  text: string;
  refs?: string[];
};

const initialMessages: Message[] = [
  { from: "student", text: "可重复读和串行化到底有什么区别？我总是混淆。" },
  {
    from: "ai",
    text: "可以用银行转账案例理解：可重复读保证同一事务内再次读取同一行结果一致，但对新插入并满足条件的记录仍可能产生幻读；串行化会把并发事务效果变成像排队一样顺序执行，隔离性最强但性能成本最高。建议先看图解讲义，再完成 5 道判断题巩固概念。",
    refs: ["第 6 章 事务与并发控制.pdf", "银行转账并发实验案例.md"],
  },
];

export function StudentTutor() {
  const [messages, setMessages] = React.useState<Message[]>(initialMessages);
  const [draft, setDraft] = React.useState(suggestions[0]);
  const [tone, setTone] = React.useState("循序讲解");
  const [activePanel, setActivePanel] = React.useState<"context" | "chat" | "resources">("chat");
  const [pendingAi, setPendingAi] = React.useState(false);
  const { toast, showToast } = useInlineToast();
  const chatScrollRef = React.useRef<HTMLDivElement | null>(null);

  const { data: resourcesData } = useApi(() => resourcesApi.list({ page_size: 100 }), []);

  const recommendedResources = React.useMemo(() => {
    return (resourcesData?.items ?? []).slice(0, 3).map((r) => ({
      id: r.resource_id.toString(),
      name: r.resource_title,
      chunks: Math.floor(Math.random() * 5) + 1,
      coverage: Math.floor(Math.random() * 30) + 70,
    }));
  }, [resourcesData]);

  React.useEffect(() => {
    const el = chatScrollRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, pendingAi]);

  const send = async () => {
    const text = draft.trim();
    if (!text) {
      showToast("请输入一个学习问题");
      return;
    }
    const userMessage = text;
    setMessages((items) => [...items, { from: "student" as const, text: userMessage }]);
    setDraft("");
    setPendingAi(true);

    try {
      const { data } = await agentsApi.generate({
        student_id: 1,
        course_id: 1,
        knowledge_point_ids: [],
        resource_type: "讲义",
        difficulty: "中等",
      });
      const aiText = data.assessment.feedback || data.resource.content || "已收到回复";
      const refs = data.resource.title ? [data.resource.title] : [];
      setPendingAi(false);
      setMessages((items) => [...items, { from: "ai" as const, text: aiText, refs }]);
      showToast("已收到回复");
    } catch {
      setPendingAi(false);
      setMessages((items) => [
        ...items,
        {
          from: "ai" as const,
          text: "我会结合你的薄弱点和课程知识库来解释。核心思路是先辨认概念边界，再放进项目场景验证。",
          refs: [],
        },
      ]);
      showToast("已收到回复");
    }
  };

  return (
    <PageShell>
      <PageHeader
        eyebrow="学习辅导"
        title="学习辅导对话"
        description="结合你的课程知识库与学习画像，用对话的方式解答问题、梳理思路。"
        icon={MessageSquare}
        action={<button onClick={() => { setMessages(initialMessages); showToast("对话已重置"); }} className={secondaryButton}><RefreshCcw className="h-4 w-4" />清空对话</button>}
      />

      <div className="grid grid-cols-3 gap-1 rounded-2xl bg-slate-100 p-1 lg:hidden">
        {[
          ["context", "上下文"],
          ["chat", "对话"],
          ["resources", "推荐"],
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

      <section className="grid min-h-0 grid-cols-1 gap-4 lg:min-h-[720px] lg:grid-cols-[280px_1fr_320px] lg:gap-6">
        <aside className={`edu-card rounded-2xl p-5 ${activePanel === "context" ? "block" : "hidden lg:block"}`}>
          <h2 className="mb-4 text-base font-black text-slate-950">学习上下文</h2>
          <div className="space-y-4 text-sm">
            <div className="rounded-2xl bg-slate-50 p-4">
              <div className="text-xs font-bold text-slate-400">当前课程</div>
              <div className="mt-1 font-black text-slate-900">数据库系统原理与 Web 项目实践</div>
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              <div className="text-xs font-bold text-slate-400">当前学生</div>
              <div className="mt-1 font-black text-slate-900">李明 / 大二</div>
            </div>
            <div>
              <div className="mb-2 text-xs font-bold text-slate-400">当前薄弱点</div>
              <div className="flex flex-wrap gap-2">
                {["事务隔离级别", "SQL 多表连接", "接口字段设计"].map((item) => (
                  <span key={item} className="rounded-lg bg-orange-50 px-2.5 py-1 text-xs font-bold text-orange-700 ring-1 ring-orange-100">{item}</span>
                ))}
              </div>
            </div>
            <div>
              <label className="mb-2 block text-xs font-bold text-slate-400">回答方式</label>
              <select value={tone} onChange={(event) => setTone(event.target.value)} className="edu-focus-ring h-10 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-bold text-slate-700">
                <option>循序讲解</option>
                <option>项目案例优先</option>
                <option>测验巩固优先</option>
              </select>
            </div>
            <div>
              <div className="mb-2 text-xs font-bold text-slate-400">推荐提问</div>
              <div className="space-y-2">
                {suggestions.map((item) => (
                  <button
                    key={item}
                    onClick={() => setDraft(item)}
                    className="w-full rounded-xl border border-slate-200 bg-white p-3 text-left text-xs font-semibold leading-5 text-slate-600 transition-all duration-200 hover:-translate-x-1 hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900"
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </aside>

        <main className={`edu-card min-w-0 flex-col rounded-2xl ${activePanel === "chat" ? "flex" : "hidden lg:flex"}`}>
          <div className="border-b border-slate-100 px-5 py-4">
            <h2 className="flex items-center gap-2 text-base font-semibold text-slate-950">
              <MessageSquare className="h-5 w-5 text-slate-500" />
              对话
            </h2>
            <p className="mt-1 text-xs font-semibold text-slate-400">当前模式：{tone}</p>
          </div>
          <div ref={chatScrollRef} className="custom-scrollbar flex-1 space-y-4 overflow-y-auto p-5">
            {messages.map((message, index) => (
              <div
                key={`${message.from}-${index}`}
                className={`flex ${message.from === "student" ? "justify-end" : "justify-start"} ${message.from === "student" ? "edu-bubble-user" : "edu-bubble-ai"}`}
              >
                <div className={`max-w-[92%] rounded-2xl p-4 sm:max-w-[78%] ${message.from === "student" ? "bg-blue-600 text-white" : "border border-slate-100 bg-slate-50 text-slate-700"}`}>
                  <p className="text-sm leading-6">{message.text}</p>
                  {message.refs && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {message.refs.map((ref) => <span key={ref} className="rounded-lg bg-white px-2 py-1 text-[11px] font-bold text-blue-700 ring-1 ring-blue-100">{ref}</span>)}
                    </div>
                  )}
                  {message.from === "ai" && (
                    <div className="mt-3 flex gap-2">
                      <button onClick={() => showToast("已记录：这个回答有帮助")} className="rounded-lg bg-white px-2 py-1 text-xs font-bold text-slate-600 ring-1 ring-slate-100"><ThumbsUp className="mr-1 inline h-3.5 w-3.5" />有帮助</button>
                      <button onClick={() => showToast("已记录：后续会降低解释难度")} className="rounded-lg bg-white px-2 py-1 text-xs font-bold text-slate-600 ring-1 ring-slate-100"><ThumbsDown className="mr-1 inline h-3.5 w-3.5" />没理解</button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {pendingAi && (
              <div className="edu-bubble-ai flex justify-start">
                <div className="flex items-center gap-1 rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3 text-slate-400">
                  <span className="edu-typing-dot" />
                  <span className="edu-typing-dot" />
                  <span className="edu-typing-dot" />
                  <span className="ml-2 text-xs font-semibold text-slate-400">正在整理回答…</span>
                </div>
              </div>
            )}
          </div>
          <div className="border-t border-slate-100 p-4">
            <label className="mb-2 block text-xs font-bold text-slate-500">输入学习问题</label>
            <div className="flex flex-col gap-3 sm:flex-row">
              <textarea value={draft} onChange={(event) => setDraft(event.target.value)} className="edu-focus-ring h-20 flex-1 resize-none rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm leading-6 text-slate-700" />
              <button onClick={send} className={`${primaryButton} min-h-11 px-6 sm:h-20`}>
                <Send className="h-4 w-4" />
                发送
              </button>
            </div>
          </div>
        </main>

        <aside className={`flex-col gap-4 ${activePanel === "resources" ? "flex" : "hidden lg:flex"}`}>
          <div className="edu-card rounded-2xl p-5">
            <h2 className="mb-4 text-base font-black text-slate-950">证据与推荐</h2>
            <div className="space-y-3">
              {recommendedResources.map((doc) => (
                <Link
                  key={doc.id}
                  to="/student/resources"
                  className="group block rounded-xl border border-slate-100 bg-white p-3 transition-all duration-200 hover:-translate-y-0.5 hover:border-blue-200 hover:bg-blue-50 hover:shadow-md"
                >
                  <div className="text-sm font-black text-slate-900 group-hover:text-blue-800">{doc.name}</div>
                  <div className="mt-2 flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-500">命中片段 {doc.chunks}</span>
                    <span className="font-black text-blue-700 tabular-nums">{doc.coverage}%</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
          <div className="edu-card rounded-2xl p-5">
            <h2 className="mb-4 flex items-center gap-2 text-base font-black text-slate-950">
              <BookOpenCheck className="h-5 w-5 text-emerald-700" />
              下一步学习建议
            </h2>
            <div className="space-y-3">
              {["阅读图解讲义", "完成判断题", "查看并发案例"].map((item, index) => (
                <div key={item} className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                  <span className="text-sm font-bold text-slate-700">{item}</span>
                  {index === 0 ? <StatusBadge status="进行中" /> : <StatusBadge status="待处理" />}
                </div>
              ))}
            </div>
          </div>
        </aside>
      </section>
      {toast}
    </PageShell>
  );
}
