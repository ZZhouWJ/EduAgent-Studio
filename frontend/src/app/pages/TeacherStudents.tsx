import React, { useState } from "react"
import { User, Target, Book, Brain, Library, AlertTriangle, XCircle, Clock, Wrench, ChevronLeft, GraduationCap } from "lucide-react"
import { useApi } from "@/lib/useApi"
import { profilesApi, type ProfileDetail } from "@/lib/api"

function masteryColor(score: number) {
  if (score >= 0.75) return "bg-emerald-50 text-emerald-700 border-emerald-200"
  if (score >= 0.4) return "bg-yellow-50 text-yellow-700 border-yellow-200"
  return "bg-red-50 text-red-700 border-red-200"
}

function MasteryBadge({ score }: { score: number }) {
  return (
    <span className={`text-xs font-bold px-2 py-0.5 rounded border ${masteryColor(score)}`}>
      {Math.round(score * 100)}%
    </span>
  )
}

/** 单个学生卡片 */
function StudentCard({ profile, selected, onClick }: {
  profile: ProfileDetail
  selected: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-2xl p-4 border transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md ${
        selected
          ? "bg-blue-50 border-blue-300 shadow-md ring-2 ring-blue-200"
          : "bg-white border-slate-100 shadow-sm hover:border-blue-200"
      }`}
    >
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
          <User className="w-5 h-5 text-blue-600" />
        </div>
        <MasteryBadge score={profile.mastery_score ?? 0} />
      </div>
      <div className="font-bold text-slate-900 text-sm mb-1">
        {profile.student_name || "未知姓名"}
      </div>
      <div className="text-xs text-slate-500 space-y-0.5">
        <div>学号：{profile.student_no || "—"}</div>
        <div className="truncate">{profile.course_name || "未分配课程"}</div>
      </div>
      {profile.weak_points && profile.weak_points.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          {profile.weak_points.slice(0, 2).map((wp: any, i: number) => (
            <span key={i} className="text-xs px-1.5 py-0.5 rounded bg-red-50 text-red-600 border border-red-100">
              {typeof wp === "string" ? wp : (wp.kp_name || wp.name || `kp#${wp.kp_id}`)}
            </span>
          ))}
          {profile.weak_points.length > 2 && (
            <span className="text-xs px-1.5 py-0.5 rounded bg-slate-50 text-slate-500">
              +{profile.weak_points.length - 2}
            </span>
          )}
        </div>
      )}
    </button>
  )
}

