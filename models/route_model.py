
from typing import Literal, Optional
from pydantic import BaseModel, Field
from flask_openapi3 import FileStorage


class UserCreate(BaseModel):
    fullname: str
    username: str
    password: str # sha256 hash
    email: str
    mobile: str

class ChangePasswordModel(BaseModel):
    user_id: str
    old_password: str
    new_password: str

class UserLogin(BaseModel):
    username: str
    password: str # sha256(password)

class UserModel(BaseModel):
    user_id: str

class UpdateProfile(BaseModel):
    user_id: str
    fullname: str
    mobile: str


class UpdateEmail(BaseModel):
    user_id: str
    email: str
    
class VerifyEmail(BaseModel):
    email: str
    user_id: str
    otp: str

class UploadModel(BaseModel):
    user_id: str
    file: FileStorage

class ForgotPasswordModel(BaseModel):
    email: str

class Customers(BaseModel):
    code: str
    name: str
    email: str
    phone: str
    country: str
    social_media: str
    photos: str
    contacts: str
    docpath: str
    dob: str
    language: str 

class ResetPasswordModel(BaseModel):
    email: str
    otp: str
    new_password: str

# === Employee Related ====================
class EmpIdModel(BaseModel):
    emp_id: str
    user_id: str

class UploadModel(BaseModel):
    user_id: str
    emp_id: str
    file: FileStorage

class EmpCreate(BaseModel):
    user_id: str
    name: str
    designation: str

class EmpData(BaseModel):
    user_id: str
    emp_code: str
    name: str
    designation: str

class EmpUpdate(BaseModel):
    emp_id: str
    user_id: str
    name: str
    designation: str

class BasicQueryString(BaseModel):
    offset: int = Field(0, description='row offset')
    limit: int = Field(10, description='nos of rows to return')
    order_by: str = Field('id')
    order_direction: Literal['asc', 'desc'] = Field('desc')
    search_term: Optional[str] = Field(None)
    role: Optional[Literal["all","users","admin"]]
    status: Optional[Literal["all","activated","deactivated"]]