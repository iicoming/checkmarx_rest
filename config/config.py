# -*- encoding: utf-8 -*-
"""
@File    : __init_.py
@Time    : 2020/08/01 10:08
@Author  : iicoming@hotmail.com
"""

#### checkmarx config

checkmarx_domain = ""
checkmarx_username = ""
checkmarx_password = ""

checkmarx_rest_login_data = {
    "client_id": "resource_owner_client",
    "userName": "checkmarx_username".format(checkmarx_username=checkmarx_username),
    "password": "checkmarx_password".format(checkmarx_password=checkmarx_password),
    "grant_type": "password",
    "scope": "sast_rest_api",
    "client_secret": "014DF517-39D1-4453-B7B3-9930C563627C"}

checkmarx_rest_headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json;v=1.0",
    "Host": "{checkmarx_domain}".format(checkmarx_domain=checkmarx_domain),
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 "
}

#### redis config

REDIS_PASSWORD = ""
REDIS_IP = ""

REDIS_CONFIG = {
    "host": "{host}".format(host="REDIS_IP"),
    "port": 6379,
    "db": 0,
    "password": "REDIS_PASSWORD".format(REDIS_PASSWORD=REDIS_PASSWORD),
    "max_connections": 100,
    "socket_timeout": 5,
    "decode_responses": True
}

#### git ssh private key

private_key = """
ssh_private_key_content
"""
