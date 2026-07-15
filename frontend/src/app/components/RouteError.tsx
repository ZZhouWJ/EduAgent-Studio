import { AlertTriangle, Home, RefreshCw } from "lucide-react";
import { isRouteErrorResponse, useNavigate, useRouteError } from "react-router-dom";

export function RouteError() {
  const error = useRouteError();
  const navigate = useNavigate();
  const status = isRouteErrorResponse(error) ? error.status : 500;

  return (
    <main className="grid min-h-screen place-items-center bg-slate-50 px-5 py-12">
      <section className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-[0_20px_50px_rgba(15,23,42,0.08)]">
        <div className="mx-auto grid h-12 w-12 place-items-center rounded-xl bg-red-50 text-red-600">
          <AlertTriangle className="h-6 w-6" />
        </div>
        <p className="mt-5 text-xs font-black uppercase text-slate-400">错误代码 {status}</p>
        <h1 className="mt-2 text-2xl font-black text-slate-950">页面暂时无法加载</h1>
        <p className="mt-3 text-sm leading-6 text-slate-500">请重试当前页面；若问题持续出现，请返回首页继续其他操作。</p>
        <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
          <button
            onClick={() => window.location.reload()}
            className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 text-sm font-black text-white transition hover:bg-blue-700"
          >
            <RefreshCw className="h-4 w-4" />
            重新加载
          </button>
          <button
            onClick={() => navigate("/", { replace: true })}
            className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 text-sm font-black text-slate-700 transition hover:bg-slate-50"
          >
            <Home className="h-4 w-4" />
            返回首页
          </button>
        </div>
      </section>
    </main>
  );
}
