/**
 * Frontend permission utilities.
 *
 * Security principle: frontend permission hiding is UX only.
 * All backend API endpoints MUST enforce their own permission checks independently.
 * Never hard-code user IDs or token values.
 */

import type { UserInfo } from "@/stores/user"
import type { ProjectMember } from "@/api/projects"

// ---------------------------------------------------------------------------
// Global / System-level helpers
// ---------------------------------------------------------------------------

/** System-level role codes stored in users.roles[] */
export type GlobalRole = "admin" | "teacher" | "student_member" | "project_leader"

/** Project-scoped role codes from project_members.project_role */
export type ProjectRole = "leader" | "teacher" | "reviewer" | "member"

/** Maps system-level role codes to human-readable labels */
export const GLOBAL_ROLE_LABEL: Record<string, string> = {
  admin: "系统管理员",
  teacher: "教师",
  student_member: "学生成员",
  project_leader: "项目负责人"
}

/** Maps project-scoped role codes to human-readable labels */
export const PROJECT_ROLE_LABEL: Record<string, string> = {
  leader: "项目负责人",
  teacher: "指导教师",
  reviewer: "审核员",
  member: "成员"
}

/** Returns whether the user has any of the given global/system-level roles */
export function hasAnyGlobalRole(user: UserInfo | null, roles: GlobalRole[]): boolean {
  if (!user) return false
  return roles.some(r => user.roles?.includes(r))
}

/** Returns whether the user has the admin global role */
export function isAdmin(user: UserInfo | null): boolean {
  return hasAnyGlobalRole(user, ["admin"])
}

/** Returns whether the user has the teacher global role */
export function isTeacher(user: UserInfo | null): boolean {
  return hasAnyGlobalRole(user, ["teacher"])
}

/** Returns whether the user has the student_member global role */
export function isStudentMember(user: UserInfo | null): boolean {
  return hasAnyGlobalRole(user, ["student_member"])
}

/** Returns whether the user has the project_leader global role */
export function isProjectLeaderGlobal(user: UserInfo | null): boolean {
  return hasAnyGlobalRole(user, ["project_leader"])
}

/**
 * Checks whether a permission code is present in the user's permissions list.
 * Permission codes follow the pattern "module:action", e.g. "project:view_all".
 */
export function hasPermission(user: UserInfo | null, permission: string): boolean {
  if (!user) return false
  // @ts-ignore – permissions may be populated from /api/auth/me
  const perms: string[] = (user as any).permissions ?? []
  return perms.includes(permission)
}

// ---------------------------------------------------------------------------
// Project-scoped role helpers
// ---------------------------------------------------------------------------

/**
 * Returns the current user's project_role from the project members list.
 * Returns null if the user is not a member of the project.
 */
export function getProjectRole(members: ProjectMember[], userId: number): ProjectRole | null {
  const member = members.find(m => m.user_id === userId)
  if (!member) return null
  return member.project_role as ProjectRole
}

/** Returns true if the project_role is 'leader' */
export function isProjectLeader(projectRole: ProjectRole | null): boolean {
  return projectRole === "leader"
}

/** Returns true if the project_role is 'teacher' */
export function isProjectTeacher(projectRole: ProjectRole | null): boolean {
  return projectRole === "teacher"
}

/** Returns true if the project_role is 'reviewer' */
export function isProjectReviewer(projectRole: ProjectRole | null): boolean {
  return projectRole === "reviewer"
}

/** Returns true if the project_role is 'member' (ordinary member, not leader/teacher/reviewer) */
export function isProjectMember(projectRole: ProjectRole | null): boolean {
  return projectRole === "member"
}

/** Returns true if the project_role is leader OR teacher (can manage project-level settings) */
export function isProjectAdmin(projectRole: ProjectRole | null): boolean {
  return projectRole === "leader" || projectRole === "teacher"
}

// ---------------------------------------------------------------------------
// Composite permission helpers
// ---------------------------------------------------------------------------

/**
 * Whether the user can manage project-level settings (edit, archive).
 * Admins can manage all projects.
 * Within a project, only leader or teacher can.
 */
export function canManageProject(
  user: UserInfo | null,
  projectRole: ProjectRole | null
): boolean {
  if (isAdmin(user)) return true
  return isProjectAdmin(projectRole)
}

/**
 * Whether the user can add/remove project members or change their roles.
 * Admins can always do this.
 * Within a project, only leader or teacher can.
 */
