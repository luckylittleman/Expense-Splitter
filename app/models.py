from .database import Base
from sqlalchemy import String,ForeignKey,Numeric
from sqlalchemy.orm import Mapped,mapped_column
from decimal import Decimal

class Users(Base):
    __tablename__="users"

    user_id: Mapped[int]=mapped_column(primary_key=True)
    user_name: Mapped[str]=mapped_column(String(100))

class Groups(Base):
    __tablename__="groups"

    group_id:Mapped[int]=mapped_column(primary_key=True)
    group_name:Mapped[str]=mapped_column(String(100))

class UserGroup(Base):
    __tablename__="usergroup"

    user_group_id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.user_id"))
    group_id:Mapped[int]=mapped_column(ForeignKey("groups.group_id"))

class Expenses(Base):
    __tablename__="expenses"

    expense_id:Mapped[int]=mapped_column(primary_key=True)
    expense_name:Mapped[str]=mapped_column(String(100))
    amount:Mapped[Decimal]=mapped_column(Numeric(10,2))
    group_id:Mapped[int]=mapped_column(ForeignKey("groups.group_id"))

class Debt(Base):
    __tablename__="debt"
    user_id:Mapped[int]=mapped_column(ForeignKey("users.user_id"))
    amount_owed:Mapped[Decimal]=mapped_column(Numeric(10,2))
    debt_id:Mapped[int]=mapped_column(primary_key=True)
    expense_id:Mapped[int]=mapped_column(ForeignKey("expenses.expense_id"))

class Paid(Base):
    __tablename__="paid"
    user_id:Mapped[int]=mapped_column(ForeignKey("users.user_id"))
    paid_amount:Mapped[Decimal]=mapped_column(Numeric(10,2))
    paid_id:Mapped[int]=mapped_column(primary_key=True)
    expense_id:Mapped[int]=mapped_column(ForeignKey("expenses.expense_id"))
