from typing import Any
from fastapi.responses import JSONResponse


def success(data: Any, message: str = "操作成功", status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": True, "data": data, "message": message},
    )


def created(data: Any, message: str = "创建成功") -> JSONResponse:
    return success(data, message, status_code=201)
