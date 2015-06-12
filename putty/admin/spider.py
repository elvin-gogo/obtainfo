#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import base64
import StringIO
import datetime
from PIL import Image
import urllib2, urllib

from lxml import etree
from pcnile.qiniu_file import Picture

def query_by_title(title):
	template = u"http://api.douban.com/v2/movie/search?q=%s"
	title = urllib.quote(title.encode('utf-8'))
	movies = json.loads(urllib2.urlopen(template % title, timeout=30).read())
	lists = list()
	
	for m in movies['subjects'][:30]: # only get first ten item
		if m['images']['small'] != '':
			image = m['images']['small']
		elif m['images']['media'] != '':
			image = m['images']['media']
		elif m['images']['large'] != '':
			image = m['images']['large']
		else:
			image = ''
		if image != '':
			image = "data:image/jpeg;base64,%s" % base64.b64encode(urllib2.urlopen(image, timeout=10).read())
		
		t = m['original_title'] + " \n %s" % m['year']
		
		detail = {'title':m['title'] + " " + m['subtype'] , 'detail':t, 'image':image, 'id':m['id']}
		lists.append(detail)
		
	return lists

def query_by_douban_id(did):
	url = "http://api.douban.com/v2/movie/subject/%s" % did
	m = json.loads(urllib2.urlopen(url, timeout=30).read())
	
	if m['images']['small'] != '':
		image = m['images']['small']
	elif m['images']['media'] != '':
		image = m['images']['media']
	elif m['images']['large'] != '':
		image = m['images']['large']
	else:
		image = ''
	if image != '':
		image = "data:image/jpeg;base64,%s" % base64.b64encode(urllib2.urlopen(image, timeout=10).read())
	
	t = m['original_title'] + u'/' + m['summary'] + u'/' + m['year']
	lists = [{'title':m['title'], 'detail':t, 'image':image, 'id':m['id']}]
	
	return lists

def clean_showtime(showtime):
	"""
	基于可能的格式清洗成标准的日期格式
	"""
	if isinstance(showtime, str) or isinstance(showtime, unicode):
		pass
	elif isinstance(showtime, list):
		showtime = showtime[0]
	else:
		showtime = str(showtime)
	
	if showtime != '':
		if re.match(ur"^\d{4}-\d+-\d+$", showtime): # one
			try:
				da = datetime.datetime.strptime(re.match(ur"^\d{4}-\d+-\d+$", showtime).group(0), "%Y-%m-%d")
				da = datetime.date(da.year, da.month, da.day)
				return da.isoformat()
			except ValueError:
				rep = { "2006-0-09":"2006-01-09", 
						"2000-06-31":"2000-06-30", 
						"1997-09-31":"1997-09-30", 
						"2012-07-00":"2012-07-01", 
						"2013-01-00":"2012-07-01",
						"2011-09-31":"2011-09-30"
					}
				da = datetime.datetime.strptime(re.match(ur"^\d{4}-\d+-\d+$", rep[showtime]).group(0), "%Y-%m-%d")
				return datetime.date(da.year, da.month, da.day).isoformat()
		elif re.match(ur"^(\d{4})\.(\d+)\.(\d+)", showtime): # full 
			try:
				da = re.match(ur"^(\d{4})\.(\d+)\.(\d+)", showtime)
				da = datetime.date(int(da.group(1)), int(da.group(2)), int(da.group(3)))
				return da.isoformat()
			except ValueError:
				return showtime
		elif re.match(ur"^\d{4}年\d+月\d+日", showtime): # full 
			try:
				da = re.match(ur"^(\d{4})年(\d+)月(\d+)日", showtime)
				da = datetime.date(int(da.group(1)), int(da.group(2)), int(da.group(3)))
				return da.isoformat()
			except ValueError:
				return showtime
		elif re.match(ur"^\d{4}年\d+月\d+号", showtime): # two
			try:
				da = re.match(ur"^(\d{4})年(\d+)月(\d+)号", showtime)
				da = datetime.date(int(da.group(1)), int(da.group(2)), int(da.group(3)))
				return da.isoformat()
			except ValueError:
				return showtime
		elif re.match(ur"^\d{4}-\d+", showtime): # three
			try:
				da = datetime.datetime.strptime(re.match(ur"^\d{4}-\d+", showtime).group(0), "%Y-%m")
				da = datetime.date(da.year, da.month, 1)	
				return da.isoformat()
			except ValueError:
				exc += 1
				rep = { u"2014-2015年间":"2014-12-01", 
						u"1973-1993":"1973-01-01", 
						u"1943-1955":"1943-01-01"
					}
				da = datetime.datetime.strptime(re.match(ur"^\d{4}-\d+-\d+$", rep[showtime]).group(0), "%Y-%m-%d")
				return datetime.date(da.year, da.month, da.day).isoformat()
		elif re.match(ur"^\d{4}年\d+月", showtime): # two
			try:
				da = re.match(ur"^(\d{4})年(\d+)月", showtime)
				return datetime.date(int(da.group(1)), int(da.group(2)), 1).isoformat()
			except ValueError:
				return showtime
		elif re.match(ur"^\d{4}", showtime): # four
			try:
				da = datetime.datetime.strptime(re.match(ur"^\d{4}", showtime).group(0), "%Y")
				da = datetime.date(da.year, 1, 1)	
				return da.isoformat()
			except ValueError:
				return showtime
		else:
			return showtime
	else:
		return showtime

