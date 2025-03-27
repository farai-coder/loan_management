from web3 import Web3
import json

# Connect to Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
if not web3.is_connected():
    raise Exception("Unable to connect to Ganache")

# Admin wallet details
admin_account = "0x92E8b7B75854be267Cbe394C64486f25D8A8AB8b"        # Replace with your admin wallet address
admin_private_key = "0xf9c76d364937562bed940465cff6159a15deb1b9c08ecf39f1abe4d3993c8b73" 

# Load compiled contract data (ABI and Bytecode)
# For example, you might have compiled your contract with solcx and saved the output.
with open("C:/Users/TIINO/Documents/projects/loan_management_backend/loan/compiled_LoanContract.json", "r") as file:
    compiled_sol = json.load(file)

# Access the contract interface using the correct keys
contract_interface = compiled_sol["contracts"]["LoanContract.sol"]["LoanSystem"]

# Extract the ABI and bytecode
abi = contract_interface["abi"]
bytecode = contract_interface["evm"]["bytecode"]["object"]

# Create contract object
LoanSystem = web3.eth.contract(abi=abi, bytecode=bytecode)

# Build deployment transaction
nonce = web3.eth.get_transaction_count(admin_account)
transaction = LoanSystem.constructor().build_transaction({
    'from': admin_account,
    'nonce': nonce,
    'gas': 3000000,
    'gasPrice': web3.to_wei('20', 'gwei')
})

# Sign the transaction with the admin's private key
signed_txn = web3.eth.account.sign_transaction(transaction, private_key=admin_private_key)

# Send the transaction
tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
print(f"Transaction hash: {tx_hash.hex()}")

# Wait for the transaction receipt
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Contract deployed at address: {tx_receipt.contractAddress}")
