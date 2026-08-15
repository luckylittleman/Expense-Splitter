from fastapi import FastAPI, Depends, HTTPException
from .database import Base, engine, get_db
from .models import Users,Groups,UserGroup,Expenses, Paid, Debt
from sqlalchemy.orm import Session
from .schemas import UserCreate,GroupCreate,UserGroupCreate, ExpenseCreate, PaymentEntry

app=FastAPI()


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
def  delete_user(user_id:int, db:Session=Depends(get_db)):
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


