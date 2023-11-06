from typing import List
from pydantic import BaseModel, Field


class ListResponseModel(BaseModel):
    results: List[dict]
    total: int = Field(0, description="No. of rows return")
    code: int = Field(0, description="Response status code")

class DataResponseModel(BaseModel):
    results: dict
    code: int = Field(0, description="Response status code")

class LoginResponseModel(BaseModel):
    result: dict = Field(..., description="Response message") 
    message: str = Field("success", description="Response message") 
    code: int = Field(0, description="Response status code")

class CreateResponseModel(BaseModel):
    result: dict
    message: str = Field("success", description="Response message") 
    code: int = Field(0, description="Response status code")


class CheckSessionResponseModel(BaseModel):
    body: dict

class MessageResponseModel(BaseModel):
    message: str 
    code: int = Field(0, description="Response status code")

class ResponseModel(BaseModel):
    result: dict
    message: str 
    code: int = Field(0, description="Response status code")

# error models
class Unauthorized(BaseModel):
    code: int = Field(-1, description="Response status code")
    message: str = Field("Unauthorized!", description="Exception Information")

class NotFoundResponse(BaseModel):
    code: int = Field(-1, description="Response status code")
    message: str = Field("Resource not found!", description="Exception Information")


class StatusResponseModel(BaseModel):
    status: bool = Field(..., description="Return status flag. True if session exists or False")