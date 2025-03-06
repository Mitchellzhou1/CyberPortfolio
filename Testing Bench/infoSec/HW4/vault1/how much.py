import socks
import socket
from web3 import Web3

# Configure SOCKS5 Proxy
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 8123)
socket.socket = socks.socksocket
node_address = "http://192.168.2.99:50538"  # Replace with your node's address
web3 = Web3(Web3.HTTPProvider(node_address))

if web3.is_connected():
    print("Connected to Ethereum Node!")
else:
    print("Failed to connect to Ethereum Node.")
    exit()

# Public address of the wallet
wallet_address = ["0x521A57f6806E41eFa232AE1999DE3e267743c6f7",
                  '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
                  '0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199',
                  '0xC014BA5EC014ba5ec014Ba5EC014ba5Ec014bA5E',
                  ]

for wallet in wallet_address:
    balance_wei = web3.eth.get_balance(wallet)
    balance_eth = web3.from_wei(balance_wei, 'ether')

    print(f"Wallet Address: {wallet}")
    print(f"Balance: {balance_eth} ETH")
