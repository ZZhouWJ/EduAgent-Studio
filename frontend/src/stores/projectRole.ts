/**
 * Project-scoped role store.
 *
 * Manages the current project's members list and derives the current user's
 * project_role from it. Used for button-level permission checks on project
 * detail pages (ProjectDetail.vue, TaskDetail.vue, etc.).
 *
 * Usage:
 *   const projectRoleStore = useProjectRoleStore()
 *   await projectRoleStore.loadMembers(projectId)
 *   const role = projectRoleStore.currentUserProjectRole(userId)
 */

import { defineStore } from "pinia"
import { ref, computed } from "vue"
import type { ProjectMember } from "@/api/projects"
import type { ProjectRole } from "@/utils/permission"

export const useProjectRoleStore = defineStore("projectRole", () => {
  // Maps projectId -> members list
  const membersMap = ref<Map<number, ProjectMember[]>>(new Map())
  const loadingProjectId = ref<number | null>(null)

  /** Get members list for a specific project */
  function getMembers(projectId: number): ProjectMember[] {
    return membersMap.value.get(projectId) ?? []
  }

  /** Get the current user's project_role for a specific project */
  function getCurrentUserProjectRole(projectId: number, userId: number): ProjectRole | null {
    const members = getMembers(projectId)
    const member = members.find(m => m.user_id === userId)
    if (!member) return null
    return member.project_role as ProjectRole
  }

  /** Check if the current user is a leader/teacher for a project */
  function isProjectAdmin(projectId: number, userId: number): boolean {
    const role = getCurrentUserProjectRole(projectId, userId)
    return role === "leader" || role === "teacher"
  }

  /** Check if the current user is a reviewer for a project */
  function isReviewer(projectId: number, userId: number): boolean {
    return getCurrentUserProjectRole(projectId, userId) === "reviewer"
  }

  /** Check if the current user is a member for a project */
  function isMember(projectId: number, userId: number): boolean {
    const role = getCurrentUserProjectRole(projectId, userId)
    return role !== null && role !== undefined
  }

  /** Cache members for a project (called after loading members from API) */
  function setMembers(projectId: number, members: ProjectMember[]) {
    membersMap.value.set(projectId, members)
  }

  /** Remove cached data for a project (e.g. on logout) */
  function clearProject(projectId: number) {
    membersMap.value.delete(projectId)
  }

  /** Clear all cached data */
  function clearAll() {
    membersMap.value.clear()
  }

  return {
    membersMap,
    loadingProjectId,
    getMembers,
    getCurrentUserProjectRole,
    isProjectAdmin,
    isReviewer,
    isMember,
    setMembers,
    clearProject,
    clearAll
  }
})
