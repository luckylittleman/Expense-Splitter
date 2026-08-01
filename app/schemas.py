from pydantic import BaseModel

class UserCreate(BaseModel):
    user_name:str

class GroupCreate(BaseModel):
    group_name:str