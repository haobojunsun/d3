'''
  抓取bbs.d.163.com
  2015.9.14
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
dirBase='/Users/chocobobo/Work/d3/public/weapon/163/'

@asyncio.coroutine
def wget(url,headers=None):
    try:
        if headers is None:
            headers = {}
        response = yield from aiohttp.get(url,headers=headers)
    except aiohttp.errors.ClientOSError as e:
        print('[error url:%s]  %s' % (url, e))
    else:
        return (yield from response.text())

def checkTitle(tag):
    return tag.name == "a" and tag.get("class") == ['xst'] and re.compile("洗").search(tag.string)

def checkTopic(tag):
    return tag.name == "div" and tag.get("class") == ['message']

def getImg(tag):
    return tag.name == "img"


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


# 抓取符合条件的帖子列表
def getTopicListUrl(url):
    topicListHtml = yield from wget(url)
    soup = BeautifulSoup(topicListHtml, 'html.parser')
    for title in soup.find_all(checkTitle):
        topicUrlList.append(title.get("href"))

# 抓取帖子内容
@asyncio.coroutine
def getTopic(loop,url):
    # 模拟手机header
    topicHtml = yield from wget(url,
            {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'}
            )
    if len(topicHtml) > 100:
        soup = BeautifulSoup(topicHtml, 'html.parser')
        topic = []
        isImg = False
        m = re.match(r'^http.+tid=(\d+)', url)
        topicId = m.group(1) if m is not None else 0
        # 帖子列表
        for content in soup.find_all(checkTopic):
            topic.append(content.get_text().strip())
        topicTitle = soup.find("h2").get_text().replace(' ','').strip()
        topicTitle = topicTitle.replace('只看楼主','')
        print('-------------------------------')
        print(topicTitle)
        print(url)
        # 获取图片页面链接
        imgA = soup.find("ul", class_="img_one")
        if imgA is not None:
            imgUrl = imgA.find("a").get("href")
            if imgUrl is not None:
                # 从图片页面获取图片真实地址
                imgHtml = yield from wget('http://bbs.d.163.com/'+imgUrl,
                                            {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'}
                                            )

                if len(imgHtml) > 100:
                    soup2 = BeautifulSoup(imgHtml, 'html.parser')
                    imgUrl = soup2.find("img", class_="postalbum_i").get("orig")
                    if imgUrl is not None:
                        isImg = True

        if isImg and len(topic) > 6:
            m = re.match(r'^http.+/(.+)', imgUrl)
            imgName = m.group(1)
            yield from orm.create_pool(loop=loop,host=dbHost, user=dbUser, password=dbPassword, db=dbName)
            num = yield from WeaponChangeTopic.findNumber('id', 'topicId=?', topicId)
            if num is None:
                words = yield from getImgWords(imgUrl)
                try:
                    wordList = json.loads(words)['retData']
                    if len(wordList) > 0:
                        logging.info(wordList[0]["word"].strip())
                        weaponTitle = wordList[0]["word"]
                        print(weaponTitle)
                        print(imgUrl)
                        weapon = WeaponChangeTopic(comefrom = "163",
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


if __name__ == '__main__':
    #抓取帖子列表
    topicUrlList= []
    # Barbarian
    url1 = 'http://bbs.d.163.com/forum-321-1.html'
    # Witch Doctor
    url2 = 'http://bbs.d.163.com/forum-320-1.html'
    # Demon Hunter
    url3 = 'http://bbs.d.163.com/forum-319-1.html'
    # Monk
    url4 = 'http://bbs.d.163.com/forum-318-1.html'
    # Wizard
    url5 = 'http://bbs.d.163.com/forum-317-1.html'
    # Crusader
    url6 = 'http://bbs.d.163.com/forum-350-1.html'
    urlList = [url1,url2,url3,url4,url5,url6]
    loop = asyncio.get_event_loop()
    tasks = [getTopicListUrl(url) for url in urlList]
    loop.run_until_complete(asyncio.wait(tasks))
    #抓取帖子内容
    if len(topicUrlList) > 0:
        tasks = [getTopic(loop,'http://bbs.d.163.com/'+url+'&mobile=2') for url in topicUrlList]
        loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


