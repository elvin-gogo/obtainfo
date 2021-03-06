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
import urllib2, urllib, urlparse

# framework include
from django.conf import settings
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.admin.forms import AdminAuthenticationForm
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, NoReverseMatch

# project include
from .proxy import Proxy, verify_oid, brief
from .hao123_tv import get_resource
from .spider import clean_showtime, query_by_douban_id, query_by_title

from obtainfo.templatetags.obtainfo_tags import pic as render_pic

from pcnile.qiniu_file import Picture
from pcnile.resource import online_table
from pcnile.http import json, JsonResponse
from pcnile.helper import md5sum, group_list
from pcnile.resource import atom_download_resource, format_online_resource, \
	format_netdisk_resource, format_bt, format_ed2k, format_thunder, \
	qualities_0, qualities_1, qualities_2, qualities_3, qualities_4, qualities_5

# third lib include
from shortuuid import uuid as uid
from bson.objectid import ObjectId
import dateutil.parser as dateparser

look = lambda title : db.server.find({'$or':[{'title':title}, {'aka':title}]})

@login_required(login_url='/login/')
@csrf_exempt
@never_cache
def process_image(request):
	try:
		source = str(request.GET['img'])
	except KeyError:
		source = request.FILES['img']

	p = Picture(source, bool(request.GET.get('split', False)) )
	outs = p.upload(selection=bool(request.GET.get('selection', False)))

	success = True
	for o in outs:
		if o['url'] == '':
			success = False

	if success:
		return JsonResponse({'status':'success', 'data':outs})
	else:
		return JsonResponse({'status':'fail'})

@login_required(login_url='/login/')
@csrf_exempt
@never_cache
def process_bt(request):
	try:
		fil = request.FILES['bt']
		info = format_bt(fil)
		info['status'] = 'success'
		return JsonResponse(info)
	except:
		return JsonResponse({'status':'fail'})

@login_required(login_url='/login/')
@csrf_exempt
@never_cache
def process_ed2k(request):	
	try:
		scheme = urlparse.urlparse(str(request.POST['ed2k'])).scheme
		if scheme == 'ed2k':
			info = format_ed2k(str(request.POST['ed2k']))
		elif scheme == 'thunder':
			info = format_thunder(str(request.POST['ed2k']))
		
		info['status'] = 'success'
		return JsonResponse(info)
	except:
		return JsonResponse({'status':'fail'})

class MovieNetdisk(object):
	"""
	patch 这个变量名字不能使用
	"""
	def __init__(self, connection):
		self.db = connection.netdisk
		
	def load(self,):
		try:
			m = self.db.scrapy.find_one({'track':'scrapy'}).sort('level', -1).limit(1)[0]
			m['resource'] = {'online':[], 'complete':[], 'episode':[], 'netdisk':m['resource']}
			m['patch'] = False
			return m
		except:
			return None
	
	def delete(self, oid):
		return self.blacklist(oid)
	
	def patch(self, oid):
		pass
	
	"""
	添加当前项进黑名单
	"""
	def blacklist(self, oid):
		if verify_oid(oid):
			self.db.scrapy.update({'_id':ObjectId(oid)}, {"$set":{'resource':[], 'desc':''}})
			return True
		else:
			return False
	
	"""
	设置保留的标志，标识这次不处理
	"""
	def reserved(self, oid):
		pass
	
	"""
	清除保留的标志
	"""
	def restore(self):
		pass

class MovieQuick(object):
    """
    patch 这个变量名字不能使用
    """
    def __init__(self, connection):
        self.db = connection.scrapy
    
    def load(self,):
        """
        load data structure{_id, title, source, desc, complete resource, patch}
        """
        try:
            m = self.db.fast.find_one({'resource.commit':False})
            m['resource'] = {'online':[], 'netdisk':[], 'episode':[],
                'complete':[resource for resource in m['resource'] if resource['commit'] == False]
            }
            m['patch'] = False
            return m
        except:
            return None
    
    def delete(self, oid):
        return self.blacklist(oid)
    
    def patch(self, oid):
        pass
    
    """
    添加当前项进黑名单
    """
    def blacklist(self, oid):
        if verify_oid(oid):
            self.db.fast.update({'_id':ObjectId(oid)}, {"$set":{'resource':[], 'desc':''}})
            return True
        else:
            return False
    
    """
    设置保留的标志，标识这次不处理
    """
    def reserved(self, oid):
        pass
    
    """
    清除保留的标志
    """
    def restore(self):
        pass

