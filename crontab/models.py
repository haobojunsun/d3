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
    topicId = IntegerField()
    title =  StringField(ddl='varchar(10)')
    details = StringField(ddl='varchar(50)')
    topicTitle = StringField(ddl='varchar(50)')
    topicList = StringField(ddl='varchar(500)')
    img = StringField(ddl='varchar(50)')
    createTime = FloatField(default=time.time())



