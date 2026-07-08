from fastapi import APIRouter

router_simple = APIRouter()

# Note: The below two routes are public and do not require authentication
# Public root route that returns a message
@router_simple.get("/", tags=["simple"])
async def read_root() -> dict:
    return {"message": "Welcome to FastAPI with Authentication by JWT and Refresh Tokens..."}

# Public ping route that returns a pong message
@router_simple.get("/ping", tags=["simple"])
async def read_root() -> dict:
    return {"message": "Pong ..."}