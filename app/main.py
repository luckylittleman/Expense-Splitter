from fastapi import FastAPI, Depends, HTTPException, Request
from .database import Base, engine, get_db, redis_client
from .models import Users,Groups,UserGroup,Expenses, Paid, Debt
from sqlalchemy.orm import Session,joinedload
from .schemas import UserCreate,GroupCreate,UserGroupCreate, ExpenseCreate, PaymentEntry, UserResponse, LoginRequest
import redis, json
from sqlalchemy import text
from .security import hash_password, verify_password, create_access_token, get_current_user
from fastapi.middleware.cors import CORSMiddleware
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address


app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter=Limiter(key_func=get_remote_address)
app.state.limiter=limiter


@app.get("/")
def read_root():
    return{"message":"Hello"}

@app.post("/users", response_model=UserResponse)
def user(user:UserCreate, db:Session=Depends(get_db)):
   
    new_user=Users(user_name=user.user_name, password_hash=hash_password(user.password))




    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    logger.info(f"New User registered:{new_user.user_id}")

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

@app.post("/usergroups")
def user_group(usergroup:UserGroupCreate, db:Session=Depends(get_db)):
    user=db.query(Users).filter(Users.user_id==usergroup.user_id).first()
    if user is None:
        raise HTTPException(status_code=404,detail="User not found")
    
    group=db.query(Groups).filter(Groups.group_id==usergroup.group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    new_user_group=UserGroup(group_id=usergroup.group_id, user_id=usergroup.user_id)

    db.add(new_user_group)

    db.commit()

    db.refresh(new_user_group)

    return new_user_group

@app.post("/expenses")
def expense(expense:ExpenseCreate, db:Session=Depends(get_db)):
   group=db.query(Groups).filter(Groups.group_id==expense.group_id).first()
   if group is None:
       raise HTTPException(status_code=404,detail="Group not found")

   users=db.query(Users).filter(Users.user_id.in_(expense.participant_ids)).all()
   if len(users) !=len(expense.participant_ids):
       raise HTTPException(status_code=404, detail="One or more user not found")

   new_expense = Expenses(expense_name=expense.expense_name, amount=expense.amount, group_id=expense.group_id)
   db.add(new_expense)
   db.commit()
   db.refresh(new_expense)

   for payment in expense.payments:
       new_payment=Paid(user_id=payment.user_id, expense_id=new_expense.expense_id,paid_amount=payment.amount_paid)
       db.add(new_payment)

   share=expense.amount/len(expense.participant_ids)

   for user_id in expense.participant_ids:
       new_debt=Debt(user_id=user_id,expense_id=new_expense.expense_id, amount_owed=share)
       db.add(new_debt)

  

   db.commit()


   return new_expense

@app.get("/expenses")
def get_expenses(db:Session=Depends(get_db)):
    all_expenses=db.query(Expenses).all()

    return all_expenses

@app.get("/expenses/{expense_id}")
def get_expense(expense_id:int ,db:Session=Depends(get_db)):
    expense=db.query(Expenses).filter(Expenses.expense_id==expense_id).first()

    if expense is None:
        raise HTTPException(status_code=404,detail="Expense not found")

    return expense

@app.delete("/users/{user_id}")
def  delete_user(user_id:int, db:Session=Depends(get_db), current_user: Users=Depends(get_current_user)):
    user=db.query(Users).filter(Users.user_id==user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)

    db.commit()

    return{"message":"User deleted"}

@app.delete("/groups/{group_id}")
def delete_group(group_id:int, db:Session=Depends(get_db)):
    group=db.query(Groups).filter(Groups.group_id==group_id).first()

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    db.delete(group)

    db.commit()

    return{"message":"Group deleted"}

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id:int, db:Session=Depends(get_db)):
    expense=db.query(Expenses).filter(Expenses.expense_id==expense_id).first()

    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)

    db.commit()

    return{"message":"expsense deleted"}

