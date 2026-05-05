from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Returns 200 if the service is up.",
)
def health_check():
    return {"status": "ok"}
