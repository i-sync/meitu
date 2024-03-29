#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import random
import time

import requests

# COLORS = [
#     "blue",
#     "indigo",
#     "purple",
#     "pink",
#     "red",
#     "orange",
#     "yellow",
#     "green",
#     "teal",
#     "cyan"
# ]


def countdown(time_sec):
    while time_sec:
        mins, secs = divmod(time_sec, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        time_sec -= 1

def date_filter(t):
    return time.strftime("%Y.%m.%d", time.localtime(t))

def datetime_filter(t):
    return time.strftime("%Y-%m-%d %X", time.localtime(t))


def test_proxy(proxies):
    """
    test proxy is available
    """
    targets = [
        #"https://www.xiurenb.com/",
        "https://www.meijuntu.com",
        # "https://www.google.com",
        #"https://www.baidu.com",
        #"https://www.viagle.cn"
    ]
    for target in targets:
        try:
            res = requests.get(target, proxies=proxies, timeout=5)
            if res.status_code == 200:
                print(res.status_code, proxies["https"], "avaiable!")
                return True
        except Exception as e:
            print(proxies, e)
    return False


path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')

def get_proxy():
    with open(f"{path}/proxies.json", "r+", encoding="utf-8") as f:
        proxys = json.load(f)

    if not len(proxys):
        return None
    for i in range(len(proxys)*2):
        index = random.randint(0, len(proxys) - 1)
        proxy = proxys[index]
        host = proxy["ip"]
        port = proxy["port"]
        protocol = proxy["protocols"]
        proxies = {
            "http": f"{protocol}://{host}:{port}",
            "https": f"{protocol}://{host}:{port}"
        }

        #if text_proxy(proxies):
        return proxies

    return None

def test_all_proxy():
    with open(f"{path}/proxies.json", "r+", encoding="utf-8") as f:
        proxys = json.load(f)

    if not len(proxys):
        return None
    for proxy in proxys:
        host = proxy["ip"]
        port = proxy["port"]
        protocol = proxy["protocols"]
        proxies = {
            "http": f"{protocol}://{host}:{port}",
            "https": f"{protocol}://{host}:{port}"
        }

        test_proxy(proxies)

    return None

def gen_valid_proxy():

    with open(f"{path}/proxies-all.json", "r+", encoding="utf-8") as f:
        proxys = json.load(f)

    if not len(proxys):
        return None

    valid_list = []
    for proxy in proxys:
        host = proxy["ip"]
        port = proxy["port"]
        protocol = proxy["protocols"]
        proxies = {
            "http": f"{protocol}://{host}:{port}",
            "https": f"{protocol}://{host}:{port}"
        }

        if test_proxy(proxies):
            valid_list.append(proxy)

    if len(valid_list):
        with open(f"{path}/proxies.json", "w+", encoding="utf-8") as f:
            json.dump(valid_list, f, indent=4)
    print("Done")
    return None

if __name__ == "__main__":
    print(__file__)
    print(get_proxy())
    # test_all_proxy()
    gen_valid_proxy()
