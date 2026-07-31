from fastapi import FastAPI, Depends
from .database import Base, engine, get_db
from .models import Users 
from sqlalchemy.orm import Session
from .schemas import UserCreate

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

 

    
