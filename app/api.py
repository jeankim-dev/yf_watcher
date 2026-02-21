from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.rs_service import get_rs_data

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/rs", response_class=HTMLResponse)
async def get_rs_page(request: Request):
    return templates.TemplateResponse("rs.html", {"request": request})

@router.post("/rs", response_class=HTMLResponse)
async def post_rs_page(request: Request, ticker: str = Form(...)):
    ticker = ticker.upper().strip()
    data, error = get_rs_data(ticker)
    if error: return templates.TemplateResponse("rs.html", {"request": request, "error": error, "ticker": ticker})
    return templates.TemplateResponse("rs.html", {"request": request, "ticker": ticker, **data})
