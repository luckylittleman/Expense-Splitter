import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase
from dotenv import load_dotenv
import redis

load_dotenv()

REDIS_HOST=os.getenv("REDIS_HOST","localhost")
REDIS_PORT=os.getenv("REDIS_PORT",6379)

redis_client=redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

DATABASE_URL=os.getenv("DATABASE_URL")

engine=create_engine(DATABASE_URL, echo=True)

SessionLocal=sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db=SessionLocal()
    try:
       yield db
    finally:
        db.close()