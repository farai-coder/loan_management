import json
import os
from web3 import Web3


ganache_url = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(ganache_url))
if not w3.is_connected():
    raise Exception("Unable to connect to Ganache network")

# Load contract ABI and set the deployed contract address.
with open("C:/Users/TIINO/Documents/projects/loan_management_backend/loan/compiled_LoanContract.json", "r") as file:
    compiled_sol = json.load(file)

# Access the contract interface using the correct keys
contract_interface = compiled_sol["contracts"]["LoanContract.sol"]["LoanSystem"]

# Extract the ABI and bytecode
contract_abi = contract_interface["abi"]
# Set your deployed contract address here or via environment variable.
contract_address = os.environ.get("CONTRACT_ADDRESS", "0x466f9DEB006f82291827945b62485Cb6571F5cC4")
loan_contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Admin wallet details
admin_address = "0x92E8b7B75854be267Cbe394C64486f25D8A8AB8b"    # Replace with your admin wallet address
admin_private_key = "0xf9c76d364937562bed940465cff6159a15deb1b9c08ecf39f1abe4d3993c8b73"    # Replace with your admin private key
