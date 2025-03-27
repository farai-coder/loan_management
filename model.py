import datetime
from enum import Enum
from sqlalchemy import (
    Boolean, Float, Integer, Column, BigInteger, String, Text, DateTime, ForeignKey,event,text
)
from sqlalchemy.orm import relationship
from data import Base, engine
from helper_functions import hash_password
from schemas import LoanStatusEnum

# -------------------------
# Database Models
# -------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer,index=True, primary_key=True,autoincrement=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    verification_code = Column(String, nullable=False)
    is_active = Column(Boolean,default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    wallet_address = Column(String, unique=True, index=True)
    private_key = Column(String)  # Store securely (e.g., encrypted)
    loans = relationship("Loan", back_populates="user")
    audit_logs = relationship("AuditLogs", back_populates="user")
    transactions = relationship("Transactions", back_populates="user")
    
class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    principal = Column(BigInteger)
    due_date = Column(BigInteger)
    interest_rate = Column(Integer)
    status = Column(String, default=LoanStatusEnum.pending)
    blockchain_loan_id = Column(Integer, nullable=True) # Cross-reference with blockchain
    to_pay_back = Column(Float,nullable=True) # amount to payback
    
    # Relationships
    transactions = relationship("Transactions", back_populates="loan")
    user = relationship("User", back_populates="loans")

class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    username = Column(String(50),nullable=False)
    password_hash = Column(Text,nullable=False)
    
    def __repr__(self):
        return f"id: {self.id} , username: {self.username}"
        
        

class AuditLogs(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action_taken = Column(String(255), nullable=False)
    action_timestamp = Column(DateTime, default=datetime.datetime.now)
    
    #relationships
    user = relationship("User", back_populates="audit_logs")
    


class Transactions(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey("loans.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    transaction_type = Column(String(50), nullable=False)
    transaction_amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, default=datetime.datetime.now)
    
    loan = relationship("Loan", back_populates="transactions")
    user = relationship("User", back_populates="transactions")




def insert_initial_records(engine, connection, **kwargs):
    """
    Inserts an initial record into the 'main_wallet' table when the database is created.
    """
    result = connection.execute(text("SELECT COUNT(*) FROM admin")).fetchone()
    if result[0] == 0:  # Check if table is empty
        connection.execute(Admin.__table__.insert().values(id = 1,username="admin",password_hash=hash_password("admin")))

# Attach event listener to insert the initial record
event.listen(Base.metadata, "after_create", insert_initial_records)

Base.metadata.create_all(bind=engine)
