from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import NotFoundError, ForbiddenError, BusinessError, ConflictError

app = FastAPI(
    title="test-center",
    description="测试管理平台 API",
    version="0.1.0",
)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": {"code": "NOT_FOUND", "message": exc.message}},
    )


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(
        status_code=403,
        content={"success": False, "error": {"code": "FORBIDDEN", "message": exc.message}},
    )


@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    return JSONResponse(
        status_code=400,
        content={"success": False, "error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=409,
        content={"success": False, "error": {"code": "CONFLICT", "message": exc.message}},
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}


from app.auth.router import router as auth_router
from app.application.router import router as app_router
from app.test_case.router import router as test_case_router
from app.test_task.router import router as test_task_router
from app.defect.router import router as defect_router

app.include_router(auth_router)
app.include_router(app_router)
app.include_router(test_case_router)
app.include_router(test_task_router)
app.include_router(defect_router)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

_DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.isdir(_DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(_DIST_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend(full_path: str):
        return FileResponse(os.path.join(_DIST_DIR, "index.html"))
