from web3 import Web3
import socks
import socket

# Setting up the proxy to connect to Ethereum node
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 8123)
socket.socket = socks.socksocket

# Connect to the Ethereum node
node_address = "http://192.168.2.99:57286"
web3 = Web3(Web3.HTTPProvider(node_address))

# Contract address and ABI (including event details if available)
contract_address = "0x850EC3780CeDfdb116E38B009d0bf7a1ef1b8b38"
contract_abi = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {"inputs": [{"internalType": "bytes32", "name": "_key", "type": "bytes32"}], "name": "get_secret", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "bytes32[3]", "name": "_data", "type": "bytes32[3]"}], "name": "set_data", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "message", "type": "string"}], "name": "set_secret", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    # Add event definition here if the contract emits any events
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "bytes32[3]", "name": "_data", "type": "bytes32[3]"}], "name": "DataSet", "type": "event"}
]

# Initialize the contract
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# If the contract emits an event like DataSet on calling set_data, we can listen for it
event_filter = contract.events.DataSet.create_filter(fromBlock='latest')

# Check for new events
events = event_filter.get_new_entries()
for event in events:
    print(f"Data Set Event: {event['args']}")
