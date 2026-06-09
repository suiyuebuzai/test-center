import pytest
from app.defect.state_machine import validate_transition
from app.core.exceptions import BusinessError


# ── 合法流转 ──────────────────────────────────────────
def test_new_to_assigned_by_tester():
    validate_transition("new", "assigned", ["tester"])  # 不抛异常即通过


def test_assigned_to_fixed_by_developer():
    validate_transition("assigned", "fixed", ["developer"])


def test_fixed_to_verified_by_tester():
    validate_transition("fixed", "verified", ["tester"])


def test_verified_to_closed_by_admin():
    validate_transition("verified", "closed", ["admin"])


def test_closed_to_reopened_by_admin():
    validate_transition("closed", "reopened", ["admin"])


def test_reopened_to_assigned_by_tester():
    validate_transition("reopened", "assigned", ["tester"])


def test_assigned_to_rejected_by_tester():
    validate_transition("assigned", "rejected", ["tester"])


def test_fixed_to_reopened_by_tester():
    validate_transition("fixed", "reopened", ["tester"])


# ── 非法状态跳转 ──────────────────────────────────────
def test_invalid_new_to_fixed():
    with pytest.raises(BusinessError) as exc:
        validate_transition("new", "fixed", ["tester"])
    assert exc.value.code == "INVALID_TRANSITION"


def test_invalid_new_to_closed():
    with pytest.raises(BusinessError) as exc:
        validate_transition("new", "closed", ["admin"])
    assert exc.value.code == "INVALID_TRANSITION"


def test_invalid_verified_to_assigned():
    with pytest.raises(BusinessError) as exc:
        validate_transition("verified", "assigned", ["admin"])
    assert exc.value.code == "INVALID_TRANSITION"


def test_rejected_is_terminal():
    with pytest.raises(BusinessError) as exc:
        validate_transition("rejected", "assigned", ["admin"])
    assert exc.value.code == "INVALID_TRANSITION"


# ── 权限不足 ──────────────────────────────────────────
def test_developer_cannot_close():
    with pytest.raises(BusinessError) as exc:
        validate_transition("verified", "closed", ["developer"])
    assert exc.value.code == "TRANSITION_FORBIDDEN"


def test_developer_cannot_assign():
    with pytest.raises(BusinessError) as exc:
        validate_transition("new", "assigned", ["developer"])
    assert exc.value.code == "TRANSITION_FORBIDDEN"


def test_readonly_cannot_do_anything():
    with pytest.raises(BusinessError):
        validate_transition("new", "assigned", ["readonly"])


def test_multi_role_allows_if_any_matches():
    # 用户同时有 developer 和 tester 角色，tester 能做这个操作
    validate_transition("new", "assigned", ["developer", "tester"])
