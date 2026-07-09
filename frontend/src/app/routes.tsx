import { createBrowserRouter, Navigate } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Login } from "./pages/Login";
import { AdminAgentConfig } from "./pages/AdminAgentConfig";
import { AdminAudit } from "./pages/AdminAudit";
import { AdminCosts } from "./pages/AdminCosts";
import { AdminCourses } from "./pages/AdminCourses";
import { AdminDashboard } from "./pages/AdminDashboard";
import { AdminGovernance } from "./pages/AdminGovernance";
import { AdminLogs } from "./pages/AdminLogs";
import { AdminModelConfig } from "./pages/AdminModelConfig";
import { AdminPrompts } from "./pages/AdminPrompts";
import { AdminUsers } from "./pages/AdminUsers";
import { AgentWorkbench } from "./pages/AgentWorkbench";
import { LearningAnalytics } from "./pages/LearningAnalytics";
import { LearningFeedback } from "./pages/LearningFeedback";
import { NotFound } from "./pages/NotFound";
import { ResourceLibrary } from "./pages/ResourceLibrary";
import { StudentDashboard } from "./pages/StudentDashboard";
import { StudentLearningPath } from "./pages/StudentLearningPath";
import { StudentProfile } from "./pages/StudentProfile";
import { StudentTasks } from "./pages/StudentTasks";
import { StudentTutor } from "./pages/StudentTutor";
import { TeacherCourses } from "./pages/TeacherCourses";
import { TeacherDashboard } from "./pages/TeacherDashboard";
import { TeacherKnowledgeBase } from "./pages/TeacherKnowledgeBase";
import { TeacherReview } from "./pages/TeacherReview";
import { TeacherTasks } from "./pages/TeacherTasks";

export const router = createBrowserRouter(
  [
    {
      path: "/login",
      Component: Login,
    },
    {
      path: "/",
      Component: Layout,
      children: [
        { index: true, element: <Navigate to="/teacher" replace /> },

        { path: "student", Component: StudentDashboard },
        { path: "student/profile", Component: StudentProfile },
        { path: "student/learning-path", Component: StudentLearningPath },
        { path: "student/tasks", Component: StudentTasks },
        { path: "student/resources", Component: ResourceLibrary },
        { path: "student/tutor", Component: StudentTutor },
        { path: "student/feedback", Component: LearningFeedback },
        { path: "student/report", Component: LearningAnalytics },

        { path: "teacher", Component: TeacherDashboard },
        { path: "teacher/courses", Component: TeacherCourses },
        { path: "teacher/students", Component: StudentProfile },
        { path: "teacher/agent-workbench", Component: AgentWorkbench },
        { path: "teacher/resources", Component: ResourceLibrary },
        { path: "teacher/review", Component: TeacherReview },
        { path: "teacher/tasks", Component: TeacherTasks },
        { path: "teacher/knowledge-base", Component: TeacherKnowledgeBase },
        { path: "teacher/analytics", Component: LearningAnalytics },

        { path: "admin", Component: AdminDashboard },
        { path: "admin/users", Component: AdminUsers },
        { path: "admin/courses", Component: AdminCourses },
        { path: "admin/resources", Component: ResourceLibrary },
        { path: "admin/model-config", Component: AdminModelConfig },
        { path: "admin/agent-config", Component: AdminAgentConfig },
        { path: "admin/prompts", Component: AdminPrompts },
        { path: "admin/audit", Component: AdminAudit },
        { path: "admin/costs", Component: AdminCosts },
        { path: "admin/governance", Component: AdminGovernance },
        { path: "admin/logs", Component: AdminLogs },

        { path: "agent-workbench", element: <Navigate to="/teacher/agent-workbench" replace /> },
        { path: "student-profile", element: <Navigate to="/student/profile" replace /> },
        { path: "resource-library", element: <Navigate to="/teacher/resources" replace /> },
        { path: "teacher-review", element: <Navigate to="/teacher/review" replace /> },
        { path: "learning-feedback", element: <Navigate to="/student/feedback" replace /> },
        { path: "learning-analytics", element: <Navigate to="/teacher/analytics" replace /> },
        { path: "*", Component: NotFound },
      ],
    },
  ],
  {
    future: {
      v7_startTransition: true,
      v7_relativeSplatPath: true,
    },
  },
);

