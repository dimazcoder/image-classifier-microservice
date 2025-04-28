from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import config


async def check_api_key(request: Request, call_next):
    if request.url.path == "/openapi.json":
        return await call_next(request)

    if request.url.path.startswith("/docs"):
        return await call_next(request)

    if request.url.path.startswith("/redoc"):
        return await call_next(request)

    if request.url.path.startswith("/api/v1/tasks/local"):
        return await call_next(request)

    if request.url.path.startswith("/status"):
        return await call_next(request)

    if request.url.path.startswith("/"):
        return await call_next(request)

    api_key = request.headers.get("API-Key")

    if api_key != config.api_key:
        return JSONResponse(status_code=401, content={"message": "Invalid API Key"})

    response = await call_next(request)
    return response
