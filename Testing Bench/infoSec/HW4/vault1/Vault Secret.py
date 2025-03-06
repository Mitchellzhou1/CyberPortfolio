import json
from solcx import compile_standard, install_solc, get_installable_solc_versions


def compile_solidity(contract_file):
    # Check available Solidity versions
    available_versions = get_installable_solc_versions()
    print(f"Available Solidity versions: {available_versions}")

    # Install a specific Solidity compiler version (e.g., '0.8.0')
    # Make sure the version matches the one you're using in your contract
    solc_version = '0.8.0'
    install_solc(solc_version)

    # Read the .sol file
    with open(contract_file, 'r') as file:
        contract_source = file.read()

    # Prepare the Solidity source in the format expected by solcx
    compiled = compile_standard({
        "language": "Solidity",
        "sources": {
            contract_file: {
                "content": contract_source
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode"]
                }
            }
        }
    })

    # Extract ABI from the compiled contract
    contract_name = list(compiled['contracts'][contract_file].keys())[0]
    abi = compiled['contracts'][contract_file][contract_name]['abi']

    return abi


def save_abi_to_file(abi, output_file):
    # Save ABI to a JSON file
    with open(output_file, 'w') as file:
        json.dump(abi, file, indent=4)


def main():
    # Specify your Solidity contract file and output file for ABI
    contract_file = "SekritVault.sol"
    output_file = "abi.json"

    try:
        # Compile the Solidity contract and get the ABI
        abi = compile_solidity(contract_file)
        print("ABI generated successfully.")

        # Save the ABI to a JSON file
        save_abi_to_file(abi, output_file)
        print(f"ABI saved to {output_file}")

    except Exception as e:
        print(f"Error compiling contract: {e}")


if __name__ == "__main__":
    main()