class Hao123TV(object):
	"""
	patch 这个变量名字不能使用
	"""
	def __init__(self, connection):
		self.db = connection.hao123
		
	def load(self,):
		try:
			m = self.db.tv.find_one()
			m['source'] = "http://v.hao123.com/dianshi/%s.htm" % m['id']
			m['desc'] = m['intro']
			m['resource'] = {'online':[], 'complete':[], 'episode':[], 'netdisk':[]}
			m['patch'] = True
			return m
		except:
			return None
	
	def delete(self, oid):
		if verify_oid(oid):
			self.db.tv.remove({'_id':ObjectId(oid)})
			return True
		else:
			return False
	
	def patch(self, oid):
		try:
			m = self.db.tv.find_one({'_id':ObjectId(oid)})
			return {'online':get_resource(m['id']), 'complete':[], 'episode':[], 'netdisk':[]} # hao123 id
		except Exception as e:
			print e
			return None
	
	"""
	添加当前项进黑名单
	"""
	def blacklist(self, oid):
		pass
	
	"""
	设置保留的标志，标识这次不处理
	"""
	def reserved(self, oid):
		pass
	
	"""
	清除保留的标志
	"""
	def restore(self):
		pass
	
	def merge(self, ):
		pass
	
	def count(self, ):
		pass

proxy = Proxy(settings.MONGOPOOL)

@login_required(login_url='/login/')
@csrf_exempt
@never_cache
def manager(request, collection, work):
	if work == 'query':
		title = request.GET.get('title', '')
		did = request.GET.get('douban', '')
		
		if title != '':
			inside = proxy.query_by_title(title)
			douban = query_by_title(title)
		elif did != '':
			inside = proxy.query_by_douban_id(did)
			douban = query_by_douban_id(did)
		else:
			return JsonResponse({'status':'fail'})
		
		return JsonResponse({'status':'success', 'inside':inside, 'douban':douban})
	
	elif work == 'fill':
		mid = request.GET.get('id', '')
		if 'direct' in request.GET:
			direct = True
		else:
			direct = False
		
		return JsonResponse(proxy.fill_new_add(mid, direct))
	
	elif work == 'list':
		m = proxy.exist(oid=request.GET.get('oid', ''), pure=False)
		if m:
			title = m['title']
		else:
			oid, title = '', ''
		
		return render(request, 'add.html',  {'oid':oid, 'title':title, 'sites':online_table.itervalues()},)
	
	elif work == 'save':
		js = json.loads(request.body)
		success = proxy.save_or_modtify(js['data'])
		
		if success:
			try:
				Collections[collection].delete(js['oid'])
			except Exception as e:
				print e
			
			return JsonResponse({'status':'success', 'redirect':'/admin/%s/list/' % collection})
		else:
			return JsonResponse({'status':'fail'})
	else:
		trans_table = {'load':'load', 'patch':'patch', 'delete':'delete', 'reserve':'reserved', 'block':'blacklist'}
		
		try:
			work = trans_table[work]
		except KeyError:
			pass
		
		try:
			if work == 'load':
				return JsonResponse( {'status':'success', 'data':getattr(Collections[collection], work)()} )
			else:
				return JsonResponse( {'status':'success', 'data':getattr(Collections[collection], work)(request.GET['oid'])} )
		except Exception as e:
			print e
			return JsonResponse( {'status':'fail'})

