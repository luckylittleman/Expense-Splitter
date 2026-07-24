from .database import Base
from sqlalchemy import String,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column

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