export function canManageMembers(
  user: UserInfo | null,
  projectRole: ProjectRole | null
): boolean {
  if (isAdmin(user)) return true
  return isProjectAdmin(projectRole)
}

/**
 * Whether the user can create tasks within a project.
 * Admins, project leaders, and project teachers can always create tasks.
 */
export function canCreateTask(
  user: UserInfo | null,
  projectRole: ProjectRole | null
): boolean {
  if (isAdmin(user)) return true
  return isProjectAdmin(projectRole)
}

/**
 * Whether the user can edit a task.
 * Admins can always edit.
 * Within a project, leader and teacher can always edit.
 * Ordinary members may also edit tasks depending on business rules
 * (we allow it here; the backend enforces the real check).
 */
export function canEditTask(
  user: UserInfo | null,
  projectRole: ProjectRole | null
): boolean {
  if (isAdmin(user)) return true
  return isProjectAdmin(projectRole)
}

/**
 * Whether the user can trigger AI generation within a project.
 * Any logged-in project member can generate.
 */
export function canGenerateOutput(
  user: UserInfo | null,
  projectRole: ProjectRole | null
): boolean {
  if (!user) return false
  if (isAdmin(user)) return true
  return projectRole !== null
}

/**
 * Whether the user can edit an output.
 * Admins can always edit.
 * Within a project, leader and teacher can edit any output.
 * Ordinary members and reviewers can edit outputs they created
 * (full enforcement is on the backend; we show the button).
 */
export function canEditOutput(
  user: UserInfo | null,
  projectRole: ProjectRole | null
): boolean {
  if (isAdmin(user)) return true
  return isProjectAdmin(projectRole)
}

/**
 * Whether the user can add comments to an output.
 * Any project member (including reviewer) can comment.
 */
export function canCommentOutput(
  user: UserInfo | null,
  projectRole: ProjectRole | null
): boolean {
  if (!user) return false
  if (isAdmin(user)) return true
  return projectRole !== null
}

/**
 * Whether the user can submit a review for an output.
 * Any project member can submit a review request.
 */
export function canSubmitReview(
  user: UserInfo | null,
  projectRole: ProjectRole | null
): boolean {
  if (!user) return false
  if (isAdmin(user)) return true
  return projectRole !== null
}

/**
 * Whether the user can complete/review an output (act as reviewer).
 * Admins can review any output.
 * Within a project, only leader, teacher, or reviewer can complete reviews.
 */
export function canCompleteReview(
  user: UserInfo | null,
  projectRole: ProjectRole | null
): boolean {
  if (isAdmin(user)) return true
  return projectRole === "leader" || projectRole === "teacher" || projectRole === "reviewer"
}

/**
 * Whether the user can adopt an output as a project artifact.
 * Admins, project leaders, and project teachers can adopt.
 * Reviewers and ordinary members cannot adopt by default.
 */
export function canAdoptOutput(
  user: UserInfo | null,
  projectRole: ProjectRole | null
): boolean {
  if (isAdmin(user)) return true
  return isProjectAdmin(projectRole)
}

/**
 * Whether the user can merge branches.
 * Admins, project leaders, and project teachers can merge.
 * Reviewers and ordinary members cannot merge.
 */
export function canMergeBranches(
  user: UserInfo | null,
  projectRole: ProjectRole | null
): boolean {
  if (isAdmin(user)) return true
  return isProjectAdmin(projectRole)
}

/**
 * Whether the user can manage AI models (view/edit model configurations).
 * Only admins can access model management pages.
 */
export function canManageModels(user: UserInfo | null): boolean {
  return isAdmin(user)
}

/**
 * Whether the user can manage users (view user list, assign roles).
 * Only admins can access user management pages.
 */
export function canManageUsers(user: UserInfo | null): boolean {
  return isAdmin(user)
}

/**
 * Whether the user can view operation logs.
 * Only admins can view system-wide operation logs.
 */
export function canViewOperationLogs(user: UserInfo | null): boolean {
  return isAdmin(user)
}

/**
 * Whether the user can view login logs.
 * Only admins can view login logs.
 */
export function canViewLoginLogs(user: UserInfo | null): boolean {
  return isAdmin(user)
}

/**
 * Whether the user can view invocation/cost statistics.
 * Admins can view all.
 * Project members can view costs/invocations for their own projects.
 */
export function canViewCosts(
  user: UserInfo | null,
  projectRole: ProjectRole | null
): boolean {
  if (!user) return false
  if (isAdmin(user)) return true
  return projectRole !== null
}
