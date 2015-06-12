#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings

from PIL import Image
from pcnile.helper import md5sum
import urllib2
import StringIO
import qiniu.conf
import qiniu.rs
import qiniu.io
import random
import json
import os.path
import requests

"""
七牛帐号密码：862634108@qq.com 123456789
			  pczhaoyun@gmail.com zhy1991223
			  1172585668@qq.com zhy1991223
"""

QINIU_CONFIG = [
	{'bucket':'zinnia', 'ak':'DTsniy9fv4Z1FNGtYG4MDAxjnoV1XXtRmSml4r2e', 'sk':'2GcAc514VuTmDrgqmFpefoqgaWML4kKBDbkCv00-'},
	{'bucket':'firecdn', 'ak':'u_uqAPxWEXC010cjeMoWrV5dSDKBF5Vi1ipnCHFx', 'sk':'uOt_YXIhFRFxwX4cWDTRj5kCHkfkEgJwHHjDnbiR'},
	{'bucket':'obtainfospecial', 'ak':'LAs5VjQ-pzZsQgNPQHAckszGXWn3PiKLBsegF2JO', 'sk':'5JAPsXN5IzKAOlCikkfAcOsJGAmTduCIvoyNMF-S'},
]

def fill_qiniu_conf():
	conf = QINIU_CONFIG[random.randint(0, len(QINIU_CONFIG)-1)]
	qiniu.conf.ACCESS_KEY = conf['ak']
	qiniu.conf.SECRET_KEY = conf['sk']
	return conf['bucket']

def upload_img_full(key):
	def upload_to_qiniu(conf, key, fil):
		template = "http://%s.qiniudn.com/%s"
		
		qiniu.conf.ACCESS_KEY = conf['ak']
		qiniu.conf.SECRET_KEY = conf['sk']
		
		bucket =  conf['bucket']
		
		policy = qiniu.rs.PutPolicy(bucket)
		uptoken = policy.token()
		
		extra = qiniu.io.PutExtra()
		extra.mime_type = "image/jpeg"
		
		for i in range(3):
			fil.seek(0)
			ret, err = qiniu.io.put(uptoken, key, fil, extra)
			if err is not None:
				print 'qiniu upload error: %s ' % err
			else:
				return template % (bucket, key)
		
		return None
	
	QINIU_CONFIGS = [
		{'bucket':'obtainfo', 'ak':'DTsniy9fv4Z1FNGtYG4MDAxjnoV1XXtRmSml4r2e', 'sk':'2GcAc514VuTmDrgqmFpefoqgaWML4kKBDbkCv00-'},
		{'bucket':'pcnile', 'ak':'u_uqAPxWEXC010cjeMoWrV5dSDKBF5Vi1ipnCHFx', 'sk':'uOt_YXIhFRFxwX4cWDTRj5kCHkfkEgJwHHjDnbiR'},
		{'bucket':'putty', 'ak':'LAs5VjQ-pzZsQgNPQHAckszGXWn3PiKLBsegF2JO', 'sk':'5JAPsXN5IzKAOlCikkfAcOsJGAmTduCIvoyNMF-S'},
	]

	with open(os.path.join(settings.MEDIA_ROOT, key), 'rb') as f:
		for conf in QINIU_CONFIGS:
			if upload_to_qiniu(conf, key, f) == None:
				print 'upload_to_qiniu fail'
				return False
		
		f.seek(0)	
		response = requests.post('http://movie.obtainfo.com/poster/', files={'file': f})
		print response.text
		
		if response.json()['status'] == 'success':
			return True
		else:
			print 'upload_to_obtainfo fail'
			return False
	
# 传入的bucket参数放弃使用
def upload_img_to_qiniu(key, fil, bucket = "pcnile"):
	fil.seek(0)
	
	with open(os.path.join(settings.MEDIA_ROOT, key), 'wb') as f:
		f.write(fil.read())
	return '/media/%s' % key

# 不要使用，代码已经修改
def delete_img_to_qiniu(key, bucket = "pcnile"):
	qiniu.conf.ACCESS_KEY = settings.QINIU_ACCESS_KEY
	qiniu.conf.SECRET_KEY = settings.QINIU_SECRET_KEY
	
	for i in range(3):
		ret, err = qiniu.rs.Client().delete(bucket, key)
		if err is not None:
			print 'error: %s ' % err
		else:
			return

