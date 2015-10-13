#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
import sys, os, posixpath
from tempfile import TemporaryFile
from datetime import datetime
from urlparse import urlparse
from twisted.internet import defer, threads

from scrapy import log, signals
from scrapy.exceptions import NotConfigured
from scrapy.utils.misc import load_object
from scrapy.utils.python import get_func_args

db = pymongo.Connection().scrapy
sdb = pymongo.Connection().server


def df(url):
    if db.scrapy.find({'source': url}).count() == 0 and db.filter.find(
            {'source': url}).count() == 0 and sdb.server.find({'samesite': url}).count() == 0:
        return False
    else:
        return True


def manual_block(url):
    db.filter.insert({'source': url})


class FeedExporter(object):
    def __init__(self, settings):
        self.settings = settings
        self.itemcount = 0

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings)
        crawler.signals.connect(o.item_scraped, signals.item_scraped)
        return o

    def item_scraped(self, item, spider):
        if db.scrapy.find({'source': item['source']}).count() == 0:
            todb = {'source': [item['source']], 'title': item['title'], 'desc': item['desc'],
                    'resource': item['resource'], 'track': 'scrapy', 'level': self.settings['LEVEL']}
            db.scrapy.insert(todb)
            self.itemcount += 1

        return item
