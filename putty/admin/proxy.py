#!/usr/bin/env python
# -*- coding: utf-8 -*-

# project include
from .spider import DoubanSpider, clean_showtime
from .hao123_tv import get_resource

from putty.sync import ServerDB
from obtainfo.templatetags.obtainfo_tags import pic_tag as render_pic
from django.conf import settings

from pcnile import sqlitedict as bsddb
from pcnile.http import json, JsonResponse
from pcnile.helper import md5sum, group_list
from pcnile.qiniu_file import upload_img_full
from pcnile.search import FullTextSearchClient
from pcnile.resource import atom_download_resource, format_netdisk_resource, format_online_resource,\
	qualities_0, qualities_1, qualities_2, qualities_3, qualities_4, qualities_5

# third lib include
from shortuuid import uuid as uid
from bson.objectid import ObjectId
import dateutil.parser as dateparser

# system lib include
import re
import time
import base64
import codecs
import random
import os.path
import datetime
import urllib2, urllib, urlparse

quality_CAM = qualities_0 + qualities_1 + qualities_2
quality_DVD = qualities_3
quality_HD = qualities_4
quality_3D = qualities_5

verify_oid = lambda oid : True if re.match(r'^[0-9a-fA-F]{24}$', oid) else False

def atom_forever(r):
	DBDIR = settings.DBDIR
	
	UrlFilter = bsddb.open(os.path.join(DBDIR, 'url.db'), autocommit=True)
	BtFilter = bsddb.open(os.path.join(DBDIR, 'bt.db'), autocommit=True)
	Ed2kFilter = bsddb.open(os.path.join(DBDIR, 'ed2k.db'), autocommit=True)
	NetdiskFilter = bsddb.open(os.path.join(DBDIR, 'netdisk.db'), autocommit=True)
	OnlineFilter = bsddb.open(os.path.join(DBDIR, 'online.db'), autocommit=True)
	
	record_netdisk, record_ed2k, record_bt = dict(), dict(), dict()
	
	for n in r['netdisk']:
		NetdiskFilter[n['link']] = int(time.time()*1000)
	
	if 'complete' not in r:
		complete = r['stereo'] + r['hd'] + r['dvd'] + r['cam']
	else:
		complete = r['complete']
	
	for c in complete:
		if c['link'].startswith('ed2k'):
			Ed2kFilter[c['link'].split('|')[4].lower()] = int(time.time()*1000)
		elif c['link'].startswith('magnet'):
			urn = re.findall(ur'xt=urn:btih:(\w+)', c['link'])[0].lower()
			BtFilter[urn] = int(time.time()*1000)
			
	UrlFilter.close()
	BtFilter.close()
	Ed2kFilter.close()
	NetdiskFilter.close()
	OnlineFilter.close()

def brief(m):
	ret = m['douban']['id'] + ' / '
	ret +=  " / ".join( m['aka'] + m['director'] + m['actor'] + m['area'] ) + " / %s" % m['showtime']
	
	try:
		ret += u'\n资源等级：' + m['resource']['level']
	except KeyError:
		pass
	
	return ret

