from app.middleware.logging import LoggingMiddleware

MIDDLEWARE_CLASSES = [
    LoggingMiddleware,
]


def register_middlewares(app):
    for middleware in MIDDLEWARE_CLASSES:
        app.add_middleware(middleware)
