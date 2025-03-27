from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper_functions import get_db, verify_password
from model import Admin, User
from schemas import UserLogin

router = APIRouter()

#logic for user login
@router.post("/")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    #check if the user is in the admin or user service_provider table
    admin = db.query(Admin).filter(Admin.username == user.username).first()
    db_user = db.query(User).filter(User.email == user.username,User.is_active == True).first()
   
    if admin:
        if verify_password(user.password, admin.password_hash):
            return {"message": "login successful" , "role" : "admin" , "id" : admin.id , "username" : admin.username}
        else:
            return {"message": "incorrect password"}
    if db_user:
        if verify_password(user.password, db_user.password_hash):
            return {"message": "login successful", "role" : "user"} 
        else:
            return {"message": "incorrect password"}
    return {"message": "Login failed" , "role" : "none"}
    
