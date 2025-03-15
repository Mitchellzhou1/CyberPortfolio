import socks
import socket
from web3 import Web3

# Configure SOCKS5 Proxy
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 8123)
socket.socket = socks.socksocket

node_address = "http://192.168.2.99:50538"
web3 = Web3(Web3.HTTPProvider(node_address))
contract_address = "0x73511669fd4dE447feD18BB79bAFeAC93aB7F31f"  # Replace with a smart contract address
first_account = "0x521A57f6806E41eFa232AE1999DE3e267743c6f7"
first_account_priv = "0xdf985dfb71d98773aafcd44a52735b961ee99aa1c5ba981f1bdfd2c42723f65e"



# Check Connection
if web3.is_connected():
    print("Connected to Ethereum Node!")
else:
    print("Failed to connect to Ethereum Node.")
    exit()


contract_abi = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"inputs": [], "name": "current_user_count", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_count", "type": "uint256"}], "name": "decrement_current_user_count", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "name": "get_current_user_count", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_count", "type": "uint256"}], "name": "increment_current_user_count", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "secret", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "string", "name": "message", "type": "string"}], "name": "set_secret", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]



contract = web3.eth.contract(address=contract_address, abi=contract_abi)

my_account = contract.functions.owner().call()
address = my_account
print(my_account)

nonce = web3.eth.get_transaction_count(first_account)

# Updated gas price and limit
# gas_price = web3.to_wei('20', 'gwei')  # 20 Gwei
# gas_limit = 21000  # For a simple ETH transfer
#
# transaction = {
#     'nonce': nonce,
#     'to': my_account,
#     'value': web3.to_wei(1, 'ether'),
#     'gas': gas_limit,
#     'gasPrice': gas_price
# }
#
# # Sign the transaction
# signed_transaction = web3.eth.account.sign_transaction(transaction, first_account_priv)
#
# # Send the transaction
#
# transaction_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)
# print(f"Transaction Hash: {transaction_hash.hex()}")
# print(web3.eth.get_transaction(transaction_hash))
#


latest_block = web3.eth.get_block('latest')
print(f"Latest Block Number: {latest_block.number}")
print(f"Block Hash: {latest_block.hash.hex()}")
print(f"Timestamp: {latest_block.timestamp}")
print(f"Miner: {latest_block.miner}")
print(f"Gas Used: {latest_block.gasUsed}")
print(f"Gas Limit: {latest_block.gasLimit}")
print("\nTransactions in Latest Block:")
for tx_hash in latest_block.transactions:
    tx = web3.eth.get_transaction(tx_hash)
    print(f"  Tx Hash: {tx.hash.hex()}")
    print(f"    From: {tx['from']}")
    print(f"    To: {tx['to']}")
    print(f"    Value: {web3.from_wei(tx['value'], 'ether')} ETH")
    print(f"    Gas: {tx['gas']}")
    print(f"    Gas Price: {web3.from_wei(tx['gasPrice'], 'gwei')} Gwei")
balance = web3.eth.get_balance(address)
print(f"Address: {address}")
print(f"Balance: {web3.from_wei(balance, 'ether')} ETH")

contract_code = web3.eth.get_code(contract_address)
if contract_code:
    print(f"Smart Contract Code at {contract_address}: {contract_code.hex()}")
else:
    print(f"{contract_address} is not a smart contract.")