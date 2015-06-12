#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
from django.conf import settings
from putty.sync import get_html_from_test_client
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	help = 'build whoosh search index by first time.'
	
	def handle(self, *args, **options):
		timestamp = datetime.datetime.now()
		
		self.stdout.write('Start build html')
		
		success, fail = 0, 0
		collection = settings.MONGOINFO
		for d in collection.find({}, {'title':1}):
			html = get_html_from_test_client(str(d['_id']))
			if html:
				base_dir = settings.HTML_DIR
				with open(os.path.join(base_dir, str(d['_id'])), 'wb') as f:
					f.write(html)
				success += 1
			else:
				fail += 1
		
		print success, fail
		self.stdout.write('Successfully build html use time "%s"' % str((datetime.datetime.now() - timestamp)) )