@app.put("/users/{user_id}")
def update_user(user_id:int, update_data:UserCreate, db:Session=Depends(get_db)):
    user=db.query(Users).filter(Users.user_id==user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="user not found")

    

    user.user_name= update_data.user_name

    db.commit()

    db.refresh(user)

    return user

@app.put("/groups/{group_id}")
def update_group(group_id:int, update_group:GroupCreate, db:Session=Depends(get_db)):
    group=db.query(Groups).filter(Groups.group_id==group_id).first()

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    group.group_name=update_group.group_name

    db.commit()

    db.refresh(group)

    return group

@app.put("/expenses/{expense_id}")
def update_expense(expense_id:int, update_data:ExpenseCreate, db:Session=Depends(get_db)):
    group=db.query(Groups).filter(Groups.group_id==update_data.group_id).first()

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    expense=db.query(Expenses).filter(Expenses.expense_id==expense_id).first()

    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    expense.expense_name=update_data.expense_name
    expense.group_id=update_data.group_id
    expense.amount=update_data.amount

    db.commit()

    db.refresh(expense)

    return expense

@app.get("/groups/{group_id}/balances")
def make_balances(group_id:int,db:Session=Depends(get_db)):
    group=db.query(Groups).filter(Groups.group_id==group_id).first()

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    cache_key=f"balances:{group_id}"
    cached_result=redis_client.get(cache_key)
        
    if cached_result is not None:
        return json.loads(cached_result)
        

    group_debts=db.query(Debt).join(Expenses, Debt.expense_id==Expenses.expense_id).filter(Expenses.group_id==group_id).all()

    group_paids=db.query(Paid).join(Expenses,Paid.expense_id==Expenses.expense_id ).filter(Expenses.group_id==group_id).all()

    balances={}

    for debt in group_debts:
        if debt.user_id not in balances:
            balances[debt.user_id]=0
        balances[debt.user_id]=balances[debt.user_id]-debt.amount_owed

    for paid in group_paids:
        if paid.user_id not in balances:
            balances[paid.user_id]=0
        balances[paid.user_id]=balances[paid.user_id]+paid.paid_amount

    redis_client.set(cache_key,json.dumps(balances,default=float),ex=60)

    return balances

@app.get("/groups/{group_id}/expenses-with-payments")
def expense_payments(group_id:int, db:Session=Depends(get_db)):
    group=db.query(Groups).filter(Groups.group_id==group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    group_expenses=db.query(Expenses).options(joinedload(Expenses.paid_entries)).filter(Expenses.group_id==group_id).all()

    res=[]

    
    for group_expense in group_expenses:
        payment_list=[]
        for paid in group_expense.paid_entries:
            payment_list.append({"user_id":paid.user_id,"amount_paid":paid.paid_amount})
        
       
        res.append({"expense_name":group_expense.expense_name, "payments":payment_list})

    

    return res

@app.get("/groups/{group_id}/debts-raw-sql")
def debt_row(group_id:int, db:Session=Depends(get_db)):
    group=db.query(Groups).filter(Groups.group_id==group_id).first()
    if group is None:
         raise HTTPException(status_code=404, detail="Group not found")

    result=db.execute(text("SELECT debt.user_id, SUM(debt.amount_owed) FROM debt JOIN expenses ON debt.expense_id = expenses.expense_id WHERE expenses.group_id= :group_id GROUP BY debt.user_id"), {"group_id":group_id})

    result=result.fetchall()

    res=[]

    for row in result:
        res.append({"user_id":row[0], "total_owed":float(row[1])})

    return res

@app.post("/login")
@limiter.limit("5/minute")
def login(request:Request, login_data:LoginRequest, db:Session=Depends(get_db)):
    user=db.query(Users).filter(Users.user_name==login_data.user_name).first()

    if user is None or not verify_password(login_data.password,user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(data={"sub":str(user.user_id)})

    logger.info(f"User {user.user_id} logged in successfully")


    return {"access_token":token, "token_type":"bearer"}



