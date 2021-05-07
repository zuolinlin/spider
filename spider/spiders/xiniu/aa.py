import json

import requests

payload = {
    "from": 1000,
    "size": 1000,
    "query": "吉利汽车",
    "fields": ["title"],
    "gte": 1000000000,
    "lte": 1999999999,
    "contain_site_name": "*",
    "contain_site_tag": "*",
    "contain_emotion": "*",
    "contain_site_client": "*",
    "not_contain_site_tag": "微博",
    "not_contain_site_name": "",
    "not_contain_emotion": "",
    "sort": {
        "publish_stamp": {
            "order": "asc"
        }
    },
    "_source": ["_id", "title", "emotion", "full_url", "content", "publish_stamp", "@timestamp"]
}

header = {
    "Content-Type": "application/json; charset=UTF-8",
    # ... other header
}
param = json.dumps(payload)
# body提交的get请求
r = requests.get("http://47.113.194.169:1323/article", data=param, headers=header)
print(r)
param = json.dumps(payload)
# 参数拼接提交的get请求
r = requests.get("http://47.113.194.169:1323/article", params=payload)

# body提交的post请求
r = requests.post("http://47.113.194.169:1323/article", data=param, headers=header)

# 参数拼接提交的post请求
r = requests.post("http://47.113.194.169:1323/article", params=payload)
print(r)
