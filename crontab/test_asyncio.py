'''
  抓取贴吧
'''
#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging; logging.basicConfig(level=logging.INFO)
from bs4 import BeautifulSoup
import aiohttp
import asyncio

def getTopicList(url):
  response = yield from aiohttp.request('GET', url)
  return (yield from response.read())

if __name__ == '__main__':
  topicUrl = 'http://tieba.baidu.com/f?ie=utf-8&kw=%E6%9A%97%E9%BB%913'
  loop = asyncio.get_event_loop()
  topicListHtml = loop.run_until_complete(getTopicList(topicUrl))
  soup = BeautifulSoup(topicListHtml)
  titleList = soup.find_all("a", class_="j_th_tit")
  logging.info(titleList)