class Proxy(object):
	def __init__(self, connection_pool):
		self.db = connection_pool.server
		self.info = self.db.info # movie and tv infomation save
		self.resource = self.db.resource # movie and tv resource save, only use info collection id to check it
		self.sync = ServerDB(self.db, html_dir="D:\\obtainfo\\Store\\html", ip='106.186.122.161') # sync local and server storage
	
	"""
	从Mongodb存储的数据格式到前端处理格式的转换
	"""
	def _toEditMode(self, m, allow='T'):
		toString = lambda x : " / ".join(x)
		
		ranking = str(m['douban']['ranking']['count']) + ' / ' + str(m['douban']['ranking']['score']) + ' / ' + allow
		
		image = list()
		
		if m['stdpic'].startswith('/media/'):
			image.append({'url':m['stdpic'], 'name':m['stdpic'].split('/')[-1], 'DH':'', 'DS':'DS', 'width':130, 'height':170})
		else:
			image.append({'url':render_pic(m['stdpic']), 'name':m['stdpic'], 'DH':'', 'DS':'DS', 'width':130, 'height':170})
		
		if m['bigpic'].startswith('/media/'):
			image.append({'url':m['bigpic'], 'name':m['bigpic'].split('/')[-1], 'DH':'DH', 'DS':'', 'width':220, 'height':300})
		else:
			image.append({'url':render_pic(m['bigpic']), 'name':m['bigpic'], 'DH':'DH', 'DS':'', 'width':220, 'height':300})
		
		# build all string field to dict
		if m['type'] == 'movie':
			info = {
				'_id':str(m['_id']), 'type':m['type'],
				'title':m['title'], 'aka':toString(m['aka']),
				'director':toString(m['director']), 'writer':toString(m['writer']), 'actor':toString(m['actor']),
				'area':toString(m['area']), 'language':toString(m['language']),
				'douban':m['douban']['id'], 'ranking':ranking, 'imdb':m['imdb'],
				'genre':toString(m['genre']), 'plot':m['plot'],
				'showtime':clean_showtime(m['showtime']), 'year':m['year'],
				'runtime':m['runtime'],
				'image':image,
				'samesite':"\n".join(m['samesite']),
			}
		else:
			info = {
				'_id':str(m['_id']), 'type':m['type'],
				'title':m['title'], 'aka':toString(m['aka']),
				'director':toString(m['director']), 'writer':toString(m['writer']), 'actor':toString(m['actor']),
				'area':toString(m['area']), 'language':toString(m['language']),
				'douban':m['douban']['id'], 'ranking':ranking, 'imdb':m['imdb'],
				'genre':toString(m['genre']), 'plot':m['plot'],
				'showtime':clean_showtime(m['showtime']), 'year':m['year'],
				'season':m['season'], 'episode':m['episode'], 'runtime':m['runtime'],
				'image':image
			}
			
			try:
				if m['finish']:
					info['finish'] = True
				else:
					info['finish'] = False
			except KeyError:
				info['finish'] = False
		
		return info

	def _fromEditMode(self, info):
		# help lambda function
		get_str_field = lambda x : x.strip()
		get_int_field = lambda x : int(x)
		get_array_field = lambda x : [get_str_field(i) for i in x.split('/') if i.strip()]
		
		item = dict()
		
		try:
			item['_id'] = ObjectId(get_str_field(info['_id']))
		except:
			item['_id'] = ''
		sub_type = item['type'] = get_str_field(info['type']) # subject type{movie, tv}
		if sub_type not in ['movie', 'tv']:
			raise ValueError(sub_type)
		
		item['title'] = get_str_field(info['title'])
		item['aka'] = get_array_field(info['aka'])
		
		item['director'] = get_array_field(info['director'])
		item['writer'] = get_array_field(info['writer'])
		item['actor'] = get_array_field(info['actor'])
		
		item['imdb'] = get_str_field(info['imdb'])
		
		try:
			count, score, allow = get_array_field(info['ranking'])
		except:
			try:
				count, score = get_array_field(info['ranking'])
			except:
				count, score = 0, 0
			finally:
				allow = 'T'
		
		if allow not in ['T', 'F']:
			allow = 'T'
		
		item['douban'] = {'id':get_str_field(info['douban']), 'ranking':{'score':score, 'count':count}}
		
		item['genre'] = get_array_field(info['genre'])
		item['area'] = get_array_field(info['area'])
		item['language'] = get_array_field(info['language'])
		
		item['year'] = get_str_field(info['year'])
		item['showtime'] = get_str_field(info['showtime'])
		if item['year'] == '':
			item['year'] = dateparser.parse(item['showtime']).year
		
		if sub_type == 'tv':
			item['finish'] = info['finish']
			item['season'] = get_str_field(info['season'])
			item['episode'] = get_str_field(info['episode'])
		item['runtime'] = get_str_field(info['runtime'])
		
		item['plot'] = get_str_field(info['plot'])
		
		if sub_type == 'movie':
			item['samesite'] = list(set([url.strip() for url in info['samesite'].split()]))
		
		# 自动处理域
		if info['ontop']:
			item['updatetime'] = datetime.datetime.now()
		
		"""
		refill image structure
		"""
		image = info['image']
		if isinstance(image, dict):
			stdpic, std_name = image['DS']['url'], image['DS']['name']
			bigpic, big_name = image['DH']['url'], image['DH']['name']
		else:
			stdpic = "http://img03.taobaocdn.com/imgextra/i3/495498642/T21.RuX5XXXXXXXXXX_!!495498642.jpg"
			std_name = "notpic_s.jpg"
			bigpic = "http://img02.taobaocdn.com/imgextra/i2/495498642/T2A7VqX0laXXXXXXXX_!!495498642.jpg"
			big_name = "notpic_b.jpg"
			
		return sub_type, allow, item, {'stdpic':{'url':stdpic, 'name':std_name}, 'bigpic':{'url':bigpic, 'name':big_name}}

	def fill_new_add(self, mid, direct):
		if re.match("^\d+$", mid): # douban id, scrapy from douban
			if not direct:
				try:
					m = self.info.find_one({'douban.id':mid})
					return {'status':'redirect', 'data':m['title']}
				except:
					pass
			
			douban_spider = DoubanSpider(mid)
			m = douban_spider.fake_info_doc()
		else: # mongodb id
			m = self.info.find_one({'_id':ObjectId(mid)})
		
		if m['_id']:
			r = self.resource.find_one({'_id':m['_id']})
			if m['type'] == 'movie':
				resource = {'online':r['online'], 'netdisk':r['netdisk'], 'complete':r['stereo'] + r['hd'] + r['dvd'] + r['cam'], 'episode':[]}
			else:
				resource = {'online':r['online'], 'netdisk':r['netdisk'], 'complete':r['complete'], 'episode':r['episode']}
		else:
			resource = {'online':[], 'netdisk':[], 'complete':[], 'episode':[]}
		
		if 'permission' not in resource:
			allow = 'T'
		else:
			allow = resource['permission']
		
		return {'status':'success', 'data':{'info':self._toEditMode(m, allow), 'resource':resource}}

	def _get_recommend(self, m):
		def make_video_actor(m):
			act = m['actor']
			length = len(act)
			
			if length:
				if length == 1:
					actor = act[0]
				else:
					for i in range(length - 1):
						if len(act[i]) + len(act[i+1]) < 10:
							actor = "%s %s" % (act[i], act[i+1])
							break
					else:
						actor = act[0]
			else:
				actor = u""
			
			return {"info":actor, "title":m['title'], "id":str(m['_id']), "img":m['stdpic']}
		
		"""
		get this movie guess list
		"""
		rand = random.random()
		
		query_name = {"$or":[{"director":{"$in":m['director']}}, {"writer":{"$in":m['writer']}}, {'actor':{'$in':m['actor']}}] }
		query_genre = {'genre':{'$in':m['genre']}}
		query_area = {'area':{'$in':m['area']}}
		
		try:
			filter_id = {'_id':{'$ne':m['_id']}}
		except KeyError:
			filter_id = {}
		
		guess = self.info.find({'$and':[filter_id, {"$and":[ query_name, query_genre ]} ]}).sort('year', -1).limit(10)
		if guess.count() < 10:
			guess = self.info.find( {'$and':[filter_id, {"$or":[ query_name, {"$and":[query_genre, query_area, {'random':{'$gt':rand}}]} ]} ]} ).sort('year', -1).limit(10)
			if guess.count() < 10:
				guess = self.info.find( {'$and':[filter_id, {"$or":[ query_name, {"$and":[query_genre, query_area, {'random':{'$lt':rand}}]} ]} ]} ).sort('year', -1).limit(10)
				if guess.count() < 10:
					guess = self.info.find( {'$and':[filter_id, {"$or":[ query_name, {"$and":[query_genre, query_area ]} ]} ]} ).sort('year', -1).limit(10)
					if guess.count() < 10:
						guess = self.info.find( {'$and':[filter_id, {"$or":[ query_name, query_genre ]} ]} ).sort('year', -1).limit(10)
						if guess.count() < 10:
							guess = self.info.find( {'$and':[filter_id, {"$or":[ query_name, query_area ]} ]} ).sort('year', -1).limit(10)
							if guess.count() < 10:
								guess = self.info.find(filter_id).sort('year', -1).limit(10)
		
		return group_list([make_video_actor(g) for g in list(guess)], 5)
	
	"""
	对所有类型的资源进行格式化
	"""
	def _pre_save_resource(self, sub_type, oid, resource):
		def max_resource_level(resource):
			level = 0
			for d in resource:
				temp_level = 0
				
				if d['quality'] in quality_CAM:
					temp_level = 1
				elif d['quality'] in quality_DVD:
					temp_level = 2
				elif d['quality'] in quality_HD or d['quality'] in quality_3D:
					return 3
				
				if temp_level > level:
					level = temp_level
			
			return level
		
		def format_show_resource(oid, complete):
			hd, dvd, cam, stereo = list(), list(), list(), list()
			
			if not oid:
				oid = str(ObjectId())
			
			for d in complete:
				if 'uid' not in d:
					d['uid'] = uid(oid + d['link'].encode('utf-8'))
				
				if d['quality'] in quality_CAM:
					cam.append(d)
				elif d['quality'] in quality_DVD:
					dvd.append(d)
				elif d['quality'] in quality_HD:
					hd.append(d)
				elif d['quality'] in quality_3D:
					stereo.append(d)
			
			return stereo, hd, dvd, cam
		
		complete = atom_download_resource(resource['complete'])
		stereo, hd, dvd, cam = format_show_resource(oid, complete)
		level = [u'', u'尝鲜', u'普清', u'高清'][max_resource_level(complete)]
		
		try:
			netdisk = format_netdisk_resource(resource['netdisk'])
		except KeyError:
			netdisk = []
		
		if sub_type == 'movie':
			online = format_online_resource( [o['link'] for o in resource['online']] )
			online_sum = len(online)
		else:
			online = resource['online']
			online_sum = sum([len(r['resource']) for r in resource['online']])
			
			# episode = format_episode_resource()
		
		if sub_type == 'movie':
			brief = {'online':online_sum, 'netdisk':len(netdisk), 'stereo':len(stereo), 'hd':len(hd), 'dvd':len(dvd), 'cam':len(cam), 'level':level}
			real = {'online':online, 'netdisk':netdisk, 'stereo':stereo, 'hd':hd, 'dvd':dvd, 'cam':cam,}
		else:
			brief = {'online':online_sum, 'netdisk':len(netdisk), 'complete':len(complete), 'episode':0, 'level':level}
			real = {'online':online, 'netdisk':netdisk, 'complete':complete, 'episode':[]}
		
		return brief, real

	def save_or_modtify(self, data):
		sub_type, allow, new, image = self._fromEditMode(data['info'])
		
		if new['_id'] == '': # save new one
			del new['_id']
			
			if upload_img_full(image['stdpic']['name']):
				new['stdpic'] = image['stdpic']['name']
			else:
				raise ValueError('upload image stdpic file fail')
			
			if upload_img_full(image['bigpic']['name']):
				new['bigpic'] = image['bigpic']['name']
			else:
				raise ValueError('upload image bigpic file fail')
			
			new['comment'] = []
			new['random'] = random.random()
			new['addtime'] = datetime.datetime.now()
			new['updatetime'] = datetime.datetime.now()
			new['recommend'] = self._get_recommend(new)
			new['resource'], resource = self._pre_save_resource(sub_type, '', data['resource'])
			
			# make sure all resource unique for wolf system
			atom_forever(resource)
			resource['permission'] = allow
			if verify_oid(self.sync.insert(new, resource)):
				return True
			
		else: # modtify exist item
			def diff(old, new, fields):
				different = dict()
				
				for f in fields:
					try:
						if new[f] != old[f]:
							old[f] = different[f] = new[f]
					except KeyError:
						old[f] = different[f] = new[f]
				
				return different
			
			old = self.info.find_one({'_id':new['_id']})
			if 'updatetime' not in new:
				new['updatetime'] = old['updatetime']
			
			if sub_type == 'movie':
				info_diff_field = ['genre', 'plot', 'imdb', 'douban',
					'area', 'language', 'showtime', 'year', 'runtime', 'updatetime', 'samesite']
			else:
				info_diff_field = ['genre', 'plot', 'imdb', 'douban',
					'area', 'language', 'showtime', 'year', 'season', 'episode', 'runtime', 'finish', 'updatetime']
			
			search_field = diff(old, new, ['title', 'aka', 'director', 'writer', 'actor'])
			info_field = diff(old, new, info_diff_field)
			
			# check image field
			if old['stdpic'] != image['stdpic']['name']:
				if upload_img_full(image['stdpic']['name']):
					old['stdpic'] = info_field['stdpic'] = image['stdpic']['name']
				else:
					raise ValueError('upload image stdpic file fail')
			
			if old['bigpic'] != image['bigpic']['name']:
				if upload_img_full(image['bigpic']['name']):
					old['bigpic'] = info_field['bigpic'] = image['bigpic']['name']
				else:
					raise ValueError('upload image bigpic file fail')
			
			info_field['type'] = sub_type
			info_field['resource'], real_resource = self._pre_save_resource(sub_type, str(old['_id']), data['resource'])
			info_field['recommend'] = self._get_recommend(old)
			
			# make sure all resource unique for wolf system
			atom_forever(real_resource)
			real_resource['permission'] = allow
			
			if self.sync.modtify(new['_id'], search_field, info_field, real_resource) == 'success':
				return True
			else:
				print 'modtify fail'
		
		return False
	
	"""
	判断当前给定的Mongodb ID是否存在
	"""
	def exist(self, oid, pure=True):
		if pure:
			if verify_oid(oid) and self.info.find({'_id':ObjectId(oid)}).count():
				return True
		else:
			try:
				return self.info.find_one({'_id':ObjectId(oid)})
			except:
				pass
		
		return False
	
	"""
	在数据库中查询条目是否存在，通过豆瓣的ID进行查询
	"""
	def query_by_douban_id(self, did):
		return  [
			{'title':m['title'], 'detail':brief(m), 'image':render_pic(m['stdpic']),'id':str(m['_id'])}
			for m in self.info.find({'douban.id':did})
		]
	
	"""
	在数据库中查询条目是否存在，通过名字进行查询
	"""
	def query_by_title(self, title):
		return  [
			{'title':m['title'], 'detail':brief(m), 'image':render_pic(m['stdpic']), 'id':str(m['_id'])}
			for m in self.info.find({'$or':[{'title':title}, {'aka':title} ]})
		]

