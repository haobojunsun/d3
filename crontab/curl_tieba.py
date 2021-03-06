''' 抓取贴吧
  1、抓取列表页，取出关键词是“洗”的帖子
  2、楼主的的帖子要包含最少一张图片，且回复数必须大于3
  3、判断库中是否有该id
  4、如果库中没有，则图像识别，保存下图片信息，并入库
'''
#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
#import logging; logging.basicConfig(level=logging.INFO)
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import re
from models import WeaponChangeTopic
import orm
import json
import base64
import urllib.request



# 数据库配置
dbHost='115.28.134.55'
dbUser='root'
dbPassword='5211314'
dbName='d3'


# 文件位置
dirBase='/Users/chocobobo/Work/d3/public/weapon/tieba/'
#dirBase='/data/htdocs/d3/public/weapon/tieba/'


@asyncio.coroutine
def wget(url):
    try:
        response = yield from aiohttp.get(url)
    except aiohttp.errors.ClientOSError as e:
        print('[error url:%s]  %s' % (url, e))
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
        with open(dirBase+imgName, 'wb') as f:
           f.write(bImage)
        #百度OCR
        payload = {'fromdevice':'pc',
                           'clientip':'115.28.134.55',
                           'detecttype':'LocateRecognize',
                           'languagetype':'CHN_ENG',
                           'imagetype':'1',
                           'image': base64.b64encode(bImage).decode("utf-8")
                           }
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                            "apikey": "0830a440f9e1b9a31c5e807fa2f0ab61"
                          }
        url = 'http://apis.baidu.com/apistore/idlocr/ocr'
        rdd = yield from aiohttp.post(url,data=payload,headers=headers)
        return (yield from rdd.text())

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
            topic.append(content.get_text().strip())
        if isImg and len(topic) > 6:
            topicTitle = soup.title.string
            m = re.match(r'^http.+/(.+)', imgUrl)
            imgName = m.group(1)
            logging.info('=============%s==============' % soup.title.string)
            logging.info(url)
            yield from orm.create_pool(loop=loop,host=dbHost, user=dbUser, password=dbPassword, db=dbName)
            num = yield from WeaponChangeTopic.findNumber('id', 'topicId=?', topicId)
            if num is None:
                words = yield from getImgWords(imgUrl)
                try:
                    wordList = json.loads(words)['retData']
                    if len(wordList) > 0:
                        logging.info(wordList[0]["word"].strip())
                        weaponTitle = wordList[0]["word"]
                        weapon = WeaponChangeTopic(comefrom = "tieba",
                                                   topicId = topicId,
                                                   title = weaponTitle,
                                                   details = json.dumps(wordList),
                                                   topicTitle = topicTitle,
                                                   topicList = json.dumps(topic),
                                                   img = imgName
                                )
                        yield from weapon.save()
                except ValueError as e:
                    print("baidu ocr json error: %s" % words)


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

