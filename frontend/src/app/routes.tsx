import { createBrowserRouter, Navigate, useNavigate } from "react-router-dom";
import { Layout } from "./components/Layout";
import { RouteError } from "./components/RouteError";
import { useAuthStore } from "@/stores/auth";
import { useEffect } from "react";

function RootRedirect() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const roles = user?.roles ?? [];
  useEffect(() => {
    if (roles.includes("admin")) { navigate("/admin", { replace: true }); }
    else if (roles.includes("teacher")) { navigate("/teacher", { replace: true }); }
    else { navigate("/student", { replace: true }); }
  }, [roles, navigate]);
  return null;
}

export const router = createBrowserRouter(
  [
    {
      path: "/login",
      errorElement: <RouteError />,
      lazy: async () => ({ Component: (await import("./pages/Login")).Login }),
    },
    {
      path: "/",
      Component: Layout,
      errorElement: <RouteError />,
      children: [
        { index: true, element: <RootRedirect /> },

        { path: "student", lazy: async () => ({ Component: (await import("./pages/StudentTutor")).StudentTutor }) },
        { path: "student/home", lazy: async () => ({ Component: (await import("./pages/StudentDashboard")).StudentDashboard }) },
        { path: "student/profile", lazy: async () => ({ Component: (await import("./pages/StudentProfile")).StudentProfile }) },
        { path: "student/learning-path", lazy: async () => ({ Component: (await import("./pages/StudentLearningPath")).StudentLearningPath }) },
        { path: "student/tasks", lazy: async () => ({ Component: (await import("./pages/StudentTasks")).StudentTasks }) },
        { path: "student/resources", lazy: async () => ({ Component: (await import("./pages/ResourceLibrary")).ResourceLibrary }) },
        { path: "student/tutor", lazy: async () => ({ Component: (await import("./pages/StudentTutor")).StudentTutor }) },
        { path: "student/feedback", lazy: async () => ({ Component: (await import("./pages/LearningFeedback")).LearningFeedback }) },
        { path: "student/report", lazy: async () => ({ Component: (await import("./pages/LearningAnalytics")).LearningAnalytics }) },

        { path: "teacher", lazy: async () => ({ Component: (await import("./pages/TeacherDashboard")).TeacherDashboard }) },
        { path: "teacher/courses", lazy: async () => ({ Component: (await import("./pages/TeacherCourses")).TeacherCourses }) },
        { path: "teacher/students", lazy: async () => ({ Component: (await import("./pages/TeacherStudents")).TeacherStudents }) },
        { path: "teacher/resources", lazy: async () => ({ Component: (await import("./pages/ResourceLibrary")).ResourceLibrary }) },
        { path: "teacher/review", lazy: async () => ({ Component: (await import("./pages/TeacherReview")).TeacherReview }) },
        { path: "teacher/tasks", lazy: async () => ({ Component: (await import("./pages/TeacherTasks")).TeacherTasks }) },
        { path: "teacher/knowledge-base", lazy: async () => ({ Component: (await import("./pages/TeacherKnowledgeBase")).TeacherKnowledgeBase }) },
        { path: "teacher/analytics", lazy: async () => ({ Component: (await import("./pages/LearningAnalytics")).LearningAnalytics }) },

        { path: "admin", lazy: async () => ({ Component: (await import("./pages/AdminDashboard")).AdminDashboard }) },
        { path: "admin/users", lazy: async () => ({ Component: (await import("./pages/AdminUsers")).AdminUsers }) },
        { path: "admin/courses", lazy: async () => ({ Component: (await import("./pages/AdminCourses")).AdminCourses }) },
        { path: "admin/resources", lazy: async () => ({ Component: (await import("./pages/ResourceLibrary")).ResourceLibrary }) },
        { path: "admin/knowledge-base", lazy: async () => ({ Component: (await import("./pages/TeacherKnowledgeBase")).TeacherKnowledgeBase }) },
        { path: "admin/model-config", lazy: async () => ({ Component: (await import("./pages/AdminModelConfig")).AdminModelConfig }) },
        { path: "admin/agent-config", lazy: async () => ({ Component: (await import("./pages/AdminAgentConfig")).AdminAgentConfig }) },
        { path: "admin/prompts", lazy: async () => ({ Component: (await import("./pages/AdminPrompts")).AdminPrompts }) },
        { path: "admin/audit", lazy: async () => ({ Component: (await import("./pages/AdminAudit")).AdminAudit }) },
        { path: "admin/costs", lazy: async () => ({ Component: (await import("./pages/AdminCosts")).AdminCosts }) },
        { path: "admin/governance", lazy: async () => ({ Component: (await import("./pages/AdminGovernance")).AdminGovernance }) },
        { path: "admin/logs", lazy: async () => ({ Component: (await import("./pages/AdminLogs")).AdminLogs }) },

        { path: "student-profile", element: <Navigate to="/student/profile" replace /> },
        { path: "resource-library", element: <Navigate to="/teacher/resources" replace /> },
        { path: "teacher-review", element: <Navigate to="/teacher/review" replace /> },
        { path: "learning-feedback", element: <Navigate to="/student/feedback" replace /> },
        { path: "learning-analytics", element: <Navigate to="/teacher/analytics" replace /> },
        { path: "*", lazy: async () => ({ Component: (await import("./pages/NotFound")).NotFound }) },
      ],
    },
  ],
  {
    future: {
      v7_relativeSplatPath: true,
    },
  },
);
