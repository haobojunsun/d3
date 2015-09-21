#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    Model类
'''
import time

from orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField

'''
    洗武器帖子列表
'''
class WeaponChangeTopic(Model):
    __table__ = 'weapon_change_topic'
    id = IntegerField(primary_key=True)
    comefrom = StringField(ddl='varchar(10)')
    topicId = StringField(ddl='varchar(50)')
    title =  StringField(ddl='varchar(10)')
    player = StringField(ddl='char(20)')
    details = StringField(ddl='text')
    topicTitle = StringField(ddl='varchar(50)')
    topicList = StringField(ddl='text')
    img = StringField(ddl='varchar(50)')
    createTime = FloatField(default=time.time())

'''
    天梯排名
'''
class HeroTop(Model):
    __table__ = 'hero_top'
    id = IntegerField(primary_key=True)
    body = StringField(ddl='text')
    createTime = FloatField(default=time.time())


'''
    装备列表
'''
class HeroItems(Model):
    __table__ = 'hero_items'
    id = IntegerField(primary_key=True)
    battleTag = StringField(ddl='varchar(50)')
    heroId = StringField(ddl='varchar(50)')
    itemData= StringField(ddl='text')
    createTime = FloatField(default=time.time())