/** 学生详细画像（只读，只截取与 StudentProfile 兼容的部分展示） */
function ProfileDetailPanel({ profile, onBack }: { profile: ProfileDetail; onBack: () => void }) {
  // 规范化：数据库返回 weak_points 为字符串数组，strong_points 为对象数组
  const weakPoints: any[] = (profile.weak_points ?? []).map((wp: any) =>
    typeof wp === "string" ? { kp_name: wp, mastery_level: null } : wp
  )
  const strongPoints: any[] = (profile.strong_points ?? []).map((sp: any) =>
    typeof sp === "string" ? { kp_name: sp, mastery_level: null } : sp
  )

  return (
    <div className="flex flex-col gap-6 max-w-[1400px] mx-auto min-h-full py-6">
      {/* 顶部返回 */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 transition-colors w-fit"
      >
        <ChevronLeft className="w-4 h-4" />
        返回学生列表
      </button>

      <div className="flex gap-6 xl:flex-row flex-col">
        {/* 左侧基本信息 */}
        <div className="w-full xl:w-[280px] bg-white rounded-2xl p-6 shadow-sm border border-slate-100 xl:shrink-0">
          <div className="flex flex-col items-center mb-6">
            <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center border-4 border-white shadow-md mb-3">
              <User className="w-10 h-10 text-blue-600" />
            </div>
            <h2 className="text-xl font-bold text-slate-900">{profile.student_name || "学生"}</h2>
            <div className="flex items-center gap-2 mt-1.5 flex-wrap justify-center">
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600">
                学号：{profile.student_no || "—"}
              </span>
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-600">
                {profile.course_name || "课程"}
              </span>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <div className="text-xs font-medium text-slate-500 mb-1">当前课程</div>
              <div className="text-sm font-semibold text-slate-800 bg-slate-50 p-2 rounded-lg border border-slate-100">
                {profile.course_name || "暂无课程"}
              </div>
            </div>
            <div>
              <div className="text-xs font-medium text-slate-500 mb-1">综合掌握度</div>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${Math.round((profile.mastery_score ?? 0) * 100)}%`,
                      backgroundColor: (profile.mastery_score ?? 0) >= 0.75 ? "#22c55e" : (profile.mastery_score ?? 0) >= 0.4 ? "#f59e0b" : "#ef4444",
                    }}
                  />
                </div>
                <span className="text-sm font-bold text-slate-700 w-10 text-right">
                  {Math.round((profile.mastery_score ?? 0) * 100)}%
                </span>
              </div>
            </div>
            <div>
              <div className="text-xs font-medium text-slate-500 mb-1">当前水平</div>
              <div className="text-sm font-medium text-slate-700">{profile.current_level || "未知"}</div>
            </div>
            <div>
              <div className="text-xs font-medium text-slate-500 mb-1">学习目标</div>
              <div className="text-sm text-slate-700">{profile.learning_goal || "未设置"}</div>
            </div>
            <div>
              <div className="text-xs font-medium text-slate-500 mb-1">学习时间</div>
              <div className="text-sm text-slate-700">
                {profile.weekly_hours ? `每周 ${profile.weekly_hours} 小时` : "未设置"}
              </div>
            </div>
            <div>
              <div className="text-xs font-medium text-slate-500 mb-1">兴趣方向</div>
              <div className="flex flex-wrap gap-1">
                {(profile.interests ?? []).length > 0
                  ? profile.interests.map((t, i) => (
                      <span key={i} className="text-xs px-2 py-0.5 rounded bg-purple-50 text-purple-600 border border-purple-100">{t}</span>
                    ))
                  : <span className="text-xs text-slate-400">暂无</span>
                }
              </div>
            </div>
            <div>
              <div className="text-xs font-medium text-slate-500 mb-1">资源偏好</div>
              <div className="flex flex-wrap gap-1">
                {(profile.resource_preferences ?? []).length > 0
                  ? profile.resource_preferences.map((t, i) => (
                      <span key={i} className="text-xs px-2 py-0.5 rounded bg-blue-50 text-blue-600 border border-blue-100">{t}</span>
                    ))
                  : <span className="text-xs text-slate-400">暂无</span>
                }
              </div>
            </div>
          </div>
        </div>

        {/* 中间：薄弱知识点 */}
        <div className="flex-1 bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <h3 className="font-bold text-slate-900">薄弱知识点</h3>
          </div>
          {weakPoints.length === 0 ? (
            <div className="text-sm text-slate-400 py-8 text-center">暂无薄弱知识点数据</div>
          ) : (
            <div className="space-y-3">
              {weakPoints.map((wp, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-red-50 border border-red-100">
                  <div className="flex items-center gap-3">
                    <div className="text-xs font-bold text-red-500 bg-red-100 rounded-full w-6 h-6 flex items-center justify-center">
                      {i + 1}
                    </div>
                    <div>
                      <div className="font-medium text-slate-800 text-sm">
                        {wp.kp_name || wp.name || `kp#${wp.kp_id}`}
                      </div>
                      {wp.reason && <div className="text-xs text-slate-500 mt-0.5">{wp.reason}</div>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {(wp.mastery_level != null || wp.mastery != null) ? (
                      <>
                        <div className="w-24 h-2 rounded-full bg-red-200 overflow-hidden">
                          <div
                            className="h-full bg-red-500 rounded-full"
                            style={{ width: `${Math.round((wp.mastery_level ?? wp.mastery ?? 0) * 100)}%` }}
                          />
                        </div>
                        <span className="text-xs font-bold text-red-600 w-10 text-right">
                          {Math.round((wp.mastery_level ?? wp.mastery ?? 0) * 100)}%
                        </span>
                      </>
                    ) : (
                      <span className="text-xs text-slate-400">无掌握度记录</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* 强项知识点 */}
          <div className="flex items-center gap-2 mt-6 mb-4">
            <Target className="w-5 h-5 text-emerald-500" />
            <h3 className="font-bold text-slate-900">强项知识点</h3>
          </div>
          {strongPoints.length === 0 ? (
            <div className="text-sm text-slate-400 py-4 text-center">暂无强项知识点数据</div>
          ) : (
            <div className="space-y-3">
              {strongPoints.map((sp, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-emerald-50 border border-emerald-100">
                  <div className="flex items-center gap-3">
                    <div className="text-xs font-bold text-emerald-600 bg-emerald-100 rounded-full w-6 h-6 flex items-center justify-center">
                      {i + 1}
                    </div>
                    <div className="font-medium text-slate-800 text-sm">
                      {sp.kp_name || sp.name || `kp#${sp.kp_id}`}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 rounded-full bg-emerald-200 overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full"
                        style={{ width: `${Math.round((sp.mastery_level ?? sp.mastery ?? 0) * 100)}%` }}
                      />
                    </div>
                    <span className="text-xs font-bold text-emerald-600 w-10 text-right">
                      {Math.round((sp.mastery_level ?? sp.mastery ?? 0) * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 右侧：AI 建议 */}
        <div className="w-full xl:w-[300px] bg-white rounded-2xl p-6 shadow-sm border border-slate-100 xl:shrink-0">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-blue-500" />
            <h3 className="font-bold text-slate-900">AI 学习建议</h3>
          </div>
          <div className="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">
            {profile.ai_suggestions || "暂无 AI 建议（需完成学习任务后自动生成）"}
          </div>
        </div>
      </div>
    </div>
  )
}

/** 教师端：查看所有学生画像列表 */
export function TeacherStudents() {
  const [selectedProfileId, setSelectedProfileId] = useState<number | null>(null)

  const { data: profilesData, loading, reload } = useApi(
    () => profilesApi.list({ page_size: 100 }),
    []
  )

  const profiles: ProfileDetail[] = profilesData?.items ?? []

  const selectedProfile = selectedProfileId
    ? profiles.find(p => p.profile_id === selectedProfileId) ?? null
    : null

  if (loading) {
    return (
      <div className="flex flex-col gap-6 max-w-[1400px] mx-auto py-6">
        <div className="text-slate-400 p-12 text-center">加载学生列表中...</div>
      </div>
    )
  }

  // 已选中某个学生 → 展示详情
  if (selectedProfile) {
    return (
      <ProfileDetailPanel
        profile={selectedProfile}
        onBack={() => setSelectedProfileId(null)}
      />
    )
  }

  // 学生列表视图
  return (
    <div className="flex flex-col gap-6 max-w-[1400px] mx-auto min-h-full py-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
            <GraduationCap className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">学生画像</h1>
            <p className="text-sm text-slate-500">{profiles.length} 名学生</p>
          </div>
        </div>
      </div>

      {profiles.length === 0 ? (
        <div className="text-center text-slate-400 py-16 bg-white rounded-2xl border border-slate-100">
          暂无学生画像数据
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {profiles.map(profile => (
            <StudentCard
              key={profile.profile_id}
              profile={profile}
              selected={profile.profile_id === selectedProfileId}
              onClick={() => setSelectedProfileId(profile.profile_id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
