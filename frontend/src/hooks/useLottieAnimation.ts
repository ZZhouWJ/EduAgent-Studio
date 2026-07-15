import { useEffect, useRef, useState, useCallback } from "react";
import type { AnimationItem } from "lottie-web";

/**
 * useLottieAnimation —— 懒加载 lottie-web 的轻量版
 *
 * 行为：
 *  - Dashboard 挂载后才动态 import lottie_light（168 KB，gzip ~60 KB）
 *  - 自动尊重 prefers-reduced-motion
 *  - 加载失败时静默降级（不破图）
 *  - 组件卸载时 destroy()，无内存泄漏
 */
export function useLottieAnimation(opts: {
  src: string;
  loop?: boolean;
}) {
  const { src, loop = true } = opts;
  const containerRef = useRef<HTMLDivElement>(null);
  const animRef = useRef<AnimationItem | null>(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(false);
  const [reduceMotion, setReduceMotion] = useState(false);

  // 检测降级偏好
  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduceMotion(mq.matches);
    const onChange = (e: MediaQueryListEvent) => setReduceMotion(e.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  // 懒加载 lottie-web light 版 + 播放
  useEffect(() => {
    if (!src || !containerRef.current || reduceMotion) return;
    let cancelled = false;
    setReady(false);
    setError(false);

    import("lottie-web/build/player/lottie_light")
      .then((mod) => {
        if (cancelled) return;
        const lottie = mod.default;
        try {
          const anim = lottie.loadAnimation({
            container: containerRef.current!,
            renderer: "svg",
            loop,
            autoplay: true,
            path: src,
            rendererSettings: {
              preserveAspectRatio: "xMidYMid meet",
              progressiveLoad: true,
            },
          });
          animRef.current = anim;
          anim.addEventListener("DOMLoaded", () => { if (!cancelled) setReady(true); });
          anim.addEventListener("data_failed", () => { if (!cancelled) setError(true); });
        } catch {
          if (!cancelled) setError(true);
        }
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });

    return () => {
      cancelled = true;
      if (animRef.current) {
        try { animRef.current.destroy(); } catch { /* noop */ }
        animRef.current = null;
      }
    };
  }, [src, loop, reduceMotion]);

  const clear = useCallback(() => {
    if (animRef.current) {
      try { animRef.current.destroy(); } catch { /* noop */ }
      animRef.current = null;
    }
  }, []);

  return {
    containerRef,
    ready,
    error,
    reduceMotion,
    clear,
  };
}
