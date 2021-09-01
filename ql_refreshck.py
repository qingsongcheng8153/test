# 在这里输入青龙面板用户名密码，如果不填写，就自动从auth.json中读取
username = ""
password = ""

import requests
import time
import json
import re

requests.packages.urllib3.disable_warnings()

token = ""
if username == "" or password == "":
    f = open("/ql/config/auth.json")
    auth = f.read()
    auth = json.loads(auth)
    username = auth["username"]
    password = auth["password"]
    token = auth["token"]
    f.close()


def gettimestamp():
    return str(int(time.time() * 1000))


def login(username, password):
    url = "http://127.0.0.1:5700/api/login?t=%s" % gettimestamp()
    data = {"username": username, "password": password}
    r = s.post(url, data)
    s.headers.update({"authorization": "Bearer " + json.loads(r.text)["data"]["token"]})


def getitem(key):
    url = "http://127.0.0.1:5700/api/envs?searchValue=%s&t=%s" % (key, gettimestamp())
    r = s.get(url)
    item = json.loads(r.text)["data"]
    return item


def getckitem(key):
    url = "http://127.0.0.1:5700/api/envs?searchValue=JD_COOKIE&t=%s" % gettimestamp()
    r = s.get(url)
    for i in json.loads(r.text)["data"]:
        if key in i["value"]:
            return i
    return []


def wstopt(wskey):
    try:
        url = "https://api.m.jd.com/client.action?functionId=switchConfig&clientVersion=10.0.6&build=88852&client=android&d_brand=Xiaomi&d_model=M2102J2SC&osVersion=11&screen=2206*1080&partner=xiaomi001&oaid=d54cc4674115badb&openudid=9f7e5a6ab7440031&eid=eidA183e412237l543bf826f1f63bdfabb17d5e29b19eaed85c1fb13OFaLlDDQzhB85DgX21RjOfnNro+gaVwe4j3x5j3ry7Yx58BfkmtK9GKq9rAK&sdkVersion=30&lang=zh_CN&uuid=9f7e5a6ab7440031&aid=9f7e5a6ab7440031&area=7_517_518_5791&networkType=UNKNOWN&wifiBssid=unknown&uts=0f31TVRjBSsfRbGER3FTwU4lhlJU61gJjp3Np7myESm0Y61GqKRDiFjxcOegwy%2FTg2Sl5t6Z5AvDSLgLA0TmlX5aWwBGZ7XBSXwZUIzP6ZMmZ6GsEf1xkxAdR6tGe4Byfh%2FWRY5QG7%2BZmwZSEHXUYgvYcz5fkqBAQUBAPKIhG67b1yAvr0Hw3X5xaMmc%2BwWpWWtiEQNw44eTSzhCtknAgQ%3D%3D&uemps=0-0&harmonyOs=0&st=1630503114696&sign=ad4e4d5f498f73a9f64fdc0153affb30&sv=12"
        headers = {
            "Host": "signer.nz.lu",
            "user-agent": "Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        }
        data = {"wskey": wskey, "key": "xb3z4z2m3n847"}
        r = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
        return r.text
    except:
        return "error"


def update(text, qlid):
    url = "http://127.0.0.1:5700/api/envs?t=%s" % gettimestamp()
    s.headers.update({"Content-Type": "application/json;charset=UTF-8"})
    data = {
        "name": "JD_COOKIE",
        "value": text,
        "_id": qlid
    }
    r = s.put(url, data=json.dumps(data))
    if json.loads(r.text)["code"] == 200:
        return True
    else:
        return False


def insert(text):
    url = "http://127.0.0.1:5700/api/envs?t=%s" % gettimestamp()
    s.headers.update({"Content-Type": "application/json;charset=UTF-8"})
    data = []
    data_json = {
        "value": text,
        "name": "JD_COOKIE"
    }
    data.append(data_json)
    r = s.post(url, json.dumps(data))
    if json.loads(r.text)["code"] == 200:
        return True
    else:
        return False


if __name__ == '__main__':
    s = requests.session()
    if token == "":
        login(username, password)
    else:
        s.headers.update({"authorization": "Bearer " + token})
    wskeys = getitem("JD_WSCK")
    count = 1
    for i in wskeys:
        if i["status"] == 0:
            ptck = wstopt(i["value"])
            wspin = re.findall(r"pin=(.*?);", i["value"])[0]
            if ptck == "wskey错误":
                print("第%s个wskey可能过期了,pin为%s" % (count, wspin))
            elif ptck == "未知错误" or ptck == "error":
                print("第%s个wskey发生了未知错误,pin为%s" % (count, wspin))
            else:
                ptpin = re.findall(r"pt_pin=(.*?);", ptck)[0]
                item = getckitem("pt_pin=" + ptpin)
                if item != []:
                    qlid = item["_id"]
                    if update(ptck, qlid):
                        print("第%s个wskey更新成功,pin为%s" % (count, wspin))
                    else:
                        print("第%s个wskey更新失败,pin为%s" % (count, wspin))
                else:
                    if insert(ptck):
                        print("第%s个wskey添加成功" % count)
                    else:
                        print("第%s个wskey添加失败" % count)
            count += 1
        else:
            print("有一个wskey被禁用了")
