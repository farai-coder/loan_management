from requests import Session
from fastapi import APIRouter, Depends, HTTPException
from helper_functions import get_db, build_and_send_txn
from model import Loan, User
from schemas import DepositFundsModel, LoanActionModel, LoanStatusEnum, RepayLoanModel, RequestLoanModel, WithdrawFundsModel
from contract_wallet_details import *
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/depositFunds")
def deposit_funds(deposit: DepositFundsModel):
    """
    Endpoint to deposit funds into the contract.
    Only callable by the admin.
    """
    try:
        # Convert ether to wei
        value = w3.to_wei(deposit.amount, 'ether')
        func = loan_contract.functions.depositFunds()
        receipt = build_and_send_txn(func=func,w3=w3, from_address=admin_address, private_key=admin_private_key, value=value)
        # later add to the transaction model in the database
        return {"status": "Funds deposited", "tx_receipt": receipt["transactionHash"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/requestLoan")
def request_loan(loan_request: RequestLoanModel, db: Session = Depends(get_db)):
    """
    Endpoint for a borrower to request a loan.
    """
    try:
        today = datetime.now()
        borrower = db.query(User).filter(User.email == loan_request.email).first()
        if not borrower:
            raise HTTPException(status_code=404, detail="User not found")
        borrower_address = borrower.wallet_address
        borrower_private_key = borrower.private_key
        
        amount = w3.to_wei(loan_request.amount, 'ether')
        
        func = loan_contract.functions.requestLoan(
            amount,
            1209600, # 14 days in seconds
            20 # 20% interest rate
        )
        
        #calculate the total amount the borrower must pay back in ether
        pay_back = loan_request.amount + (loan_request.amount * 20) / 100
        
        #send the transaction
        receipt = build_and_send_txn(w3, func, borrower_address, borrower_private_key)

        if receipt is None: #Handle Transaction Failure
            raise HTTPException(status_code=500, detail="Transaction failed")
        
        # Get the LoanRequested event signature (topic)
        loan_requested_event_signature = w3.keccak(text="LoanRequested(uint256,address,uint256,uint256,uint256)").hex()

        # Iterate through the logs to find the LoanRequested event
        loan_id = None
        for log in receipt['logs']:
            if log['topics'][0].hex() == loan_requested_event_signature:
                # Decode the event data
                event_data = loan_contract.events.LoanRequested().process_log(log)
                loan_id = event_data['args']['loanId']
                break
        # add the loan to the loan table
        new_loan = Loan(
            user_id=borrower.id,
            principal=loan_request.amount,
            due_date= today + timedelta(days=14), # calculate todays date and add 14 days
            interest_rate=20,
            status=LoanStatusEnum.pending,
            blockchain_loan_id=loan_id,
            to_pay_back = pay_back   
        )
        db.add(new_loan)
        db.commit()
        
        return {"status": receipt["status"],
                "tx_receipt": receipt["transactionHash"],
                "loan_id": loan_id,
                "amount_to_returned" : pay_back
                }
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/approveRequest")
def approve_request(loan_action: LoanActionModel,db: Session = Depends(get_db)):
    """
    Endpoint for the admin to approve a pending loan request.
    """
    try:
        func = loan_contract.functions.approveRequest(loan_action.loan_id)
        receipt = build_and_send_txn(w3=w3,func=func, from_address=admin_address, private_key=admin_private_key)
        loan = db.query(Loan).filter(Loan.blockchain_loan_id == loan_action.loan_id).first()
        loan.status = LoanStatusEnum.approved
        db.commit()
        return {"status": "Loan approved", "tx_receipt": receipt["transactionHash"],"loan_id" : loan_action.loan_id}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rejectRequest")
def reject_request(loan_action: LoanActionModel,db: Session = Depends(get_db)):
    """
    Endpoint for the admin to reject a pending loan request.
    """
    try:
        func = loan_contract.functions.rejectRequest(loan_action.loan_id)
        receipt = build_and_send_txn(w3=w3,func=func, from_address=admin_address, private_key=admin_private_key)
        loan  = db.query(Loan).filter(Loan.blockchain_loan_id == loan_action.loan_id).first()
        loan.status = LoanStatusEnum.rejected
        db.commit()
        return {"status": "Loan rejected", "tx_receipt": receipt["transactionHash"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/repayLoan")
def repay_loan(repay: RepayLoanModel,db: Session = Depends(get_db)):
    """
    Endpoint for the borrower to repay an approved loan.
    The repayment amount should include the principal plus interest.
    """
    try:
        user = db.query(User).filter(User.email == repay.borrower_email).first()
        loan  = db.query(Loan).filter(Loan.id == repay.loan_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        borrower_address = user.wallet_address
        borrower_private_key = user.private_key  
        
        
        # Convert ether to wei for the repayment value
        value = w3.to_wei(repay.amount, 'ether')
        
        #update the loan status to approved 
        loan.status  = LoanStatusEnum.repayed
        db.commit()
        
        func = loan_contract.functions.repayLoan(repay.loan_id)
        receipt = build_and_send_txn(w3=w3, func=func, from_address=borrower_address, private_key=borrower_private_key, value=value)
        
        return {"status": "Loan repaid", "tx_receipt": receipt["transactionHash"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/withdrawMoney")
def withdraw_money(withdraw: WithdrawFundsModel):
    """
    Endpoint for the admin to withdraw funds from the contract.
    """
    try:
        # Convert the withdrawal amount to wei
        wei_amount = w3.to_wei(withdraw.amount, 'ether')
        func = loan_contract.functions.withdrawMoney(wei_amount)
        receipt = build_and_send_txn(w3 =w3, func= func, from_address=admin_address, private_key=admin_private_key)
        return {"status": "Funds withdrawn", "tx_receipt": receipt["transactionHash"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



