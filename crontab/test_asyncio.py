'''
  抓取贴吧
'''
#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging; logging.basicConfig(level=logging.INFO)
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import re

@asyncio.coroutine
def wget(url):
    try:
        response = yield from aiohttp.request('GET', url)
    except aiohttp.errors.ClientOSError as e:
        print('[error url:%s]  %s' % (url, e))
        exit()
    else:
        return (yield from response.read())

@asyncio.coroutine
def getTopic(url):
    topicHtml = yield from wget(url)
    if len(topicHtml) > 100:
        soup = BeautifulSoup(topicHtml, 'html.parser')
        print('=============%s==============' % soup.title.string)
        print(url)
        topic = []
        isImg = False
        for content in soup.find_all(checkTopic):
            img = content.find(class_="BDE_Image")
            if img != None:
                isImg = True
            topic.append(content.get_text())
        if isImg:
            print(len(topic))

def checkTitle(tag):
    return tag.name == "a" and tag.get("class") == ['j_th_tit', ''] and re.compile("求助").search(tag.string)

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
        tasks = [getTopic('http://tieba.baidu.com'+url) for url in titleList]
        topicHtml = loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

