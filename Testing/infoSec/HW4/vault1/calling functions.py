

import socks
import socket
from web3 import Web3
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 8123)
socket.socket = socks.socksocket

node_address = "http://192.168.2.99:49795"
web3 = Web3(Web3.HTTPProvider(node_address))

contract_address = "0x73511669fd4dE447feD18BB79bAFeAC93aB7F31f"  # Replace with actual address
contract_abi = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"inputs": [], "name": "current_user_count", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_count", "type": "uint256"}], "name": "decrement_current_user_count", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "name": "get_current_user_count", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_count", "type": "uint256"}], "name": "increment_current_user_count", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "secret", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "string", "name": "message", "type": "string"}], "name": "set_secret", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

secret = contract.functions.secret().call()
print(secret)
