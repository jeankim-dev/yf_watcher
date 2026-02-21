from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.rs_service import get_rs_data, get_rs_kr_data

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/rs", response_class=HTMLResponse)
async def get_rs_page(request: Request):
    return templates.TemplateResponse("rs.html", {"request": request, "market": "US"})

@router.post("/rs", response_class=HTMLResponse)
async def post_rs_page(request: Request, ticker: str = Form(...)):
    data, error = get_rs_data(ticker.strip())
    if error: return templates.TemplateResponse("rs.html", {"request": request, "error": error, "ticker": ticker, "market": "US"})
    return templates.TemplateResponse("rs.html", {"request": request, "ticker": ticker, "market": "US", **data})

@router.get("/rskr", response_class=HTMLResponse)
async def get_rs_kr_page(request: Request):
    return templates.TemplateResponse("rs.html", {"request": request, "market": "KR"})

@router.post("/rskr", response_class=HTMLResponse)
async def post_rs_kr_page(request: Request, ticker: str = Form(...)):
    data, error = get_rs_kr_data(ticker.strip())
    if error: return templates.TemplateResponse("rs.html", {"request": request, "error": error, "ticker": ticker, "market": "KR"})
    return templates.TemplateResponse("rs.html", {"request": request, "ticker": ticker, "market": "KR", **data})
