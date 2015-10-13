#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python lib
import re
import random
import base64
import codecs
import logging
import hashlib
import datetime
import StringIO
import urllib2, urllib, urlparse

from pcnile.qiniu_file import Picture
from pcnile.resource import online_table
from pcnile.http import json, JsonResponse
from pcnile.helper import md5sum, group_list

# third lib include
from shortuuid import uuid as uid
from bson.objectid import ObjectId
import dateutil.parser as dateparser

from base import Collection


class Hao123TV(Collection):
    """
    patch 这个变量名字不能使用
    """

    def __init__(self, connection):
        self.db = connection.hao123

    def load(self, ):
        try:
            m = self.db.tv.find_one()
            m['source'] = "http://v.hao123.com/dianshi/%s.htm" % m['id']
            m['desc'] = m['intro']
            m['resource'] = {'online': [], 'complete': [], 'episode': [], 'netdisk': []}
            m['patch'] = True
            return m
        except:
            return None

    def delete(self, oid):
        if verify_oid(oid):
            self.db.tv.remove({'_id': ObjectId(oid)})
            return True
        else:
            return False

    def patch(self, oid):
        try:
            m = self.db.tv.find_one({'_id': ObjectId(oid)})
            return {'online': get_resource(m['id']), 'complete': [], 'episode': [], 'netdisk': []} # hao123 id
        except Exception as e:
            print e
            return None

    """
    添加当前项进黑名单
    """

    def blacklist(self, oid):
        pass

    """
    设置保留的标志，标识这次不处理
    """

    def reserved(self, oid):
        pass

    """
    清除保留的标志
    """

    def restore(self):
        pass

    def merge(self, ):
        pass

    def count(self, ):
        pass
