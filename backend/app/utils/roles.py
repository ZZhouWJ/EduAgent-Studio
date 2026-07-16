"""平台角色与能力清单的单一事实源。"""

PLATFORM_ROLE_CODES = frozenset({"student_member", "teacher", "admin"})
PUBLIC_REGISTRATION_ROLE_CODES = frozenset({"student_member"})

ROLE_METADATA = {
    "student_member": {
        "role_name": "学生",
        "description": "使用个性化辅导、学习路径、任务、资源与学习反馈。",
    },
    "teacher": {
        "role_name": "教师",
        "description": "管理本人课程、学生画像、学习任务、知识库与 AI 生成资源。",
    },
    "admin": {
        "role_name": "系统管理员",
        "description": "负责平台用户、课程、模型、智能体、审计、成本与内容安全治理。",
    },
}

# (name, code, module code, module label, description, granted roles)
CAPABILITY_DEFINITIONS = (
    ("使用 AI 学习辅导", "tutor:chat", "learning", "个性化学习", "进行对话辅导并获得基于课程知识库的回答。", ("student_member",)),
    ("查看个人学习画像", "profile:view_self", "learning", "个性化学习", "查看本人的目标、偏好、能力与知识掌握情况。", ("student_member",)),
    ("查看个人学习路径", "learning_path:view_self", "learning", "个性化学习", "查看根据画像与掌握度生成的学习路径。", ("student_member",)),
    ("查看个人学习任务", "learning_task:view_self", "learning", "个性化学习", "查看分配给本人的课程学习任务。", ("student_member",)),
    ("访问已选课程资源", "resource:view_enrolled", "learning", "个性化学习", "浏览已选课程中审核通过的学习资源。", ("student_member",)),
    ("提交学习反馈", "feedback:submit", "learning", "个性化学习", "提交资源评价、自评掌握度与学习结果。", ("student_member",)),
    ("查看个人学习报告", "analytics:view_self", "learning", "个性化学习", "查看本人的学习趋势、薄弱点与改进建议。", ("student_member",)),
    ("管理本人课程", "course:manage_own", "teaching", "教学管理", "查看并维护本人负责的课程。", ("teacher",)),
    ("管理课程学生画像", "profile:manage_enrolled", "teaching", "教学管理", "查看和维护本人课程内学生的学习画像。", ("teacher",)),
    ("生成课程学习资源", "resource:generate", "teaching", "教学管理", "使用多智能体工作流生成课程学习资源。", ("teacher",)),
    ("管理本人课程资源", "resource:manage_own", "teaching", "教学管理", "查看、编辑和维护本人课程资源。", ("teacher",)),
    ("审核 AI 生成内容", "resource:review", "teaching", "教学管理", "审核 AI 生成结果并决定是否发布。", ("teacher",)),
    ("管理课程学习任务", "learning_task:manage", "teaching", "教学管理", "创建并分配本人课程的学习任务。", ("teacher",)),
    ("管理课程知识库", "knowledge:manage_own", "teaching", "教学管理", "上传、解析和维护本人课程知识材料。", ("teacher",)),
    ("查看课程教学分析", "analytics:view_course", "teaching", "教学管理", "查看本人课程的学习成效与风险分析。", ("teacher",)),
    ("查看平台运营总览", "platform:view", "platform", "平台治理", "查看平台服务、课程、资源与调用运行情况。", ("admin",)),
    ("管理用户与角色", "user:manage", "platform", "平台治理", "创建、启停用户并分配平台角色。", ("admin",)),
    ("管理全部课程", "course:manage_all", "platform", "平台治理", "查看和维护平台全部课程。", ("admin",)),
    ("管理全部学习资源", "resource:manage_all", "platform", "平台治理", "查看并治理平台全部学习资源。", ("admin",)),
    ("管理全部课程知识库", "knowledge:manage_all", "platform", "平台治理", "查看并维护平台全部课程知识材料。", ("admin",)),
    ("管理模型服务", "model:manage", "ai_governance", "AI 治理", "配置模型供应商、模型与加密凭据。", ("admin",)),
    ("管理智能体编排", "agent:manage", "ai_governance", "AI 治理", "配置诊断、规划、生成、评估与审核智能体。", ("admin",)),
    ("管理提示词模板", "prompt:manage", "ai_governance", "AI 治理", "维护资源生成与审核提示词版本。", ("admin",)),
    ("审计模型调用", "invocation:audit", "ai_governance", "AI 治理", "按用户、模型与智能体追踪调用证据。", ("admin",)),
    ("查看模型成本", "cost:view", "ai_governance", "AI 治理", "分析模型调用量、Token 与成本。", ("admin",)),
    ("治理内容安全", "content:govern", "ai_governance", "AI 治理", "查看风险内容并跟踪人工复核结果。", ("admin",)),
    ("查看平台操作日志", "log:view", "ai_governance", "AI 治理", "查询用户操作和登录审计日志。", ("admin",)),
)


def filter_platform_roles(roles: list[dict]) -> list[dict]:
    """只返回平台角色，并使用当前产品的名称与说明。"""
    result = []
    for role in roles:
        role_code = role.get("role_code")
        metadata = ROLE_METADATA.get(role_code)
        if metadata is None:
            continue
        result.append({**role, **metadata})
    return result


def list_platform_capabilities() -> list[dict]:
    """返回可用于管理界面展示的稳定能力清单。"""
    return [
        {
            "permission_id": index,
            "permission_name": name,
            "permission_code": code,
            "module_name": module_name,
            "module_label": module_label,
            "description": description,
            "role_codes": list(role_codes),
        }
        for index, (
            name,
            code,
            module_name,
            module_label,
            description,
            role_codes,
        ) in enumerate(CAPABILITY_DEFINITIONS, start=1)
    ]


def permissions_for_roles(role_codes: list[str]) -> list[str]:
    """根据角色集合计算当前产品能力代码。"""
    assigned_roles = set(role_codes)
    return [
        code
        for _name, code, _module, _label, _description, granted_roles
        in CAPABILITY_DEFINITIONS
        if assigned_roles.intersection(granted_roles)
    ]
