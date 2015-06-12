#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from obtainfo.search import delete_item
from django.core.management.base import BaseCommand, CommandError
import datetime
import pymongo
from bson import ObjectId

class Command(BaseCommand):
	help = 'remove by oid.'
	
	def handle(self, oid, *args, **options):
		db = pymongo.Connection().server
		i = oid
		
		db.server.remove({'_id':ObjectId(i)})
		
		db.big_poster.remove({'oid':i})
		db.ranking.remove({'oid':i})
		
		# update selection list
		for d in list(db.selection.find({"list":i})):
			d['list'] = [ l for l in d['list'] if l is not i ]
			d['count'] = len(d['list'])
			if d['count'] == 0:
				db.selection.remove({'_id':d['_id']})
			else:
				db.selection.save(d)
		
		# update search index
		delete_item(oid)
