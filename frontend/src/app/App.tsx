import { RouterProvider } from "react-router";
import { router } from "./routes";
import { useRouterGuard } from "@/lib/router-guard";

function GuardedApp() {
  useRouterGuard()
  return <RouterProvider router={router} />;
}

export default function App() {
  return <GuardedApp />;
}
