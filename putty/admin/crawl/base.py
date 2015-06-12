#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Collection(object):
	def __init__(self, collection):
		self.collection = collection
	
	def load(self, ):
		pass
	
	def delete(self, oid):
		pass
	
	def patch(self, ):
		pass
	
	def blacklist(self, ):
		pass
	
	def restore(self):
		pass
	
	"""
	设置保留的标志，标识这次不处理
	"""
	def reserved(self, oid):
		return False
	
	def count(self):
		pass
	
	def merge(self, ):
		pass

