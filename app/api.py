from fastapi import APIRouter
from app.services import run_screening

router = APIRouter()


@router.post("/screening")
async def screening():
    results = await run_screening()
    return {
        "count": len(results),
        "results": results
    }
