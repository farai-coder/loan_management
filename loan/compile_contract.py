from solcx import compile_standard, install_solc
import json

# Install a specific Solidity compiler version (if needed)
install_solc('0.8.0')

# Read the Solidity contract
with open("C:/Users/TIINO/Documents/projects/loan_management_backend/loan/LoanContract.sol", "r") as file:
    contract_source_code = file.read()

# Compile the contract
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {"LoanContract.sol": {"content": contract_source_code}},
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "evm.bytecode"]
            }
        }
    }
}, solc_version="0.8.0")

# Write the compiled contract to a JSON file (optional)
with open("C:/Users/TIINO/Documents/projects/loan_management_backend/loan/compiled_LoanContract.json", "w") as file:
    json.dump(compiled_sol, file, indent=2)

# Print a success message
print("Compilation complete. ABI and bytecode are saved in compiled_LoanContract.json")
