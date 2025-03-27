// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title LoanSystem
 * @dev Implements a basic loan system with admin (lender) and borrower roles.
 *      The admin can deposit funds, approve or reject loan requests, and withdraw money.
 *      Borrowers can request loans and repay them (principal + interest).
 */
contract LoanSystem {
    // Address of the admin (lender)
    address public admin;
    // Counter for loan IDs
    uint256 public loanCounter;

    // Enum for tracking the state of a loan request
    enum LoanState { Pending, Approved, Rejected, Repaid }

    // Struct representing a loan request
    struct Loan {
        address borrower;     // Borrower's wallet address
        uint256 amount;       // Loan principal amount
        uint256 duration;     // Duration of the loan (in seconds)
        uint256 interestRate; // Interest rate as a percentage (e.g., 10 means 10%)
        uint256 dueDate;      // Timestamp when the loan is due (set upon approval)
        LoanState state;      // Current state of the loan
    }

    // Mapping from a loan ID to a Loan
    mapping(uint256 => Loan) public loans;

    // Events for logging significant actions
    event FundsDeposited(address indexed admin, uint256 amount);
    event LoanRequested(uint256 indexed loanId, address indexed borrower, uint256 amount, uint256 duration, uint256 interestRate);
    event LoanApproved(uint256 indexed loanId, address indexed borrower, uint256 amount, uint256 dueDate);
    event LoanRejected(uint256 indexed loanId, address indexed borrower);
    event LoanRepaid(uint256 indexed loanId, address indexed borrower, uint256 repaymentAmount);
    event FundsWithdrawn(address indexed admin, uint256 amount);

    // Modifier to restrict functions to only the admin
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    // Constructor sets the contract deployer as the admin
    constructor() {
        admin = msg.sender;
        loanCounter = 0;
    }

    /**
     * @dev depositFunds allows the admin to deposit funds into the contract.
     *      Only callable by the admin.
     */
    function depositFunds() external payable onlyAdmin {
        require(msg.value > 0, "Must deposit a positive amount");
        emit FundsDeposited(msg.sender, msg.value);
    }

    /**
     * @dev requestLoan allows a borrower to request a loan.
     * @param _amount The desired loan amount.
     * @param _duration Loan duration in seconds.
     * @param _interestRate Interest rate percentage.
     */
    
    function requestLoan(uint256 _amount, uint256 _duration, uint256 _interestRate) external {
        require(_amount > 0, "Loan amount must be positive");
        require(_duration > 0, "Duration must be positive");

        loans[loanCounter] = Loan({
            borrower: msg.sender,
            amount: _amount,
            duration: _duration,
            interestRate: _interestRate,
            dueDate: 0, // To be set on approval
            state: LoanState.Pending
        });

        emit LoanRequested(loanCounter, msg.sender, _amount, _duration, _interestRate);
        loanCounter++;
    }

    /**
     * @dev approveRequest allows the admin to approve a pending loan request.
     *      It transfers the loan amount from the contract to the borrower's wallet.
     * @param _loanId The ID of the loan request to approve.
     */
    function approveRequest(uint256 _loanId) external onlyAdmin {
        Loan storage loan = loans[_loanId];
        require(loan.state == LoanState.Pending, "Loan is not pending");
        require(address(this).balance >= loan.amount, "Insufficient funds in contract");

        // Update loan state and set due date (current time + duration)
        loan.state = LoanState.Approved;
        loan.dueDate = block.timestamp + loan.duration;
        // Transfer the loan amount to the borrower
        payable(loan.borrower).transfer(loan.amount);
        emit LoanApproved(_loanId, loan.borrower, loan.amount, loan.dueDate);
    }

    /**
     * @dev rejectRequest allows the admin to reject a pending loan request.
     *      No funds are transferred in this case.
     * @param _loanId The ID of the loan request to reject.
     */
    function rejectRequest(uint256 _loanId) external onlyAdmin {
        Loan storage loan = loans[_loanId];
        require(loan.state == LoanState.Pending, "Loan is not pending");
        loan.state = LoanState.Rejected;
        emit LoanRejected(_loanId, loan.borrower);
    }

    /**
     * @dev repayLoan allows a borrower to repay an approved loan.
     *      The repayment must cover the principal plus the calculated interest.
     * @param _loanId The ID of the loan being repaid.
     */
    function repayLoan(uint256 _loanId) external payable {
        Loan storage loan = loans[_loanId];
        require(loan.state == LoanState.Approved, "Loan is not approved");
        require(msg.sender == loan.borrower, "Only borrower can repay the loan");

        // Calculate total repayment amount: principal + interest.
        uint256 interest = (loan.amount * loan.interestRate) / 100;
        uint256 repaymentAmount = loan.amount + interest;
        require(msg.value >= repaymentAmount, "Insufficient repayment amount");

        // Mark the loan as repaid
        loan.state = LoanState.Repaid;
        emit LoanRepaid(_loanId, loan.borrower, msg.value);
    }

    /**
     * @dev withdrawMoney allows the admin to withdraw funds from the contract.
     * @param _amount The amount to withdraw.
     */
    function withdrawMoney(uint256 _amount) external onlyAdmin {
        require(address(this).balance >= _amount, "Insufficient funds in contract");
        payable(admin).transfer(_amount);
        emit FundsWithdrawn(admin, _amount);
    }
}
