import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Home, ShieldQuestion } from "lucide-react";
import { primaryButton, secondaryButton } from "../components/common/ProductUI";

export function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="mx-auto grid min-h-[620px] max-w-[900px] place-items-center">
      <section className="edu-card relative w-full overflow-hidden rounded-[28px] p-10 text-center">
        <div className="absolute inset-0 edu-grid-bg opacity-50" />
        <div className="relative">
          <div className="mx-auto mb-5 grid h-16 w-16 place-items-center rounded-3xl bg-blue-50 text-blue-700 ring-1 ring-blue-100">
            <ShieldQuestion className="h-8 w-8" />
          </div>
          <h1 className="text-[32px] font-black text-slate-950">页面不存在</h1>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-600">你访问的页面不存在或无权限访问，请返回角色首页继续使用 EduAgent Studio。</p>
          <div className="mt-7 flex justify-center gap-3">
            <Link to="/teacher" className={primaryButton}><Home className="h-4 w-4" />返回首页</Link>
            <button onClick={() => navigate(-1)} className={secondaryButton}><ArrowLeft className="h-4 w-4" />返回上一页</button>
          </div>
        </div>
      </section>
    </div>
  );
}
