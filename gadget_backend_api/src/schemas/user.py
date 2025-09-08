from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User email")
    full_name: str | None = Field(default=None, description="Full name")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")


class UserRead(UserBase):
    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Is active")
    is_admin: bool = Field(..., description="Is admin")

    class Config:
        from_attributes = True
