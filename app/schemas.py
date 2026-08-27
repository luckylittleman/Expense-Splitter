from pydantic import BaseModel
from decimal import Decimal

class UserCreate(BaseModel):
    user_name:str
    password:str

class GroupCreate(BaseModel):
    group_name:str

class UserGroupCreate(BaseModel):
    group_id:int
    user_id:int

class PaymentEntry(BaseModel):
    user_id:int
    amount_paid:Decimal


class ExpenseCreate(BaseModel):
    group_id:int
    expense_name :str
    amount:Decimal
    participant_ids:list[int]
    payments:list[PaymentEntry]

class UserResponse(BaseModel):
    user_id:int
    user_name:str

    class Config:
        from_attributes = True

