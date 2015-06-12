#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
from bson import ObjectId
from obtainfo.models import MovieInfo
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import urllib2
import urlparse
import random

class Command(BaseCommand):
    def handle(self, *args, **options):
        db = pymongo.Connection().server
        download = list()
        for d in db.ranking.find():
            if d['pic']:
                download.append(d['pic'])
                fil = urlparse.urlparse(d['pic']).path.split('/')[-1]
                m = MovieInfo(id=d['oid'], title=d['title'], recommend=True, timestamp=datetime.now(), image="uploads/200_92/%s" % fil)
            else:
                m = MovieInfo(id=d['oid'], title=d['title'], recommend=True, timestamp=datetime.now())
            
            m.visitor = random.randint(1, 10)
            m.save()
    