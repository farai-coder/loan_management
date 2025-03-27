import bcrypt
from web3 import Web3
from data import SessionLocal
from web3.exceptions import TransactionNotFound

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if a given password matches the stored hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

# Hash password
def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

# -------------- Helper Function ----------------

    
def serialize_receipt(receipt):
    """
    Converts the transaction receipt into a JSON-serializable dictionary.
    """
    def convert_bytes_to_hex(obj):
        if isinstance(obj, bytes):
            return obj.hex()
        elif isinstance(obj, list):
            return [convert_bytes_to_hex(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: convert_bytes_to_hex(value) for key, value in obj.items()}
        else:
            return obj

    return convert_bytes_to_hex(dict(receipt))

def build_and_send_txn(w3, func, from_address, private_key, value=0):
    """
    Helper function to build, sign, and send a transaction.
    """
    nonce = w3.eth.get_transaction_count(from_address)
    txn = func.build_transaction({
        'from': from_address,
        'nonce': nonce,
        'gas': func.estimate_gas({'from': from_address, 'value': value}),
        'gasPrice': w3.eth.gas_price,
        'value': value,
    })
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return serialize_receipt(receipt)
    except TransactionNotFound:
        print(f"Transaction {tx_hash.hex()} not found.")
        return None
    except Exception as e:
        print(f"Error during transaction: {e}")
        return None
    