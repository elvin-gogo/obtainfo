#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from pcnile.search import Search
from django.core.management.base import BaseCommand, CommandError
import datetime

class Command(BaseCommand):
	help = 'build whoosh search index by first time.'
	
	def handle(self, *args, **options):
		timestamp = datetime.datetime.now()
		
		self.stdout.write('Start build index')
		
		s = Search(settings.INDEX_PATH, settings.MONGOINFO)
		s.initialize()
		
		self.stdout.write('Successfully build search index use time "%s"' % str((datetime.datetime.now() - timestamp)) )
