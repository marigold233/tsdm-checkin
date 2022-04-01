#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from io import StringIO
from wurlitzer import pipes, STDOUT
import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
from functools import wraps


def gotify(url, level):  # url: http://localhost:8008/message?token=<apptoken>
    def decorator(func):
        @wraps(func)
        def out(*args, **kwargs):
            # f = io.StringIO()
            # with redirect_stdout(f):
            #    result = func(*args, **kwargs)
            # func_print = f.getvalue()
            out = StringIO()
            with pipes(stdout=out, stderr=STDOUT):
                result = func(*args, **kwargs)
            stdout = out.getvalue()
            print(stdout)
            response = requests.post(
                url,
                json={
                    "message": stdout,
                    "priority": level,
                    "title": func.__name__,
                },
            )
            return result

        return out

    return decorator


def ding_bot(url, secret):
    def decorator(func):
        @wraps(func)
        def out(*args, **kwargs):
            out = StringIO()
            with pipes(stdout=out, stderr=STDOUT):
                result = func(*args, **kwargs)
            stdout = out.getvalue()
            print(stdout)
            timestamp = str(round(time.time() * 1000))
            secret_enc = secret.encode("utf-8")
            string_to_sign = f"{timestamp}\n{secret}"
            string_to_sign_enc = string_to_sign.encode("utf-8")
            hmac_code = hmac.new(
                secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
            ).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
            headers = {"Content-Type": "application/json;charset=utf-8"}
            data = {
                "msgtype": "text",  # 发送消息类型为文本
                "at": {
                    "isAtAll": False,  # True为@所有人
                },
                "text": {
                    "content": stdout,
                },
            }
            url1 = url + "&timestamp=" + timestamp + "&sign=" + sign
            res = requests.post(url1, json=data, headers=headers)
            return result

        return out

    return decorator
