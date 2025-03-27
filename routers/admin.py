import time
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from data import *
from helper_functions import  get_db, hash_password
from model import *
from schemas import AdminCreate, AdminEdit
from notification_service import NotificationService
from web3 import Web3

router = APIRouter()


###admin logic###

# Create a new admin
@router.post("/add_admin")
def create_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    #create a new admin
    new_admin = Admin(
        username=admin.username,
        password_hash=hash_password(admin.password)
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return {"username" : new_admin.username, "message": "Admin created successfully"}

# Get all admins
@router.get("/get_all_admins")
def get_admins(db: Session = Depends(get_db)): 
    admins = db.query(Admin).all()
    return admins

# Get a single admin
@router.get("/admin/{username}")
def get_admin(username:str , db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

# Delete an admin
@router.delete("/delete_admin/{username}")
def delete_admin(username:str, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    db.delete(admin)
    db.commit()
    return {"message": "Admin deleted successfully"}

# Edit an admin
@router.put("/change_password/{username}")
def edit_admin(admin: AdminEdit , db: Session = Depends(get_db)):
    try:
        editing_admin = db.query(Admin).filter(Admin.username == admin.username).first()
        editing_admin.password_hash = hash_password(admin.new_password)
        return {"message": "Admin password changed"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
### end of admin logic ###



#------------------
# user logic
#------------------



# Get all users
@router.get("/users")
def admin_get_users(db: Session = Depends(get_db)):
    # check if admin is authorized
    users = db.query(User).all()
    return users

#delete a user
@router.delete("/delete_user/{user_id}")
def admin_delete_user(user_id:int ,db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# -----------------------
# common getter functions
#------------------------
# get all walllets
@router.get("/wallets")
def admin_get_wallets(db: Session = Depends(get_db)):
    #impliment logic to get all the registered wallets
    return 

# Get all loans
@router.get("/loans")
def get_loans(db: Session = Depends(get_db)):
    loans = db.query(Loan).all()
    if not loans:
        raise HTTPException(status_code=404, detail="No loans found")
    return loans
