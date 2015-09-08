'''
  抓取贴吧
  1、抓取列表页，取出关键词是“洗”的帖子
  2、楼主的的帖子要包含最少一张图片，且回复数必须大于3
  3、判断库中是否有该id
  4、如果库中没有，则图像识别，保存下图片信息，并入库
'''
#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#import logging; logging.basicConfig(level=logging.INFO)
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import re
from models import WeaponChangeTopic
import orm
import json
import base64
import urllib.parse

# 数据库配置
dbHost='115.28.134.55'
dbUser='root'
dbPassword='5211314'
dbName='d3'

def urlencode(str) :
    reprStr = repr(str).replace(r'\x', '%')
    return reprStr[1:-1]

@asyncio.coroutine
def wget(url):
    try:
        response = yield from aiohttp.get(url)
    except aiohttp.errors.ClientOSError as e:
        print('[error url:%s]  %s' % (url, e))
        exit()
    else:
        return (yield from response.text())

@asyncio.coroutine
def getImgWords(imgUrl):
    bImage = ''
    m = re.match(r'^http.+/(.+)', imgUrl)
    imgName = m.group(1) if m is not None else None
    if imgName is None:
        pass
    try:
        r = yield from aiohttp.get(imgUrl)
    except aiohttp.errors.ClientOSError as e:
        print('[error url:%s]  %s' % (url, e))
    else:
        bImage = yield from r.read()
        with open('/Users/chocobobo/Work/d3/public/weapon/tieba/'+imgName, 'wb') as f:
           f.write(bImage)
        #百度OCR
        payload = {'fromdevice':'pc',
                           'clientip':'115.28.134.55',
                           'detecttype':'LocateRecognize',
                           'languagetype':'CHN_ENG',
                           'imagetype':'1',
                           'image': base64.b64encode(bImage)
                           }
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                            "apikey": "0830a440f9e1b9a31c5e807fa2f0ab61"
                          }
        rdd = yield from aiohttp.post('http://apis.baidu.com/apistore/idlocr/ocr', data=payload, headers=headers)
        return (yield from rdd.text())

@asyncio.coroutine
def saveImg(imgName,b):
    with open('/Users/chocobobo/Work/d3/public/weapon/tieba/'+imgName, 'w') as f:
        f.write(b)

@asyncio.coroutine
def getTopic(loop,url):
    topicHtml = yield from wget(url)
    if len(topicHtml) > 100:
        soup = BeautifulSoup(topicHtml, 'html.parser')
        topic = []
        isImg = False
        m = re.match(r'^http.+/(\d+)', url)
        topicId = m.group(1) if m is not None else 0
        for content in soup.find_all(checkTopic):
            img = content.find(class_="BDE_Image")
            if img is not None and isImg == False:
                isImg = True
                imgUrl = img.get("src")
            topic.append(content.get_text())
        if imgUrl is not None and isImg and len(topic) > 5:
            print('=============%s==============' % soup.title.string)
            print(url)
            yield from orm.create_pool(loop=loop,host=dbHost, user=dbUser, password=dbPassword, db=dbName)
            num = yield from WeaponChangeTopic.findNumber('id', 'topicId=?', topicId)
            if num is None:
                words = yield from getImgWords(imgUrl)
                print(json.loads(words))
               # try:
               #     wordList = json.loads(words)['retData']
               #     if len(wordList) > 0:
               #         pass
               # except ValueError as e:
               #     print("baidu ocr json error: %s" % words)


def checkTitle(tag):
    return tag.name == "a" and tag.get("class") == ['j_th_tit', ''] and re.compile("洗").search(tag.string)

def checkTopic(tag):
    return tag.name == "div" and tag.get("class") == ['d_post_content', 'j_d_post_content', '']

if __name__ == '__main__':
    #抓取帖子列表
    titleList = []
    topicUrl = 'http://tieba.baidu.com/f?ie=utf-8&kw=%E6%9A%97%E9%BB%913'
    loop = asyncio.get_event_loop()
    topicListHtml = loop.run_until_complete(wget(topicUrl))
    soup = BeautifulSoup(topicListHtml, 'html.parser')
    for title in soup.find_all(checkTitle):
        titleList.append(title.get("href"))
    #抓取帖子内容
    if len(titleList) > 0:
        # 抓取内容
        tasks = [getTopic(loop,'http://tieba.baidu.com'+url) for url in titleList]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