class Picture(object):
	def __init__(self, source, split=False):
		if isinstance(source, str):
			load = urllib2.urlopen(source, timeout=30).read()
			sf = StringIO.StringIO(load)
		else: # upload a file
			sf = StringIO.StringIO(source.read())
		
		img = Image.open(sf)
		
		try:
			img = img.convert('RGB')
		except:
			pass
			
		img.save(sf, 'JPEG', quality=100)
		
		self.file = sf
		self.pil = img
		self.split = split

	def md5name(self, fil):
		fil.seek(0)
		return md5sum(fil) + '.jpg'

	def format_img_x_y(self, img, sw, sh):
		# return StringIo
		ow, oh = img.size
		out = StringIO.StringIO()
		pic = img.resize((sw, sw*oh/ow), Image.ANTIALIAS)
		ow, oh = pic.size
		pic = pic.crop( (0, (oh-sh)/2, ow, (oh-sh)/2 + sh) )
		pic.save(out, 'JPEG', quality=95)
		
		return out

	def format_img_y_x(self, img, sw, sh):
		# return StringIo
		ow, oh = img.size
		out = StringIO.StringIO()
		pic = img.resize((sh*ow/oh, sh), Image.ANTIALIAS)
		ow, oh = pic.size
		pic = pic.crop( ((ow-sw)/2, 0, (ow-sw)/2+sw, oh) )
		pic.save(out, 'JPEG', quality=95)
		
		return out
	
	def process_split(self):
		img = self.pil
		ow, oh = img.size
		
		if 220 * oh / ow >= 300:
			bigpic = self.format_img_x_y(img, 220, 300)
		elif 300 * ow / oh >= 220:
			bigpic = self.format_img_y_x(img, 220, 300)
		
		if 130 * oh / ow >= 170:
			stdpic = self.format_img_x_y(img, 130, 170)
		elif 170 * ow / oh >= 130:
			stdpic = self.format_img_y_x(img, 130, 170)
		
		return [
				{'file':bigpic, 'width':220, 'height':300, 'name':self.md5name(bigpic), 'DH':'DH', 'DS':''}, 
				{'file':stdpic, 'width':130, 'height':170, 'name':self.md5name(stdpic), 'DH':'', 'DS':'DS'}
			]

	def process_split_selection(self):
		img = self.pil
		ow, oh = img.size
		
		if 390 * oh / ow >= 243:
			bigpic = self.format_img_x_y(img, 390, 243)
			stdpic = self.format_img_x_y(img, 192, 121)
		elif 243 * ow / oh >= 390:
			bigpic = self.format_img_y_x(img, 390, 243)
			stdpic = self.format_img_y_x(img, 192, 121)
		
		return [
				{'file':bigpic, 'width':390, 'height':243, 'name':self.md5name(bigpic), 'DH':'DH', 'DS':''}, 
				{'file':stdpic, 'width':192, 'height':121, 'name':self.md5name(stdpic), 'DH':'', 'DS':'DS'}
			]
	
	def upload(self, selection=False):
		x , y = self.pil.size
		
		if selection:
			pre = self.process_split_selection()
		else:
			if self.split and x >= 220 and y >= 300:
				pre = self.process_split()
			else:
				pre = [{'file':self.file, 'width':x, 'height':y, 'name':self.md5name(self.file), 'DH':'DH', 'DS':'DS'}]
		
		for p in pre:
			p['url'] = upload_img_to_qiniu(p['name'], p['file'], bucket='firecdn')
			del p['file']
		
		return pre
	
if __name__ == '__main__':

	qiniu.conf.ACCESS_KEY = "u_uqAPxWEXC010cjeMoWrV5dSDKBF5Vi1ipnCHFx"
	qiniu.conf.SECRET_KEY = "uOt_YXIhFRFxwX4cWDTRj5kCHkfkEgJwHHjDnbiR"
	
	policy = qiniu.rs.PutPolicy("pcnile")
	uptoken = policy.token()

	extra = qiniu.io.PutExtra()
	extra.mime_type = "text/plain"
	
	# data 可以是str或read()able对象
	data = StringIO.StringIO("hello!")
	ret, err = qiniu.io.put(uptoken, "dsajafsfshafio.html", data, extra)
	print ret
	if err is not None:
		sys.stderr.write('error: %s ' % err)