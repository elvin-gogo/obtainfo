#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import urllib2
from lxml import etree
from itertools import groupby

target = 'http://www.yayaxz.com/resource/32456'
page = urllib2.urlopen(target).read()
tree = etree.fromstring(page, etree.HTMLParser())

boxes = list()
for box in tree.xpath("//*[@class='resource-list']"):
	season = box.xpath("./dt/h2/span")[0].text
	if re.match(ur'第\d+季', season):
		groups = list()
		for k, group in groupby(box.xpath("./dd"), lambda b : b.xpath("@data-format")[0]):
			seq = list()
			for g in group:
				try:
					r = list(set([e for e in g.xpath(".//a/@href") if e.startswith('ed2k')]))[0]
				except IndexError:
					try:
						r = list(set([e for e in g.xpath(".//a/@href") if e.startswith('magnet')]))[0]
					except IndexError:
						r = ''
				seq.append(r.lower())
			
			groups.append(seq)
		
		boxes.append(groups)
