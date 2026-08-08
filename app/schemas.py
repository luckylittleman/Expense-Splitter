from pydantic import BaseModel
from decimal import Decimal

class UserCreate(BaseModel):
    user_name:str

class GroupCreate(BaseModel):
    group_name:str

class UserGroupCreate(BaseModel):
    group_id:int
    user_id:int

class ExpenseCreate(BaseModel):
    group_id:int
    expense_name :str
    amount:Decimal