class DoubanSpider(object):
	def __init__(self, did):
		self.did = did
		self.screen_url = "http://movie.douban.com/subject/%s/" % did
		self.api_url = "http://api.douban.com/v2/movie/subject/%s" % did
		
		self.movie_kv = {
			'aka' : re.compile(ur'^又名:(.*)'),
			'director' : re.compile(ur'^导演:(.*)'),
			'writer' : re.compile(ur'^编剧:(.*)'),
			'actor' : re.compile(ur'^主演:(.*)'),
			'genre' : re.compile(ur'^类型:(.*)'),
			'area' : re.compile(ur'^制片国家/地区:(.*)'),
			'language' : re.compile(ur'^语言:(.*)'),
			'showtime' : re.compile(ur'^上映日期:(.*)'),
			'runtime' : re.compile(ur'^片长:(.*)'),
			'imdb' : re.compile(ur'^IMDb链接:(.*)')
		}
		
		self.tv_kv = {
			'aka' : re.compile(ur'^又名:(.*)'),
			'director' : re.compile(ur'^导演:(.*)'),
			'writer' : re.compile(ur'^编剧:(.*)'),
			'actor' : re.compile(ur'^主演:(.*)'),
			'genre' : re.compile(ur'^类型:(.*)'),
			'area' : re.compile(ur'^制片国家/地区:(.*)'),
			'language' : re.compile(ur'^语言:(.*)'),
			'showtime' : re.compile(ur'^首播:(.*)'),
			'episode' : re.compile(ur'^集数:(.*)'),
			'runtime' : re.compile(ur'^单集片长:(.*)'),
			'imdb' : re.compile(ur'^IMDb链接:(.*)')
		}
		
		self.re_season = re.compile(ur'^季数:(.*)')
	
	def scrape_screen(self, page, item, kv):
		string_field = [k for k,v in item.iteritems() if v == '']
		
		tree = etree.fromstring(page, etree.HTMLParser())
		
		try:
			item['title'] = tree.xpath("//*[@id='content']/h1/span[1]")[0].text
		except IndexError:
			pass
		
		try:
			select = tree.xpath("//*[@id='season']")[0]
			item['season'] = select.find("option[@selected]").text
		except IndexError:
			item['season'] = str()
		
		"""
		force string to unicode code
		"""
		info = etree.tostring(tree.xpath("//*[@id='info']")[0], encoding='utf-8')
		info = re.split('<br/>', info)
		for i in info:
			s = re.sub(r'</?\w+[^>]*>', '', i).strip().decode('utf-8')
			for k,v in kv.iteritems():
				m = v.match(s)
				if m:
					c = [s.strip() for s in m.group(1).split('/')]
					if k in string_field:
						item[k] = c[0]
					else:
						item[k] = c
					break
			
			if item['season'] == "" and self.re_season.match(s):
				item['season'] = self.re_season.match(s).group(1).strip()
		
		try:
			info = etree.tostring(tree.xpath("//*[@id='link-report']")[0], encoding='utf-8')
			info = re.sub(r"</br>", '\n', info)
			item['plot'] = re.sub(r'</?\w+[^>]*>','',info).replace(u'©豆瓣'.encode('utf-8'), '').replace(' ', '').strip()
		except IndexError:
			item['plot'] =str()
		
		try:
			item['poster'] = tree.xpath("//*[@id='mainpic']/a/img/@src")[0]
		except IndexError:
			item['poster'] = str()
		
		try:		
			item['year'] = re.match('\((\d+)\)', tree.xpath("//*[@id='content']/h1/span[2]")[0].text).group(1)
		except IndexError:
			pass
		except AttributeError:
			pass
		
		return item
	
	def scrape_screen_for_movie(self, page, api):
		item = {
			'title':'', 'aka':[],
			'director':[], 'writer':[], 'actor':[],
			'genre':[], 'area':[], 'language':[],
			'showtime':'', 'year':'',
			'runtime':'', 'imdb':'', 'plot':'',
		}
		
		if page:			
			return self.scrape_screen(page, item, self.movie_kv)
		else:
			item['director'] = [d['name'] for d in api['directors']]
			item['actor'] = [d['name'] for d in api['casts']]
			return item

	def scrape_screen_for_tv(self, page, api):
		item = {
			'title':'', 'aka':[],
			'director':[], 'writer':[], 'actor':[],
			'genre':[], 'area':[], 'language':[],
			'showtime':'', 'year':'',
			'season':'', 'runtime':'', 'episode':'', 'imdb':'', 'plot':'',
		}
		
		if page:
			return self.scrape_screen(page, item, self.tv_kv)
		else:
			item['director'] = [d['name'] for d in api['directors']]
			item['actor'] = [d['name'] for d in api['casts']]
			return item
	
	def fake_info_doc(self):
		aitem = json.loads(urllib2.urlopen(self.api_url, timeout=15).read())
		try:
			page = urllib2.urlopen(self.screen_url, timeout=15).read()
		except urllib2.HTTPError:
			page = ''
		
		if aitem['subtype'] == 'movie':
			vitem = self.scrape_screen_for_movie(page, aitem)
		else:
			vitem = self.scrape_screen_for_tv(page, aitem)
		
		"""
		start fake mongodb doc 
		"""
		# add all movie aka name
		aitem['aka'].append(aitem['original_title'])
		aitem['aka'] = list(set(aitem['aka']))
		aitem['aka'] = filter(lambda x:x !=aitem['title'], aitem['aka'])
		
		# get movie brief image
		content = urllib2.urlopen(aitem['images']['large'], timeout=30).read()
		img = Image.open(StringIO.StringIO(content)).size
		x, y = img
		
		if x > 220:
			image = Picture(StringIO.StringIO(content), split=True).upload()
			if image[0]['DS'] == 'DS':
				stdpic, bigpic = image[0]['url'], image[1]['url']
			else:
				stdpic, bigpic = image[1]['url'], image[0]['url']
		else:
			image = Picture(StringIO.StringIO(content)).upload()
			stdpic, bigpic = image[0]['url'], image[0]['url']
		
		did = self.did
		if aitem['subtype'] == 'movie':
			# pack info to fake movie item
			info = {'_id':'', 'type':aitem['subtype'],
				'title':aitem['title'], 'aka':aitem['aka'],
				'stdpic':stdpic, 'bigpic':bigpic,
				'director':vitem['director'], 'writer':vitem['writer'], 'actor':vitem['actor'],
				'genre':aitem['genres'], 'plot':aitem['summary'].rstrip(u"©豆瓣"),
				'imdb':vitem['imdb'], 'douban':{'id':did, 'ranking':{'score':aitem['rating']['average'], 'count':aitem['ratings_count']}},
				'area':aitem['countries'], 'language':vitem['language'],
				'showtime':vitem['showtime'], 'year':aitem['year'],
				'runtime':vitem['runtime'],
				'samesite':[],
			}
		else:
			# pack info to fake tv item
			info = {'_id':'', 'type':aitem['subtype'],
				'title':aitem['title'], 'aka':aitem['aka'],
				'stdpic':stdpic, 'bigpic':bigpic,
				'director':vitem['director'], 'writer':vitem['writer'], 'actor':vitem['actor'],
				'genre':aitem['genres'], 'plot':aitem['summary'].rstrip(u"©豆瓣"),
				'imdb':vitem['imdb'], 'douban':{'id':did, 'ranking':{'score':aitem['rating']['average'], 'count':aitem['ratings_count']}},
				'area':aitem['countries'], 'language':vitem['language'],
				'showtime':vitem['showtime'], 'year':aitem['year'],
				'season':vitem['season'], 'episode':vitem['episode'], 'runtime':vitem['runtime'],
			}
		
		return info

if __name__ == '__main__':
	response = urllib2.urlopen('http://movie.douban.com/subject/25755667/', timeout=15).read()
	vitem = resolve_tv_view_content('25755667', response)
	print re.findall(ur"单集片长".encode('utf-8'), response)
	print vitem
