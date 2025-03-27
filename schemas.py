# -------------------------
# Enums for Statuses and Types
# -------------------------
import enum
from pydantic import BaseModel, EmailStr

class UserRole(enum.Enum):
    student = "student"
    admin = "admin"


class ApplicationStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

#-------------------------------
# Schemas for Users
#--------------------------------
class UserLogin(BaseModel):
    email:EmailStr
    password:str
    
class UserCreate(BaseModel):
    email:EmailStr
    name:str
    surname:str
    password:str
    phone_number:str

class UserVerify(BaseModel):
    email:EmailStr
    verification_code:str

class UserEdit(BaseModel):
    email:EmailStr
    name:str
    surname:str
    phone_number:str
    
class UserChangePassword(BaseModel):
    email:EmailStr
    password:str
    new_password:str

class UserDelete(BaseModel):
    email:EmailStr
    password:str

#-------------------------------
# Schemas for Login
#--------------------------------
class UserLogin(BaseModel):
    username:str # can be the admin username or user email
    password:str
    
    
#-------------------------------
# Schemas for Admin
#-------------------------------- 
class AdminCreate(BaseModel):
    username:str
    password:str

class AdminEdit(BaseModel):
    username:str
    password : str
    new_password : str

class LoanRequest(BaseModel):
    user_id: int
    email:EmailStr
    principal: int
    duration_weeks: int
    interest_rate: int

class LoanApproval(BaseModel):
    loan_id: int
    
class LoanStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    repayed = "repayed"
#-------------------------------
# ---------------- Models ------------------

class DepositFundsModel(BaseModel):
    amount: float             # Amount in ether to deposit

class RequestLoanModel(BaseModel):
    email: EmailStr
    amount: int               # Loan principal in wei

class LoanActionModel(BaseModel):
    loan_id: int              # ID of the loan to approve or reject

class RepayLoanModel(BaseModel):
    loan_id: int              # ID of the loan being repaid
    amount: float             # Repayment amount in ether (should cover principal + interest)
    borrower_email: EmailStr

class WithdrawFundsModel(BaseModel):
    amount: float             # Amount in ether to withdraw

class WalletCreate(BaseModel):
    email:EmailStr
    address :str
    private_key:str       