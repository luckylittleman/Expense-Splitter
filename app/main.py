from fastapi import FastAPI, Depends
from .database import Base, engine, get_db
from .models import Users,Groups
from sqlalchemy.orm import Session
from .schemas import UserCreate,GroupCreate

app=FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return{"message":"Hello"}

@app.post("/users")
def user(user:UserCreate, db:Session=Depends(get_db)):
    new_user=Users(user_name=user.user_name)

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user

@app.post("/groups")
def group(group:GroupCreate, db:Session=Depends(get_db)):
    new_group=Groups(group_name=group.group_name)

    db.add(new_group)

    db.commit()

    db.refresh(new_group)

    return new_group
 

    
