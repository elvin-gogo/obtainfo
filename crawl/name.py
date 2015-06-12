#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
import pymongo
from bson import ObjectId
import hashlib
import jieba
import re
import argparse

format_title = lambda title : re.sub(ur"【|】|\[|\]|/|\.|\_", u' ', title).upper()

downloadwords = [ u"720P下载", u"720下载", u"1080P下载", u"1080下载", u"高清下载", u"迅雷下载", u'BT下载', u'3D下载', u"下载" ]

torrentwords = [ u"BT种子", u"电影BT种子", u"电影种子", u"免费电影种子", u"最新电影种子", u"最新BT种子", u'免费电影BT种子', u'高清种子', u'快播种子' ]

nonewords = torrentwords + downloadwords + [u'REMUX蓝光无损', u'720P蓝光版', u'上下半宽', u'左右半宽', u'上下半高', u'百度云盘', 
	u'美版', u'DIY简繁', u'蓝光原盘', u'蓝光版', u'HD1280',  u'BD1280', u'1080P', u'720P', u'高清', u'最新', u'最新电影',
	u'免费', u'电影', u'经典电影', u'经典']

singlewords = [u'国', u'粤', u'英', u'国语', u'中字', u'R级', u'蓝光']

def clear_title(title):
	for w in nonewords:
		if w in title:
			title = title.replace(w, '')
	
	return title.lstrip().rstrip()

def filter_title(title):
	words = [u"中字", u"双语", u"字幕"]

	for w in nonewords:
		if w in title:
			title = title.replace(w, '')
	
	if title in singlewords:
		return False
	
	if title == "":
		return False

	t = re.match(r'[a-zA-Z0-9.&_+-]+', title)
	if t and t.group() == title:
		return False
	else:
		return True

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-t", "--target", type=str, help="load downloaded resource to server or dump magnet url from server")
	args = parser.parse_args()
	
	global_level = 7
	
	if args.target == 'l':
		goods = list()
		with codecs.open('title.txt', 'rb', 'utf-8') as f:
			for l in f:
				l = l.split('|')
				goods.append({'_id':ObjectId(l[0].rstrip().lstrip()), 'title':l[1].rstrip().lstrip()})
		
		look = [g['title'] for g in goods]
		with codecs.open('look.txt', 'wb', 'utf-8') as f:
			f.write("\n".join( look ))

	if args.target == 'rl':
		db = pymongo.Connection().scrapy
		
		goods = list()
		with codecs.open('title.txt', 'rb', 'utf-8') as f:
			for l in f:
				l = l.split('|')
				goods.append({'_id':ObjectId(l[0].rstrip().lstrip()), 'title':l[1].rstrip().lstrip()})
		
		for g in goods:
			try:
				m = db.scrapy.find_one({'_id':g['_id']})
				m['title'] = g['title']
				db.scrapy.save(m)
			except:
				pass
	
	if args.target == 'rd':
		db = pymongo.Connection().scrapy
		
		goods = list()
		for d in db.scrapy.find({'level': global_level}):
			t = format_title(d['title'])
			try:
				d['maybe'] = re.findall(ur"《(.+)》", t)[0]
				goods.append(d)
				continue
			except:
				pass
			
			try:
				title = re.findall(ur".+下载", t)[0]
				for w in downloadwords:
					if w in title:
						title = title.replace(w, '')
						break
				else:
					print title
				
				d['maybe'] = " | ".join( [clear_title(w) for w in title.split() if filter_title(w) ] )
				goods.append(d)
				continue
			except:
				pass

			try:
				title = re.findall(ur".+种子", t)[0]
				for w in torrentwords:
					if w in title:
						title = title.replace(w, '')
						break
				else:
					print title
				
				d['maybe'] = " | ".join( [clear_title(w) for w in title.split() if filter_title(w) ] )
				goods.append(d)
				continue
			except:
				pass
			
			d['maybe'] = " | ".join( [clear_title(w) for w in t.split() if filter_title(w) ] )
			goods.append(d)
		
		with codecs.open('title.txt', 'wb', 'utf-8') as f:
			f.write("\n".join( [str(g['_id']) + ' | ' + g['maybe'] + ' | ' + g['title'] for g in goods] ))

	if args.target == 'd':
		db = pymongo.Connection().scrapy
		with codecs.open('title.txt', 'wb', 'utf-8') as f:
			f.write("\n".join( [d['title']for d in db.scrapy.find({'level': global_level})] ))

	if args.target == 'fix':
		ids = list()
		with codecs.open('title.txt', 'rb', 'utf-8') as f:
			for l in f:
				l = l.split('|')
				ids.append(l[0].rstrip().lstrip())
			
		titles = list()
		with codecs.open('look.txt', 'rb', 'utf-8') as f:
			for l in f:
				l = l.split('|')
				titles.append(l[0].rstrip().lstrip())
		
		goods = list()
		for i in range(len(ids)):
			goods.append(ids[i] + ' | ' + titles[i])
		
		with codecs.open('title_look.txt', 'wb', 'utf-8') as f:
			f.write("\n".join( goods ))