#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from obtainfo.sync import Client
import json
import datetime

class Command(BaseCommand):
	help = 'build whoosh search index by first time.'
	
	def handle(self, *args, **options):
		cache.clear()