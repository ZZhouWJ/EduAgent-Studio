import React, { useEffect, useState, useRef } from "react";
import Lottie, { type LottieRefCurrentProps } from "lottie-react";
import { INLINE_LOTTIES, type InlineLottieKey } from "./inlineLotties";

type Source = InlineLottieKey | { url: string };

interface SafeLottieProps {
  /** 内置主题：loading / empty / success / dashboard / teaching / studying */
  source: Source;
  /** 自定义容器 className */
  className?: string;
  /** 是否循环（默认 true） */
  loop?: boolean;
  /** 是否自动播放（默认 true） */
  autoplay?: boolean;
  /** 播放速度，0.5 ~ 1.5 比较克制 */
  speed?: number;
  /** 加载失败/网络不可达时的占位元素（可选） */
  fallback?: React.ReactNode;
}

function useRemoteLottie(url: string) {
  const [data, setData] = useState<object | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    let cancelled = false;
    setData(null);
    setError(false);
    fetch(url)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((j) => {
        if (!cancelled) setData(j);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
    };
  }, [url]);
  return { data, error };
}

/**
 * 通用 Lottie 包装：
 * - 默认使用内联 JSON（0 网络依赖，最稳）
 * - 可选 { url } 从公开 CDN 拉取（Lottie Simple License，无需署名）
 * - 失败/加载中均有占位，不污染布局
 */
export function SafeLottie({
  source,
  className = "h-32 w-32",
  loop = true,
  autoplay = true,
  speed = 1,
  fallback,
}: SafeLottieProps) {
  const ref = useRef<LottieRefCurrentProps | null>(null);

  // 内联模式
  if (typeof source === "string") {
    const data = INLINE_LOTTIES[source as InlineLottieKey];
    return (
      <Lottie
        lottieRef={ref}
        animationData={data}
        loop={loop}
        autoplay={autoplay}
        className={className}
      />
    );
  }

  // 远端模式
  const { data, error } = useRemoteLottie(source.url);
  if (error) {
    return <div className={`${className} flex items-center justify-center`}>{fallback}</div>;
  }
  if (!data) {
    return <div className={`${className} animate-pulse rounded-lg bg-slate-100`} />;
  }
  return (
    <Lottie
      lottieRef={ref}
      animationData={data}
      loop={loop}
      autoplay={autoplay}
      className={className}
    />
  );
}

export default SafeLottie;
