# 导入所有模型，确保 Alembic autogenerate 能检测到所有表
from app.models.base import Base
from app.models.user import User, Role, UserRole
from app.models.application import Application
from app.models.version import Version
from app.models.test_case import TestCase
from app.models.test_task import TestTask
from app.models.execution import TaskExecution
from app.models.associations import test_case_defects
from app.models.defect import Defect, DefectComment, DefectStatusHistory

__all__ = [
    "Base",
    "User", "Role", "UserRole",
    "Application",
    "Version",
    "TestCase",
    "TestTask",
    "TaskExecution",
    "test_case_defects",
    "Defect", "DefectComment", "DefectStatusHistory",
]
