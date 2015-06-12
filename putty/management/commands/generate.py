#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from bson import ObjectId
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.core.management.base import BaseCommand, CommandError
import datetime
from obtainfo.templatetags.pic import pic as render_pic
import codecs
import pymongo
import os.path
import urllib2
import json

class Command(BaseCommand):
    help = 'generate article for blogs'
    
    def handle(self, num = 30, *args, **options):
        timestamp = datetime.datetime.now()
        db = pymongo.Connection().server
        folder = ['baidu_561424310', 'baidu_1172585668', 'sina_twenty_first', 'sina_xiaolingxianer', 'renren_561424310', '163_hduzhy', '163_twenty_first']
        # get already generate artiles
        try:
            with codecs.open(os.path.join(settings.BLOGS, 'oids.json'), 'rb', 'utf-8') as f:
                oids = [ObjectId(j) for j in json.load(f)]
        except:
            oids = []
        
        # find matched movie
        num = int(num)
        ms = db.server.find({'$and':[{'_id':{'$nin': oids}}, {'douban.ranking.score':{'$gt':5}}, {'douban.ranking.count':{'$gt':1000}}]}).sort([('douban.ranking.count', -1), ('douban.ranking.score', -1)]).limit(num)
        blog = get_template('blog.txt')
        
        articled = list()
        for m in ms:
            try:
                img = urllib2.urlopen(render_pic(m['bigpic'])).read()
            except:
                continue
            
            for f in folder:
                basedir = os.path.join(settings.BLOGS, f)
                    
                if not os.path.exists(basedir):
                    os.makedirs(basedir)
                    
                article = blog.render(Context({'m':m}))
                    
                writedir = os.path.join(basedir, str(m['_id']))
                if not os.path.exists(writedir):
                    os.makedirs(writedir)
                    
                with open( os.path.join(writedir, 'blog.jpg' ), 'wb') as f:
                    f.write(img)
                    
                with codecs.open( os.path.join(writedir, 'blog.txt' ), 'wb', 'utf-8') as f:
                    f.write(article)
            
            articled.append(m['_id'])
        
        oids += articled
        with codecs.open(os.path.join(settings.BLOGS, 'oids.json'), 'wb', 'utf-8') as f:
            json.dump([str(o) for o in oids], f)
        
        self.stdout.write('Successfully generate article use time %s \nalready generate articles %d' % (str((datetime.datetime.now() - timestamp)), len(oids)) )