@login_required(login_url='/login/')
@csrf_exempt
def selection(request, work):
	if request.method == 'POST':
		if work == 'douban':
			js = json.loads(request.body)
			
			if db.selection.find({'title':js['title']}).count():
				return jsonresponse({"status":'fail', 'reason':'dumplicate title'})
			
			content = [s.strip() for s in js['content'].split()] # undo must make sure titles in content only one !!!
			js['list'] = [str(i['_id']) for i in db.server.find({'douban.id':{"$in":content}}, {'_id':1})]
			js['count'] = len(js['list'])
			js['addtime'] = datetime.datetime.now()
			
			todb = js
			
			# start save
			res = client.insert('selection', todb)
			if res['status'] == True:
				try:
					_id = res['result']
					if verify_oid(_id):
						todb['_id'] = ObjectId(_id)
						db.selection.insert(todb)
				except:
					pass
				
			return jsonresponse( {"status":"success"} )
		
		if work == 'list':
			title = request.POST['title'].strip()
			stdpic = request.POST['stdpic'].strip()
			bigpic = request.POST['bigpic'].strip()
			desc = request.POST['desc']
			if db.selection.find({'title':title}).count():
				return jsonresponse({"status":'fail', 'reason':'dumplicate title'})
			
			filldata = { "title": title, 'desc':desc, 'stdpic':stdpic, 'bigpic':bigpic, "list":[] }
			content = [s.strip() for s in request.POST['content'].split()] # must make sure titles in content only one !!!
			
			count = 0
			fail = list()
			for c in content:
				ms = look(c)
				if ms.count():
					group = {'id':count, "title": c, "lists":[{'title':m['title'], 'detail':brief(m), 'image':render_pic(m['stdpic']), 'id':str(m['_id'])} for m in ms]}
					filldata['list'].append(group)
					count += 1
				else:
					fail.append(c)
			
			if len(fail):
				with codecs.open('selection.txt', 'wb', 'utf-8') as f:
					f.write("\n".join(fail))
			
			return jsonresponse( {"status":"success", 'data': filldata, 'count':count, 'total':len(content), 'commit':len(content)} )
		
		elif work == 'commit':
			js = json.loads(request.body)
			ls = db.selection.find({'title':js['title']})
			
			if ls.count(): # update movie list
				todb = ls[0]
				
				js['count'] = len(js['list'])
				js['addtime'] = datetime.datetime.now()
				
				res = client.modtify('selection', str(todb['_id']), js)
				if res['status'] == True:
					try:
						if res['result'] == 'success':
							db.selection.save(todb)
					except:
						pass
					
			else: # save new
				todb = js
				todb['count'] = len(js['list'])
				todb['addtime'] = datetime.datetime.now()
				
				res = client.insert('selection', todb)
				if res['status'] == True:
					try:
						_id = res['result']
						if verify_oid(_id):
							todb['_id'] = ObjectId(_id)
							db.selection.insert(todb)
					except:
						pass
			
			return jsonresponse( {"status":"success"} )
		
		elif request.POST['method'] == 'del':
			res = client.delete('selection', request.POST['data'])
			if res['status'] == True:
				try:
					if res['result'] == 'success':
						db.selection.remove( {'_id':ObjectId(request.POST['data']) } )
						return JsonResponse({'status':'success'})
				except:
					pass
				
			return JsonResponse({'status':'fail'})
		
		elif request.POST['method'] == 'pre_edit':
			ls = db.selection.find_one( {'_id':ObjectId(request.POST['data']) } )
			filldata = { "title": ls['title'], "group":[] }
			
			for uid in ls['list']:
				try:
					m = db.server.find( {'_id':ObjectId(uid)} )[0]
					group = {"name": m['title'], "option":[{'k':brief(m), 'v':uid, 'select':True}]}
					filldata['group'].append(group)
				except IndexError:
					pass
				
			return JsonResponse({"status":"success", 'data':filldata})
		
		return JsonResponse({'status':'fail'})

	ds = list(db.selection.find())
	for d in ds:
		d['date'] = d['addtime']
		d['id'] = str(d['_id'])
		del d['_id'], d['addtime']
	
	left = ds[0::2]
	right = ds[1::2]
	return render(request, 'admins/omnibus.html', {'right':right, 'left':left},)

