from app.core.exceptions import BusinessError

# 允许的状态流转：{当前状态: [可到达的状态列表]}
VALID_TRANSITIONS: dict[str, list[str]] = {
    "new":      ["assigned"],
    "assigned": ["fixed", "rejected"],
    "fixed":    ["verified", "reopened"],
    "verified": ["closed"],
    "rejected": [],            # 终态，不能再流转
    "closed":   ["reopened"],
    "reopened": ["assigned"],
}

# 每条流转允许的角色：{(from, to): [角色列表]}
ROLE_PERMISSIONS: dict[tuple[str, str], list[str]] = {
    ("new",      "assigned"): ["admin", "tester"],
    ("assigned", "fixed"):    ["developer"],
    ("assigned", "rejected"): ["admin", "tester"],
    ("fixed",    "verified"): ["tester"],
    ("fixed",    "reopened"): ["tester"],
    ("verified", "closed"):   ["admin", "tester"],
    ("closed",   "reopened"): ["admin"],
    ("reopened", "assigned"): ["admin", "tester"],
}


def validate_transition(from_status: str, to_status: str, user_roles: list[str]) -> None:
    """
    验证缺陷状态流转是否合法。
    - 状态跳转不合法：抛 BusinessError(code="INVALID_TRANSITION")
    - 角色无权执行：抛 BusinessError(code="TRANSITION_FORBIDDEN")
    """
    allowed_targets = VALID_TRANSITIONS.get(from_status, [])
    if to_status not in allowed_targets:
        raise BusinessError(
            code="INVALID_TRANSITION",
            message=f"无效的状态流转：{from_status} → {to_status}",
        )

    allowed_roles = ROLE_PERMISSIONS.get((from_status, to_status), [])
    if not any(role in allowed_roles for role in user_roles):
        raise BusinessError(
            code="TRANSITION_FORBIDDEN",
            message="当前角色无权执行此状态流转",
        )
