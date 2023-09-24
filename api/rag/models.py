from pydantic import BaseModel


class BaseResponseModel(BaseModel):
    success: bool
