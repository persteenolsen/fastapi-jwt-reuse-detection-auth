from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str

    # 25-12-2025 - Added Users Name
    name: str
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    username: str

    # 25-12-2025 - Added Users Name
    name: str
    email: EmailStr

    class Config:

        # 19-12-2025 - Renamed orm_mode to from_attributes due to an Error
        #orm_mode = True
        from_attributes = True