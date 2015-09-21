'''
  抓取 www.diablo3.com.cn
  2015.9.21
  抓取装备图片
'''
#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import os

# 装备保存地址
itemDir = '/Users/chocobobo/Work/d3/public/items/'

# 抓取图片的Url
baseUrl = 'http://content.battlenet.com.cn/d3/icons-zh-cn/items/large/'


@asyncio.coroutine
def getItemImg(itemName):
    itemName = itemName + '.png'
    if os.path.exists(itemDir+itemName):
        return
    try:
        r = yield from aiohttp.get(baseUrl+itemName)
    except aiohttp.errors.ClientOSError as e:
        print('[error url:%s]  %s' % (url, e))
    else:
        bImage = yield from r.read()
        with open(itemDir+itemName, 'wb') as f:
           f.write(bImage)
