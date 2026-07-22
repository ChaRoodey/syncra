from fastapi import APIRouter

router = APIRouter(
    prefix="/calendar",
    tags=["Calendar"],
)


@router.get("/")
async def get_calendar(): ...
