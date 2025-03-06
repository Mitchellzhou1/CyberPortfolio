
from solcx import compile_standard
import json

with open("SekritVault.sol", "r") as file:
    contract_source_code = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"contract.sol": {"content": contract_source_code}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.0",
)

abi = compiled_sol["contracts"]["contract.sol"]["SekritVault"]["abi"]
bytecode = compiled_sol["contracts"]["contract.sol"]["SekritVault"]["evm"]["bytecode"]["object"]

with open("abi.json", "w") as abi_file:
    json.dump(abi, abi_file)

print("ABI:", abi)
print("Bytecode:", bytecode)
