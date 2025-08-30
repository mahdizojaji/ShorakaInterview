from fastapi import FastAPI

from app.api import endpoints
from app.middleware import register_middlewares

app = FastAPI()
app.include_router(endpoints.router)
register_middlewares(app)
