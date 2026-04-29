from fastapi import APIRouter

router = APIRouter()

@router.get("/init")
async def get_all():
    return "ok"
