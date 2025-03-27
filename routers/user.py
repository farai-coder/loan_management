from fastapi import HTTPException, Depends,APIRouter
from sqlalchemy.orm import Session
import random
from notification_service import NotificationService
from helper_functions import get_db, hash_password, verify_password
from model import User
from schemas import UserChangePassword, UserCreate, UserDelete, UserEdit, UserVerify, WalletCreate

router = APIRouter()

@router.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate a 6-digit verification code
    verification_code = f"{random.randint(100000, 999999)}"

    # Hash the password
    hashed_password = hash_password(user.password)

    # Create new user instance
    new_user = User(email=user.email,
                    name=user.name,
                    surname=user.surname,
                    phone_number=user.phone_number, 
                    password_hash=hashed_password,
                    verification_code=verification_code, 
                    is_active=False)
    db.add(new_user)
    db.commit()

    # Send verification code to user's email
    #NotificationService.send_email(user.email,"You verification Code is ",verification_code) // review code for fixing
    print(verification_code)
    return {"message": "User registered successfully. Please check your email for the verification code."}

#user auto verification
@router.post("/verify/")
def verify_user(user: UserVerify, db: Session = Depends(get_db)):
    # Retrieve user from the database
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    # Check if the verification code matches
    if db_user.verification_code != user.verification_code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # Update user status to active
    db_user.is_active = True
    db_user.verification_code = "000000"  # Clear the verification code

    # Commit changes to database
    db.commit()

    return {
        "message": "Email verified successfully. Your account is now active.",
    }

@router.post("/edit/")
def edit_user(user: UserEdit,db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    
    db_user.name = user.name
    db_user.surname = user.surname
    db_user.phone_number = user.phone_number
    db.commit()
    return {"message" : "User detail successfully updated"}

@router.post("/wallet")
def add_wallet(wallet:WalletCreate,db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == wallet.email,User.is_active == True).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    
    db_user.wallet_address = wallet.address
    db_user.private_key = wallet.private_key
    db.commit()
    return {"message": "wallet added succesfully"}
       

@router.post("/change_password/")
def change_password(user:UserChangePassword,db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    
    if verify_password(user.password,db_user.password_hash):
        db_user.password_hash = hash_password(user.new_password)
    
    db.commit()
    return {"message" : "Password Updated Sucessfully"}


@router.delete("/delete/")
def delete_user(user:UserDelete,db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    
    #delete the user from the database
    db.delete(db_user)
    db.commit()
    return {"message" : "User deleted"}