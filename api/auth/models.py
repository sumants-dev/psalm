from pydantic import BaseModel


class BasicRes(BaseModel):
    success: bool


class ApiCreationReq(BaseModel):
    username: str


class ApiDeletionReq(BaseModel):
    username: str


class ApiCreationRes(BaseModel):
    success: bool
    username: str = ""
    api_key: str = ""
