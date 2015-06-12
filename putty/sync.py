#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import json
import pymongo
import datetime
import pyjsonrpc

from bson import ObjectId
from pcnile.search import FullTextSearchClient

def get_html_from_test_client(oid):
	from django.test import Client
	
	response = Client().get("/force_detail/%s/" % oid)
	if response.status_code == 200:
		return response.content
	else:
		print response.status_code
		raise 

# 传入连接的等级，比如当前类中需要用到不同集合的时候，就传入数据库
# 当只需要在某一集合中处理的时候只传入集合,最小化域
class ServerDB(object):
	def __init__(self, db, html_dir=None, ip='localhost', port=3149):
		self.old = db.server # 上一版本的数据库，现在可基于豆瓣ID获得原始数据
		
		self.info = db.info
		self.resource = db.resource
		self.html_dir = html_dir
		self.fts = FullTextSearchClient(self.info)
		self.rpc = pyjsonrpc.HttpClient(url="http://%s:%s" % (ip, port))
	
	def server_insert_handler(self, m, resource, html):
		if '_id' not in m and '_id' not in resource and not html:
			return '_id must exist and html must have'
		
		try:
			self.info.save(m)
			self.resource.save(resource)
			self.fts.insert(m)
			
			with open(os.path.join(self.html_dir, str(m['_id'])), 'wb') as f:
				if isinstance(html, unicode):
					html = html.encode('utf-8')
				f.write(html)
		except Exception as e:
			self.info.remove({'_id':m['_id']})
			self.resource.remove({'_id':m['_id']})
			self.fts.delete(str(m['_id']))
			
			return 'Exception ' + str(e)
		
		return str(m['_id'])
	
	def local_insert_handler(self, m, resource):
		if self.old.find({'douban.id':m['douban']['id']}).count():
			old = self.old.find_one({'douban.id':m['douban']['id']})
			m['_id'] = old['_id']
			m['addtime'] = old['addtime']
			m['updatetime'] = old['addtime']
		
		try:
			resource['_id'] = m['_id'] = _id = self.info.save(m)
			self.fts.insert(m)
			self.resource.save(resource)
			
			html = get_html_from_test_client(str(_id))
			
			return m, resource, html
		except Exception as e:
			print 'Exception', e
			
			self.info.remove({'_id':_id})
			self.resource.remove({'_id':_id})
			self.fts.delete(str(_id))
			
			raise
	
	def insert(self, m, resource):
		m, resource, html = self.local_insert_handler(m, resource)
		
		try:
			result = self.rpc.call("insert", m, resource, html)
		except Exception as e:
			result = 'Exception ' + str(e)
		
		if result != str(m['_id']):
			self.info.remove({'_id':m['_id']})
			self.resource.remove({'_id':m['_id']})
			self.fts.delete(str(m['_id']))
		
		return result

	def server_modtify_handler(self, _id, search, info, resource, html):
		if not html:
			return '_id must exist and html must have'
		
		old_info = self.info.find_one({'_id':_id})
		old_resource = self.resource.find_one({'_id':_id})
		
		try:
			if len(search) or len(info):
				self.info.update({'_id':_id}, {"$set":dict(search.items() + info.items())})
			if len(search):
				self.fts.modtify(self.info.find_one({'_id':_id}))
		except Exception as e:
			self.info.save(old_info)
			self.fts.modtify(old_info)
			
			return 'Exception from modtify info' + str(e)
		
		try:
			self.resource.update({'_id':_id}, {"$set":resource})
		except Exception as e:
			self.info.save(old_info)
			self.fts.modtify(old_info)
			self.resource.save(old_resource)
			
			return 'Exception from modtify resource' + str(e)
		
		try:
			with open(os.path.join(self.html_dir, str(_id)), 'wb') as f:
				if isinstance(html, unicode):
					html = html.encode('utf-8')
				f.write(html)
		except Exception as e:
			self.info.save(old_info)
			self.fts.modtify(old_info)
			self.resource.save(old_resource)
			
			return 'Exception from modtify html' + str(e)
		
		return 'success'
	
	def local_modtify_handler(self, _id, search, info, resource):
		old_info = self.info.find_one({'_id':_id})
		old_resource = self.resource.find_one({'_id':_id})
		
		try:
			if len(search) or len(info):
				self.info.update({'_id':_id}, {"$set":dict(search.items() + info.items())})
			if len(search):
				self.fts.modtify(self.info.find_one({'_id':_id}))
		except Exception as e:
			self.info.save(old_info)
			self.fts.modtify(old_info)
			
			return 'Exception from modtify info' + str(e)
		
		try:
			self.resource.update({'_id':_id}, {"$set":resource})
		except Exception as e:
			self.info.save(old_info)
			self.fts.modtify(old_info)
			self.resource.save(old_resource)
			
			return 'Exception from modtify resource' + str(e)
		
		try:
			html = get_html_from_test_client(str(_id))
			with open(os.path.join(self.html_dir, str(_id)), 'wb') as f:
				if isinstance(html, unicode):
					html = html.encode('utf-8')
				f.write(html)
		except Exception as e:
			self.info.save(old_info)
			self.fts.modtify(old_info)
			self.resource.save(old_resource)
			
			return 'Exception from modtify html' + str(e)
		
		return old_info, old_resource, html
	
	def modtify(self, _id, search, info, resource):
		lr = self.local_modtify_handler(_id, search, info, resource)
		if isinstance(lr, tuple):
			old_info, old_resource, html = lr
			result = self.rpc.call("modtify", _id, search, info, resource, html)
			if result != 'success':
				print result
				
				self.info.save(old_info)
				self.fts.modtify(old_info)
				self.resource.save(old_resource)
			
			return result
		else:
			print lr
			return lr

class SyncServer(object):
	def __init__(self, db, html_dir, ip, port):
		self.ip = ip
		self.port = port
		self.sdb = ServerDB(db, html_dir, ip, port)
	
	def run(self):
		class RequestHandler(pyjsonrpc.HttpRequestHandler):
			methods = {'insert':self.sdb.server_insert_handler, 'modtify':self.sdb.server_modtify_handler}
		
		# Threading HTTP-Server
		http_server = pyjsonrpc.ThreadingHttpServer(
			server_address = (self.ip, self.port),
			RequestHandlerClass = RequestHandler
		)
		
		print "Starting Background server ..."
		print "URL: http://%s:%s" % (self.ip, self.port)
		
		try:
			http_server.serve_forever()
		except KeyboardInterrupt:
			http_server.shutdown()
		
		print "Stopping HTTP server ..."
