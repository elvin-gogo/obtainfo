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
from base import Collection

class MovieQuick(Collection):
	"""
	quick data structure: {_id, title, source, desc, complete resource, patch}
	"""
	def load(self):
		try:
			m = self.collection.find_one({'resource.commit':False})
			m['resource'] = {'online':[], 'netdisk':[], 'episode':[],
				'complete':[resource for resource in m['resource'] if resource['commit'] == False]
			}
			m['patch'] = False
			return m
		except:
			return None
	
	"""
	添加当前项进黑名单
	"""
	def blacklist(self, oid):
		if verify_oid(oid):
			self.db.fast.update({'_id':ObjectId(oid)}, {"$set":{'resource':[], 'desc':''}})
			return True
		else:
			return False

	def delete(self, oid):
		return self.blacklist(oid)
	
	def count(self, ):
		return {'name':'first page scrapy', 'num':self.collection.find({'resource.commit':False}).count()}
	
	def merge(self, ):
		pass
