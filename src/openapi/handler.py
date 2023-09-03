from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    print("hello world")
    return {"message": "Hello World"}