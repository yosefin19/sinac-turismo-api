from pydantic import BaseModel

class Profile(BaseModel):
    name: str
    phone: int
    email: str
    admin: bool
    user_id: int
    
    class Config:
        orm_mode = True
