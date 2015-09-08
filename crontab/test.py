#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import json
import urllib.parse
import codecs
import base64
import urllib.request


@asyncio.coroutine
def getImgString(bImage):
    payload = {'fromdevice':'pc',
               'clientip':'115.28.134.55',
               'detecttype':'LocateRecognize',
               'languagetype':'CHN_ENG',
               'imagetype':'2',
               'image': bImage
               }
    headers = {"Content-Type": "application/x-www-form-urlencoded",
                "apikey": "0830a440f9e1b9a31c5e807fa2f0ab61"
              }
    r = yield from aiohttp.post('http://apis.baidu.com/apistore/idlocr/ocr', data=payload, headers=headers)
    return (yield from r.text())

large_image_url = 'http://imgsrc.baidu.com/forum/pic/item/160266d0f703918f33381593573d269758eec4a7.jpg'
large_image = {'image': urllib.request.urlopen(large_image_url)}
loop = asyncio.get_event_loop()
topicListHtml = loop.run_until_complete(getImgString(large_image))
print(json.loads(topicListHtml))
loop.close()

txtFile = codecs.open('/Users/chocobobo/Work/d3/public/weapon/tieba/down.jpg', 'r', 'utf-16')
for line in txtFile:
  print(repr(line))
