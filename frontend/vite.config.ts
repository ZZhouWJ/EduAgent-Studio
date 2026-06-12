import { resolve } from "node:path"
import vue from "@vitejs/plugin-vue"
import { defineConfig, loadEnv } from "vite"

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "") as ImportMetaEnv
  const {
    VITE_PUBLIC_PATH,
    VITE_API_BASE_URL,
    VITE_API_PROXY_TARGET,
  } = env

  const proxyTarget = VITE_API_PROXY_TARGET || VITE_API_BASE_URL || "http://127.0.0.1:8000"

  return {
    base: VITE_PUBLIC_PATH || "/",
    resolve: {
      alias: {
        "@": resolve(__dirname, "src")
      }
    },
    server: {
      host: true,
      port: 5173,
      strictPort: false,
      open: false,
      cors: true,
      proxy: {
        "/api": {
          target: proxyTarget,
          changeOrigin: true
        }
      }
    },
    build: {
      reportCompressedSize: false,
      chunkSizeWarningLimit: 2048
    },
    esbuild:
      mode === "development"
        ? undefined
        : {
            pure: ["console.log"],
            drop: ["debugger"],
            legalComments: "none"
          },
    plugins: [vue()]
  }
})
