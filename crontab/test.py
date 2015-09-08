#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import json
import aiohttp
import asyncio

str = '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDABMNDxEPDBMREBEWFRMXHTAfHRsbHTsqLSMwRj5KSUU+RENNV29eTVJpU0NEYYRiaXN3fX59S12Jkoh5kW96fXj/2wBDARUWFh0ZHTkfHzl4UERQeHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHj/wAARCAAfACEDAREAAhEBAxEB/8QAGAABAQEBAQAAAAAAAAAAAAAAAAQDBQb/xAAjEAACAgICAgEFAAAAAAAAAAABAgADBBESIRMxBSIyQXGB/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/APawEBAQEBAgy8i8ZTVV3UY6V1eU2XoWDDZB19S646Gz39w9fkKsW1r8Wm2yo1PYis1be0JG9H9QNYCAgc35Cl3yuVuJZl0cB41rZQa32dt2y6OuOiOxo61vsLcVblxaVyXD3hFFjL6La7I/sDWAgICAgICB/9k='

bstr = base64.b64decode(str)

#with open('test.jpg', 'wb') as f:
#  f.write(bstr)

with open('/Users/chocobobo/Work/d3/public/weapon/tieba/test.jpg', 'rb') as f:
    img = base64.b64encode(f.read()).decode("utf-8")


@asyncio.coroutine
def wget(img):
    payload = {'fromdevice':'pc',
                       'clientip':'115.28.134.55',
                       'detecttype':'LocateRecognize',
                       'languagetype':'CHN_ENG',
                       'imagetype':'1',
                       'image': img
                       }
    headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "apikey": "0830a440f9e1b9a31c5e807fa2f0ab61"
                      }
    url = 'http://apis.baidu.com/apistore/idlocr/ocr'
    rdd = yield from aiohttp.post(url,data=payload,headers=headers)
    return (yield from rdd.text())


loop = asyncio.get_event_loop()
html = loop.run_until_complete(wget(img))
print(json.loads(html))
loop.close()
