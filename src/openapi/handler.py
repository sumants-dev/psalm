from fastapi import APIRouter

router = APIRouter()

@router.get("/v1/chat/completions")
async def root():
    print("hello world")
    return {"message": "Hello World"}