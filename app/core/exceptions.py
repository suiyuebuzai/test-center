class NotFoundError(Exception):
    """资源不存在 → HTTP 404"""
    def __init__(self, message: str = "资源不存在"):
        self.message = message
        super().__init__(self.message)


class ForbiddenError(Exception):
    """无权限 → HTTP 403"""
    def __init__(self, message: str = "无访问权限"):
        self.message = message
        super().__init__(self.message)


class BusinessError(Exception):
    """业务规则违反 → HTTP 400（如非法状态流转）"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)


class ConflictError(Exception):
    """唯一约束冲突 → HTTP 409（如应用 code 重复）"""
    def __init__(self, message: str = "资源已存在"):
        self.message = message
        super().__init__(self.message)
