#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import string
import codecs
import urllib2
import urlparse
import datetime
from bson import ObjectId
from django.conf import settings
from putty.admin.proxy import Proxy
from multiprocessing.pool import ThreadPool
from django.core.management.base import BaseCommand, CommandError

db = settings.MONGODB
proxy = Proxy(settings.MONGOPOOL)

"""
db.server 集合添加type字段，{movie, tv}
从本地已经抓取的数据进行分析，没有的话从豆瓣抓取
"""
def get_json_data(file_name):
    with codecs.open(file_name, 'rb', 'utf-8') as f:
        js = json.load(f)
    
    info = dict()
    for j in js:
        info[j['id']] = j
    
    return info

def get_type_from_douban(did):
    atemplate = u"http://api.douban.com/v2/movie/subject/%s"
    try:
        m = json.loads(urllib2.urlopen(atemplate % did, timeout=30).read())
        return m['subtype']
    except:
        return ''

def get_dl_from_douban(did):
	atemplate = u"http://api.douban.com/v2/movie/subject/%s"
	try:
		return json.loads(urllib2.urlopen(atemplate % did, timeout=30).read())
	except Exception as e:
		print e, did
		return None

def get_items(pool, callback, urls):
	pool = ThreadPool(pool)
	items = pool.map(callback, urls)
	pool.close()
	pool.join()
	return items

def add_douban_list(db):    
	with codecs.open('douban.json', 'rb', 'utf-8') as f:
		js = json.load(f)
	
	dl = list()
	did = set([j['id'] for j in js])
	for m in db.server.find():
		if m['douban']['id'] and m['douban']['id'] not in did:
			dl.append(m['douban']['id'])
	
	dl = get_items(10, get_dl_from_douban, dl)
	dl = [d for d in dl if d]
	
	if len(dl):
		print 'add', len(dl)
		js += dl
		with codecs.open('out.json', 'wb', 'utf-8') as f:
			json.dump(js, f)

def add_type(db):    
	js = get_json_data('douban.json')
	
	exist = 0
	found = 0
	error = 0
	tv = 0
	for m in db.server.find():
		if m['douban']['id']:
			try:
				m['type'] = js[m['douban']['id']]['subtype']
				exist += 1
				
				if m['type'] == 'tv':
					tv += 1
			except:
				m['type'] = 'movie'
				error += 1
		else:
			m['type'] = 'movie'
			found += 1
		
		#if 'type' in m:
		db.server.save(m)
	
	print exist, found, error, tv

"""
from db.server to db.info and db.resource
"""
def server_to_ir(db):
	for d in db.server.find({'type':'movie'}):
		d['resource']['complete'] = d['resource']['download']
		d['resource'], resource = proxy._pre_save_resource('movie', str(d['_id']), d['resource'])
		d['updatetime'] = d['addtime']
		db.info.save(d)
		resource['_id'] = d['_id']
		db.resource.save(resource)
	
	db.server.remove({'type':'movie'})
	
	db.info.ensure_index('title')
	db.info.ensure_index('aka')
	db.info.ensure_index('director')
	db.info.ensure_index('writer')
	db.info.ensure_index('actor')
	db.info.ensure_index('genre')
	db.info.ensure_index('area')
	db.info.ensure_index('language')
	db.info.ensure_index('imdb')
	db.info.ensure_index('douban.id')
	db.info.ensure_index('douban.ranking.score')
	db.info.ensure_index('douban.ranking.count')
	db.info.ensure_index('year')
	db.info.ensure_index('type')
	db.info.ensure_index('addtime')
	db.info.ensure_index('updatetime')
	db.info.ensure_index('random')
	db.info.ensure_index('resource.level')
	db.info.ensure_index('resource.online')
	db.info.ensure_index('resource.netdisk')
	db.info.ensure_index('resource.complete')
	db.info.ensure_index('resource.cam')
	db.info.ensure_index('resource.dvd')
	db.info.ensure_index('resource.hd')
	db.info.ensure_index('resource.stereo')
	
	db.resource.ensure_index('stereo.uid')
	db.resource.ensure_index('hd.uid')
	db.resource.ensure_index('dvd.uid')
	db.resource.ensure_index('cam.uid')

def add_recommend(db):
	for d in db.info.find():
		if 'recommend' not in d:
			d['recommend'] = proxy._get_recommend(d)
			db.info.save(d)

class Command(BaseCommand):
	help = 'db.server to db.info and db.resource'
	
	def handle(self, *args, **options):
		add_recommend(db)
