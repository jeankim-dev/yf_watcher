from fastapi import FastAPI
from app.api import router

app = FastAPI(title="Stock Screener")

app.include_router(router)
