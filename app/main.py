from fastapi import FastAPI, Depends, HTTPException
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

@app.get("/users")
def get_users(db:Session=Depends(get_db)):
    all_users=db.query(Users).all()

    return all_users
 
@app.get("/users/{user_id}")
def get_user(user_id:int,db:Session=Depends(get_db)):
    user=db.query(Users).filter(Users.user_id==user_id).first()
    if user is None:
        raise HTTPException(status_code=404,detail="User not found")
    return user

@app.get("/groups")
def get_groups(db:Session=Depends(get_db)):
    all_groups=db.query(Groups).all()

    return all_groups

@app.get("/groups/{group_id}")
def get_group(group_id:int,db:Session=Depends(get_db)):
    group=db.query(Groups).filter(Groups.group_id==group_id).first()
    if group is None:
        raise HTTPException(status_code=404,detail="Group not found")
    return group
    