"""
big poster structure(_id, oid, title, state, pic, date)
"""
@login_required(login_url='/login/')
@csrf_exempt
@never_cache
def poster(request):
	def atom_save(i):
		try:
			b = db.big_poster.find({'oid':i['oid']})[0]
			b['pic'] = i['pic']
			
			res = client.modtify('big_poster', str(b['_id']), {'pic':i['pic']})
			if res['status'] == True:
				try:
					if res['result'] == 'success':
						db.big_poster.save(b)
				except:
					pass
			
		except IndexError: # add new
			big_poster = {'oid':i['oid'], 'title':i['title'], 'state':'add', 'pic':i['pic'], 'addtime':datetime.datetime.now()}
			
			res = client.insert('big_poster', big_poster)
			if res['status'] == True:
				try:
					_id = res['result']
					if verify_oid(_id):
						big_poster['_id'] = ObjectId(_id)
						db.big_poster.insert(big_poster)
				except:
					pass

	if request.method == 'POST':
		try:
			qs = json.loads(request.body) # query string
		except ValueError:
			raise Http404
		
		if qs['method'] == 'save':
			if len(qs['data']):
				remote = list()
				for i in qs['data']:
					if i['remote']:
						if i['action'] == 'delete':
							remote.append({'action':'delete', 'id':i['id']})
						elif i['action'] == 'use':
							atom_save(i)
							remote.append({'action':'used', 'id':i['id']})
					else:
						atom_save(i)
					
				if len(remote):
					req = urllib2.Request('http://firecdn.sinaapp.com/post/big_poster/', json.dumps(remote), {'Content-Type': 'application/json'})
					urllib2.urlopen(req, timeout=30).read()
					
				return jsonresponse({'status':'success'})
				
			else:
				return jsonresponse({'status':'fail', 'reason':'empty data field'})

		elif qs['method'] == 'check':
			js = json.loads(urllib2.urlopen("http://firecdn.sinaapp.com/get/big_poster/").read())
			if js['type'] == 'big_poster': # always success
				movies = js['data'][:25]
			
			for m in movies:
				m['lists'] = get_movie_inside(m['title'])
			
			js = {'status':'success', 'data':movies }
			return HttpResponse(json.dumps(js), content_type="application/json")
		
		elif qs['method'] == 'query':
			oid = qs['data']
			if verify_oid(oid): # oid
				try:
					m = db.server.find({'_id':ObjectId(oid)})[0]
					detail = {'title':m['title'], 'detail':brief(m), 'image':render_pic(m['stdpic']), 'id':str(m['_id'])}
					js = {'status':'success', 'type':'oid', 'oid':oid, 'data':detail}
					return HttpResponse(json.dumps(js), content_type="application/json")
				except IndexError:
					return HttpResponse(json.dumps({'status':'fail'}), content_type="application/json")
			else: # title
				inside = get_movie_inside(oid)
				js = {'status':'success', 'type':'result', 'inside':inside, 'count':len(inside)}
				return HttpResponse(json.dumps(js), content_type="application/json")
		
		elif qs['method'] == 'delete':
			# process use delete action
			res = client.delete('big_poster', qs['data'])
			if res['status'] == True:
				try:
					if res['result'] == 'success':
						db.big_poster.remove({'_id':ObjectId(qs['data'])})
						return HttpResponse(json.dumps({'status':'success'}), content_type="application/json")
				except:
					pass
				
			return HttpResponse(json.dumps({'status':'fail'}), content_type="application/json")
			
		elif qs['method'] == 'use':
			bp = db.big_poster.find_one({'_id':ObjectId(qs['data'])})
			bp['state'] = 'add' if bp['state'] == 'use' else 'use'
			
			res = client.modtify('big_poster', qs['data'], {'state':bp['state']})
			
			if res['status'] == True:
				try:
					if res['result'] == 'success':
						db.big_poster.save(bp)
						return HttpResponse(json.dumps({'status':'success'}), content_type="application/json")
				except:
					pass
				
			return HttpResponse(json.dumps({'status':'fail'}), content_type="application/json")

		elif qs['method'] == 'fill':
			# first time fill data
			dbs = [d for d in db.big_poster.find()]
			use = list()
			add = list()
			for d in  dbs:
				d['date'] = str(d['addtime'])
				d['id'] = str(d['_id'])
				del d['_id'], d['addtime']
				if d['state'] == 'add':
					add.append(d)
				else:
					use.append(d)
			
			dbs = use + add
			
			return HttpResponse(json.dumps(dbs), content_type="application/json")
		
		else:
			raise Http404
	else:
		# template fill data
		oid = request.GET.get('oid', '')
		if not verify_oid(oid):
			oid = ''
		
		return render(request, 'admins/poster.html', {'oid':oid},)

@login_required(login_url='/login/')
def admin(request):
	item = list()
	
	today = datetime.date.today()
	yesterday = today - datetime.timedelta(days=1)
	last = today - datetime.timedelta(days=7)
	
	today = datetime.datetime.combine(today, datetime.datetime.min.time())
	yesterday = datetime.datetime.combine(yesterday, datetime.datetime.min.time())
	last = datetime.datetime.combine(last, datetime.datetime.min.time())
	
	item.append({"name":"total movie item", "num":db.server.find().count()} )
		
	tadd = db.server.find({'addtime':{'$gt':today}}).count()
	item.append({"name":"today add item", "num":tadd} )
	item.append({"name":"yesterday add item", "num":db.server.find({'addtime':{'$gt':yesterday}}).count() - tadd } )
	item.append({"name":"last 7 add item", "num":db.server.find({'addtime':{'$gt':last}}).count()} )
	
	item.append({"name":"scrapied item", "num":cdb.scrapy.find().count()} )
	if settings.LEVEL != -1:
		item.append( {"name":"current level %d scrapied item" % settings.LEVEL, "num":cdb.scrapy.find({'level':settings.LEVEL}).count()} )
	item.append({"name":"netdisk scrapied item", "num":ndb.scrapy.find({'track':'scrapy'}).count()} )
	item.append({"name":"online scrapied item", "num":odb.hao123.find({'fresh':True}).count()} )
	item.append({"name":"selection item", "num":db.selection.find().count()} )
	item.append({"name":"big poster item", "num":db.big_poster.find().count()} )
	
	return render(request, 'admins/admin.html',  {'item':item},)
