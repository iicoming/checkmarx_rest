# -*- encoding: utf-8 -*-
"""
@File    : CheckmarxBase.py
@Time    : 2020/08/01 10:08
@Author  : iicoming@hotmail.com
"""

import sys
import time

import redis
import requests

from config.config import REDIS_CONFIG, checkmarx_domain, checkmarx_rest_headers, checkmarx_rest_login_data


class CheckmarxBase:
    def __init__(self):
        self.checkmarx_base_url = "https://{checkmarx_domain}/cxrestapi".format(
            checkmarx_domain=checkmarx_domain)

        self._login()
        self.today = time.strftime("%Y-%m-%d", time.localtime())
        self.client = redis.StrictRedis(**REDIS_CONFIG)

    def catch_exception(func):
        time_now = time.strftime("%Y-%m-%d", time.localtime())

        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                return res
            except Exception as e:
                print(time_now +
                      ': Error method: \n\t%s,\nException info:\n\t%s' %
                      (func.__name__, e))
                sys.exit()

        return wrapper

    @catch_exception
    def _login(self):
        checkmarx_login = self.checkmarx_base_url + '/auth/identity/connect/token'

        r = requests.post(checkmarx_login,
                          data=checkmarx_rest_login_data,
                          headers=checkmarx_rest_headers)

        if r.status_code != 200:
            raise Exception(" login Failed. ")

        access_token = r.json().get('access_token')
        token_type = r.json().get('token_type')
        authorization = token_type + ' ' + access_token
        checkmarx_rest_headers["Authorization"] = authorization
        checkmarx_rest_headers['Content-Type'] = "application/json;v=1.0"
        self.checkmarx_headers = checkmarx_rest_headers
