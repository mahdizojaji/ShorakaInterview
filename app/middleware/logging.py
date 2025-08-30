from datetime import datetime, timezone
from json import loads as json_loads
from logging import INFO, Formatter, StreamHandler, getLogger
from time import time

from fastapi import Request, Response
from jwt import decode as jwt_decode
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

logger = getLogger(__name__)
logger.setLevel(INFO)
ch = StreamHandler()
ch.setLevel(INFO)
formatter = Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
getLogger("uvicorn.access").disabled = True

EXCLUDE_PATHS = [
    "/health_check",
]

SENSITIVE_FIELDS = [
    "password",
    "code",
    "token",
]


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if any(request.url.path.startswith(p) for p in EXCLUDE_PATHS):
            return await call_next(request)

        start_time = time()

        body_bytes = await request.body()
        try:
            request_body = json_loads(body_bytes)
        except Exception:
            request_body = str(body_bytes)

        if isinstance(request_body, dict):
            for key in SENSITIVE_FIELDS:
                request_body.pop(key, None)

        headers = dict(request.headers)
        auth_data = {}
        if "authorization" in headers:
            auth_header = headers.get("authorization")
            headers.pop("authorization", None)
            try:
                _, token = auth_header.split(" ")
                auth_data = jwt_decode(token, options={"verify_signature": False})
            except Exception:  # noqa
                auth_data = {}

        response = await call_next(request)
        body = [section async for section in response.body_iterator]  # noqa
        response_bytes = b"".join(body)

        new_response = StarletteResponse(
            content=response_bytes,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

        process_time = time() - start_time
        try:
            response_body = json_loads(response_bytes)
        except Exception:  # noqa
            response_body = str(response_bytes)

        ip = request.headers.get("x-forwarded-for", request.client.host if request.client else None)
        timestamp = datetime.now(timezone.utc).timestamp()

        logger.info(
            f"{request.method} {request.url.path} {response.status_code} {process_time:.3f}s",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
                "request_body": request_body,
                "response_body": response_body,
                "request_headers": headers,
                "authorization_data": auth_data,
                "client_ip": ip,
                "timestamp": timestamp,
            },
        )
        return new_response


def add_logging_middleware(app):
    app.add_middleware(LoggingMiddleware)
