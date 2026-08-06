from pydantic import BaseModel

class UserCreate(BaseModel):
    user_name:str

class GroupCreate(BaseModel):
    group_name:str

class UserGroupCreate(BaseModel):
    group_id:int
    user_id:int