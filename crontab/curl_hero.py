'''
  抓取 www.diablo3.com.cn
  2015.9.16
  1、抓取每个职业的赛季排名列表
  2、抓取每个用户角色的资料
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
from models import HeroItems
import orm
import json
import base64
import urllib.request
import time
import curl_items

# 数据库配置
dbHost='115.28.134.55'
dbUser='root'
dbPassword='5211314'
dbName='d3'

# 网站域名
webUrl = 'www.diablo3.com.cn'

# 文件位置
dirBase='/Users/chocobobo/Work/d3/public/weapon/163/'
#dirBase='/data/htdocs/d3/public/weapon/163/'

def rep(str):
    if str is not None:
        str = str.replace(' ','')
        str = str.replace('\r\n','')
        str = str.replace('\t','')
    else:
        str = ''
    return str

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

# 抓取英雄列表
@asyncio.coroutine
def getHeroList(url):
    heroListHtml = yield from wget(url)
    soup = BeautifulSoup(heroListHtml, 'html.parser')
    heroList = []
    id = 0
    for tr in soup.find_all('tr'):
        if id == 10:
            break
        battleName = tr.find(class_="battleName")
        battleTag = tr.find(class_="battletag")
        faceImg = tr.find("img", class_="class-portrait")
        level = tr.find("td", class_="cell-RiftLevel")
        over = tr.find("td", class_="cell-RiftTime")
        if battleName is not None and battleTag is not None and faceImg is not None:
            battleTag = battleTag.find("a").get("href")
            battleName = battleName.string
            battleTag = battleTag.replace('\r\n','')
            faceImg = faceImg.get("src")
            m = re.match(r'^http.+/(.+)', faceImg)
            faceImg = m.group(1)
            level = level.string.replace(' ','')
            level = level.replace('\r\n','')
            over = over.string.replace('\r\n','')
            over = over.replace(' ','')
            heroList.append((battleName,battleTag,faceImg,level,over))
            heroUrlList.append(battleTag)
            #logging.info("%s(%s)\r\nFace:%s\r\nLevel:%s\r\nOverTime:%s" % (battleName, battleTag, faceImg, level, over))
            id = id + 1
        else:
            continue
    if "barbarian" in url:
        topDic['barbarian'] = heroList
    if "wd" in url:
        topDic['wd'] = heroList
    if 'dh' in url:
        topDic['dh'] = heroList
    if 'monk' in url:
        topDic['monk'] = heroList
    if 'wizard' in url:
        topDic['wizard'] = heroList
    if 'crusader' in url:
        topDic['crusader'] = heroList

@asyncio.coroutine
def saveTop():
    yield from orm.create_pool(loop=loop,host=dbHost, user=dbUser, password=dbPassword, db=dbName)
    heroTop = HeroTop(id=1, body=json.dumps(topDic),createTime=time.time())
    yield from heroTop.update()

def getToolTip(ob):
    if ob is not None:
        link = ob.find("a", class_="slot-link")
        if link is not None:
            return link.get("data-d3tooltip")
        else:
            return ""
    else:
        return ""

# 抓取装备详情
@asyncio.coroutine
def getItem(battleTag,heroId,itemList):
    # 先删除，再保存入库
    yield from orm.create_pool(loop=loop,host=dbHost, user=dbUser, password=dbPassword, db=dbName)
    heroItems = HeroItems(battleTag=battleTag,heroId=heroId)
    yield from heroItems.delete()
    for item in itemList:
        m = re.match(r'.+item/(.+)', item)
        if m is not None:
            data = m.group(1)
            itemData = yield from wget('http://www.battlenet.com.cn/api/d3/data/item/'+data)
            if len(itemData) > 100:
                heroItems = HeroItems(battleTag= battleTag,
                                  heroId = heroId,
                                  itemData = itemData
                                  )
                yield from heroItems.save()
                jsonData = json.loads(itemData)
                if 'set' in jsonData:
                    icon = jsonData['set']['items'][0]['icon']
                else:
                    icon = jsonData['icon']
                # 保存装备
                yield from curl_items.getItemImg(icon)
        else:
            return

@asyncio.coroutine
def getHero(url):
    m = re.match(r'^/profile/(.+)/(.+)', url)
    heroName = m.group(1)
    heroId = m.group(2)
    url = 'http://www.diablo3.com.cn/action/profile/career/' + heroName + '/hero/' + heroId
    heroHtml = yield from wget(url)
    soup = BeautifulSoup(heroHtml, 'html.parser')
    # 巅峰等级
    level = soup.find('span', class_="paragon-level").string
    # 头
    head = getToolTip(soup.find("li", class_="slot-head"))
    # 身体
    torso = getToolTip(soup.find("li", class_="slot-torso"))
    # 脚
    feet = getToolTip(soup.find("li", class_="slot-feet"))
    # 手
    hands = getToolTip(soup.find("li", class_="slot-hands"))
    # 肩膀
    shoulders = getToolTip(soup.find("li", class_="slot-shoulders"))
    # 腿
    legs = getToolTip(soup.find("li", class_="slot-legs"))
    # 护腕
    bracers = getToolTip(soup.find("li", class_="slot-bracers"))
    # 主手
    mainHand = getToolTip(soup.find("li", class_="slot-mainHand"))
    # 副手
    offHand = getToolTip(soup.find("li", class_="slot-offHand"))
    # 腰带
    waist = getToolTip(soup.find("li", class_="slot-waist"))
    # 右手戒指
    rightFinger= getToolTip(soup.find("li", class_="slot-rightFinger"))
    # 左手戒指
    leftFinger= getToolTip(soup.find("li", class_="slot-leftFinger"))
    # 项链
    neck = getToolTip(soup.find("li", class_="slot-neck"))
    # 装备数据列表
    itemDataList = (head,torso,feet,hands,shoulders,legs,bracers,mainHand,offHand,waist,rightFinger,leftFinger,neck)
    yield from getItem(heroName,heroId,itemDataList)

    # 获取技能
    mainSkill = []
    passiveSkill = []
    skillDic= {}
    skills = soup.find_all("span", class_="skill-name")
    for skill in skills:
        skillName = rep(skill.contents[0])
        runeName = skill.find('span',class_='rune-name')
        if runeName is not None:
            # 主要技能
            mainSkill.append((skillName,rep(runeName.string)))
        else:
            # 被动技能
            passiveSkill.append(skillName)
    skillDic["main"] = mainSkill
    skillDic["passive"] = passiveSkill
    # 获取卡奈魔盒
    kanaiList = []
    kanaiDic = {}
    kanai = soup.find_all('a', class_='legendary-power-item')
    for ka in kanai:
        kanaiList.append(ka.get('data-d3tooltip'))
    kanaiDic['kanai'] = kanaiList
    # 获取属性
    attributesDic= {}
    attributesUL = soup.find('ul', class_='attributes-core secondary')
    attributesLI = attributesUL.find_all('li')
    for li in attributesLI:
        if li.get('data-tooltip') == '#tooltip-dps-hero':
            attributesDic["dps"] = li.find('span', class_='value').string
        elif li.get('data-tooltip') == '#tooltip-toughness-hero':
            attributesDic["toughness"] = li.find('span', class_='value').string
        elif li.get('data-tooltip') == '#tooltip-healing-hero':
            attributesDic["healing"] = li.find('span', class_='value').string


if __name__ == '__main__':
    # 抓取各职业的赛季排名
    topDic = {}
    # 角色tag url列表
    heroUrlList = []

    # Barbarian
    url1 = 'http://www.diablo3.com.cn/action/ranking/leaderboard?season=season&phase=4&classes=barbarian&type=normal&p=1'
    # Witch Doctor
    url2 = 'http://www.diablo3.com.cn/action/ranking/leaderboard?season=season&phase=4&classes=wd&type=normal&p=1'
    # Demon Hunter
    url3 = 'http://www.diablo3.com.cn/action/ranking/leaderboard?season=season&phase=4&classes=dh&type=normal&p=1'
    # Monk
    url4 = 'http://www.diablo3.com.cn/action/ranking/leaderboard?season=season&phase=4&classes=monk&type=normal&p=1'
    # Wizard
    url5 = 'http://www.diablo3.com.cn/action/ranking/leaderboard?season=season&phase=4&classes=wizard&type=normal&p=1'
    # Crusader
    url6 = 'http://www.diablo3.com.cn/action/ranking/leaderboard?season=season&phase=4&classes=crusader&type=normal&p=1'
    urlList = [url1,url2,url3,url4,url5,url6]
    loop = asyncio.get_event_loop()
    tasks = [getHeroList(url) for url in urlList]
    loop.run_until_complete(asyncio.wait(tasks))
    # 保存天梯排名，抓取角色数据
    if len(topDic) > 0:
        loop.run_until_complete(saveTop())
        tasks = [getHero(url) for url in heroUrlList]
        loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


