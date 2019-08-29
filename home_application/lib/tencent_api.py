# -*- coding: utf-8 -*-
import requests
import json

class Tencent_Api:
    def __init__(self,url,data):
        self.url=url
        self.data=json.dumps(data)
        
    def search_host(self):
        r = requests.post(self.url, data = self.data)
        return r.text

class Handle_Api:
    def handle_host(self,bk_token):
        ip=[]
        self.token=bk_token
        url='http://paas.aikaqiche.net/api/c/compapi/v2/cc/search_host/'
     
        data={
            "bk_app_code": "confd",
            "bk_app_secret": "359b9cf6-ba4c-479e-997b-a1969368be2d",
            "bk_token": self.token,
           # "bk_username":"hao.wen",    # 需要加应用白名单
        }
        req=json.loads(Tencent_Api(url=url,data=data).search_host())
        for ipaddr in req['data']['info']:
            ip.append(ipaddr['host']['bk_host_innerip'])
         
        return ip


if __name__=='__main__':
    print Handle_Api().handle_host()