#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests
import time
import md5
import json

import qiniu
from qiniu import CdnManager

def clear_qiniu(url):
    # 账户ak，sk
    access_key = 'MeUQwQAvlOJ7C-wVasdfcCsJIvq0PppRT3VrYKog34xv'
    secret_key = 'wAwXfUY12YD3vkHa_Qqi9S3F31RF6F8reIP7cWj-jj'

    auth = qiniu.Auth(access_key=access_key, secret_key=secret_key)
    cdn_manager = CdnManager(auth)

   # 需要刷新的文件链接
    urls = [url]
    # 刷新链接
    refresh_url_result = cdn_manager.refresh_urls(urls) 
 
    return refresh_url_result[0]['requestId']


def yun_config():
    """
    云端cdn基础配置
    """
    Date=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    AppID='040df59cfa41d034ceasdf13dd8a7ebf6f1'
    AppSecret='4844a6610445'
    MD5=md5.new()
    MD5.update('%s%s%s' %(Date,AppSecret,AppID))
    Sgn=MD5.hexdigest()
    return (AppID,Sgn,Date,AppSecret)

def yun_task(data):
    '''
    提交任务 
    '''
    AppID,Sgn,Date,AppSecret=yun_config()
    url='https://webapi.1ecloud.com/content/add_purge'
    d=json.dumps(data)
    res= requests.post(url,d)
    return json.loads(res.text)