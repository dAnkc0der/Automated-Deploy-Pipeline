from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserBase(BaseModel):
    name: str
    email: EmailStr  


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: UUID  
    class Config:
        from_attributes = True
