from urllib.parse import urlencode
from io import BytesIO
import requests

URL_BASE = "https://api.cddes.cn:4430"

def api_sms_code(phone, code, captcha_id):
    url = URL_BASE + "/api/sms/code"
    headers = {"X-Captcha-Id": captcha_id}
    data = {
        "phone": phone,
        "code": code
    }
    with requests.post(url, headers=headers, json=data) as rsp:
        if not rsp.ok:
            raise Exception(rsp.json().get("detail"))

def api_user_login(username, password):
    url = URL_BASE + "/api/user/login"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "password",
        "username": username,
        "password": password
    }
    encoded_data = urlencode(data)
    with requests.post(url, headers=headers, data=encoded_data) as rsp:
        if not rsp.ok:
            raise Exception(rsp.json().get("detail"))
        return rsp.json().get("access_token")

def api_get_user_me(token):
    url = URL_BASE + "/api/user/me"
    headers = {"Authorization": f"Bearer {token}"}
    with requests.get(url, headers=headers) as rsp:
        if not rsp.ok:
            raise Exception(rsp.json().get("detail"))
        return rsp.json()

def api_post_user_me(phone, sms_code, password):
    url = URL_BASE + "/api/user/me"
    data = {
        "phone": phone,
        "sms_code": sms_code,
        "password": password
    }
    with requests.post(url, json=data) as rsp:
        if not rsp.ok:
            raise Exception(rsp.json().get("detail"))

def api_delete_user_me(token, phone, sms_code):
    url = URL_BASE + "/api/user/me"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "phone": phone,
        "sms_code": sms_code
    }
    with requests.delete(url, headers=headers, json=data) as rsp:
        if not rsp.ok:
            raise Exception(rsp.json().get("detail"))

def api_post_user_me_password(token, old_password, new_password):
    url = URL_BASE + "/api/user/me/password"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "old_password": old_password,
        "new_password": new_password
    }
    with requests.post(url, headers=headers, json=data) as rsp:
        if not rsp.ok:
            raise Exception(rsp.json().get("detail"))

def api_post_phone_password(phone, sms_code, password):
    url = URL_BASE + f"/api/phone/{phone}/password"
    data = {
        "sms_code": sms_code,
        "password": password
    }
    with requests.post(url, json=data) as rsp:
        if not rsp.ok:
            raise Exception(rsp.json().get("detail"))

def api_post_user_me_phone(
    token, old_phone_sms_code, new_phone, new_phone_sms_code
):
    url = URL_BASE + "/api/user/me/phone"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "old_phone_sms_code": old_phone_sms_code,
        "new_phone": new_phone,
        "new_phone_sms_code": new_phone_sms_code
    }
    with requests.post(url, headers=headers, json=data) as rsp:
        if not rsp.ok:
            raise Exception(rsp.json().get("detail"))

def api_post_user_me_robots(token, robots):
    url = URL_BASE + "/api/user/me/robots"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"robots": robots}
    with requests.post(url, headers=headers, json=data) as rsp:
        if not rsp.ok:
            raise Exception(rsp.json().get("detail"))

def api_get_user_me_robots(token):
    url = URL_BASE + "/api/user/me/robots"
    headers = {"Authorization": f"Bearer {token}"}
    with requests.get(url, headers=headers) as rsp:
        if not rsp.ok:
            raise Exception(rsp.json().get("detail"))
        return rsp.json().get("robots")

def apt_get_captcha():
    url = URL_BASE + "/api/captcha"
    with requests.get(url) as rsp:
        if not rsp.ok:
            raise Exception(rsp.json().get("detail"))
        return BytesIO(rsp.content), rsp.headers.get('x-captcha-id')
