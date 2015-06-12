#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
import random
import codecs
import re, json, time, base64, sys, copy
from collections import OrderedDict

loginPost = {
	'staticpage':'http://fm.baidu.com/v3Jump.html',
	'charset':'utf8',
	'token':'',
	'tpl':'fm',
	'apiver':'v3',
	'safeflg':'0',
	'u':'http://fm.baidu.com',
	'isPhone':'false',
	'quick_user':'0',
	'logintype':'basicLogin',
	'username':'',
	'password':'',
}

requestHeader = {
	'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
	'Referer':'http://pan.baidu.com/disk/home',
}

loginUrl='https://passport.baidu.com/v2/api/?login'

timestamp = lambda : str(int(time.time()*1000))
random_float = lambda : str(round( random.random(), 5))

class baidu(object):
	#def __init__(self, username='pczhaoyun@gmail.com', password='zhy1991223'):
	def __init__(self, username='561424310', password='zhy1991223'):
		self.username = username
		self.password = password
		self.loginPost = copy.deepcopy(loginPost)
		self.cj = cookielib.LWPCookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj), urllib2.HTTPRedirectHandler(), urllib2.HTTPHandler())
		self._getToken()
	
	def _getToken(self, url1='http://www.baidu.com', url2='http://passport.baidu.com/v2/api/?getapi&tpl=fm'):
		self.opener.open(url1)
		re_token = re.compile('_token=\'(.+?)\'')
		token = re_token.findall( self.opener.open(url2).read() )[0]
		self.loginPost['token'] = token
	
	def _getBdstoken(self):
		page = self.opener.open('http://pan.baidu.com').read()
		re_bdstoken = re.compile(r'FileUtils\.bdstoken=\"(.+?)\"')
		re_uid = re.compile(ur'FileUtils\.sysUID=\"(.*?)\"')
		re_space = re.compile(r'<span id=\"remainingSpace\">(.+?)</div>',re.S)
		self.uid = re_uid.findall(page)[0]
		self.bdstoken = re_bdstoken.findall(page)[0]
		self.space = re_space.findall(page)[0]
		self.space = re.sub(r'</?span>','', self.space)
	
	def _login(self):
		self.loginPost['username'] = self.username
		self.loginPost['password'] = self.password
		result = urllib2.Request(loginUrl, urllib.urlencode(self.loginPost), requestHeader)
		text = self.opener.open(result).read()
		re_codeStr = re.compile(r'codeString=(.*?)&')
		re_no = re.compile(r'err_no=(.*?)&')
		self.codeStr = re_codeStr.findall(text)[0]
		if  int(re_no.findall(text)[0])==0:
			return True
		else:
			return False
	
	def login(self):
		if self._login():
			self._getBdstoken()
			return True
		else:
			return False
	
	"""
	1. baidu yun list api
	http://pan.baidu.com/api/list?channel=chunlei&clienttype=0&web=1&num=100&t=1400114427146&page=1&dir=%2FSoft%2Foffice2003&t=0.10280&order=time&desc=1&_=1400114427147&bdstoken=bf98d083b044e3909d9043a432dfbb2d
	
	2. baidu yun folder structure
	{
		"fs_id": 976343392418862,
		"path": "\/\u52a8\u753b\/\u6d77\u5e95\u603b\u52a8\u5458-MP4",
		"server_filename": "\u6d77\u5e95\u603b\u52a8\u5458-MP4",
		"server_mtime": 1395623629,
		"server_ctime": 1395623629,
		"local_mtime": 1395623629,
		"local_ctime": 1395623629,
		"isdir": 1,
		"category": 6,
		"size": 0,
		"dir_empty": 1,
		"empty": 0
	}
	
	3. baidu yun file structure
	{
		"fs_id": 997805734974024,
		"path": "\/\u52a8\u753b\/\u673a\u5668\u4eba\u74e6\u529b.mkv",
		"server_filename": "\u673a\u5668\u4eba\u74e6\u529b.mkv",
		"size": 1574160361,
		"server_mtime": 1395399360,
		"server_ctime": 1395399360,
		"local_mtime": 1395399358,
		"local_ctime": 1395399358,
		"isdir": 0,
		"category": 1,
		"md5": "b9664fb6f957eeecd59dffeec3f37a10",
		"dlink": "http:\/\/d.pcs.baidu.com\/file\/b9664fb6f957eeecd59dffeec3f37a10?fid=823131261-250528-997805734974024&time=1400138418&rt=pr&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-MNEbVxzyQADRBuexQIIb2Vjzjyg%3D&expires=8h&prisign=RK9dhfZlTqV5TuwkO5ihMQzlM241kT2YfffnCZFTaEPmexAmbPWLXKJ80iU4zC2r2V4S+FNWGNFxHzeBGnigsNFaawa4C9wFhXwC5bIhj4z5T8yM4Gib1paWDpwKM2EokoAzaD8qDPwqyhHIuCXWkoJKwOrktN5yaJjzMFAxE2sJKV7i84jmEODlTCjPLcHG+LRfe1+dK0IiYwWdhn43BicKwM86OSM5&chkv=0&chkbd=0&r=505097728",
		"thumbs": {
			"url1": "http:\/\/d.pcs.baidu.com\/thumbnail\/b9664fb6f957eeecd59dffeec3f37a10?fid=823131261-250528-997805734974024&time=1400137200&rt=pr&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-hvoJTEP72H%2FohtkTqiVcSixQsdk%3D&expires=8h&prisign=RK9dhfZlTqV5TuwkO5ihMQzlM241kT2YfffnCZFTaEPmexAmbPWLXKJ80iU4zC2r2V4S+FNWGNFxHzeBGnigsNFaawa4C9wFhXwC5bIhj4z5T8yM4Gib1paWDpwKM2EokoAzaD8qDPwqyhHIuCXWkoJKwOrktN5yaJjzMFAxE2sJKV7i84jmEODlTCjPLcHG+LRfe1+dK0IiYwWdhn43BicKwM86OSM5&chkv=0&chkbd=0&r=962540316&size=c140_u90&quality=100",
			"url2": "http:\/\/d.pcs.baidu.com\/thumbnail\/b9664fb6f957eeecd59dffeec3f37a10?fid=823131261-250528-997805734974024&time=1400137200&rt=pr&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-hvoJTEP72H%2FohtkTqiVcSixQsdk%3D&expires=8h&prisign=RK9dhfZlTqV5TuwkO5ihMQzlM241kT2YfffnCZFTaEPmexAmbPWLXKJ80iU4zC2r2V4S+FNWGNFxHzeBGnigsNFaawa4C9wFhXwC5bIhj4z5T8yM4Gib1paWDpwKM2EokoAzaD8qDPwqyhHIuCXWkoJKwOrktN5yaJjzMFAxE2sJKV7i84jmEODlTCjPLcHG+LRfe1+dK0IiYwWdhn43BicKwM86OSM5&chkv=0&chkbd=0&r=962540316&size=c360_u270&quality=100",
			"url3": "http:\/\/d.pcs.baidu.com\/thumbnail\/b9664fb6f957eeecd59dffeec3f37a10?fid=823131261-250528-997805734974024&time=1400137200&rt=pr&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-hvoJTEP72H%2FohtkTqiVcSixQsdk%3D&expires=8h&prisign=RK9dhfZlTqV5TuwkO5ihMQzlM241kT2YfffnCZFTaEPmexAmbPWLXKJ80iU4zC2r2V4S+FNWGNFxHzeBGnigsNFaawa4C9wFhXwC5bIhj4z5T8yM4Gib1paWDpwKM2EokoAzaD8qDPwqyhHIuCXWkoJKwOrktN5yaJjzMFAxE2sJKV7i84jmEODlTCjPLcHG+LRfe1+dK0IiYwWdhn43BicKwM86OSM5&chkv=0&chkbd=0&r=962540316&size=c850_u580&quality=100",
			"icon": "http:\/\/d.pcs.baidu.com\/thumbnail\/b9664fb6f957eeecd59dffeec3f37a10?fid=823131261-250528-997805734974024&time=1400137200&rt=pr&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-hvoJTEP72H%2FohtkTqiVcSixQsdk%3D&expires=8h&prisign=RK9dhfZlTqV5TuwkO5ihMQzlM241kT2YfffnCZFTaEPmexAmbPWLXKJ80iU4zC2r2V4S+FNWGNFxHzeBGnigsNFaawa4C9wFhXwC5bIhj4z5T8yM4Gib1paWDpwKM2EokoAzaD8qDPwqyhHIuCXWkoJKwOrktN5yaJjzMFAxE2sJKV7i84jmEODlTCjPLcHG+LRfe1+dK0IiYwWdhn43BicKwM86OSM5&chkv=0&chkbd=0&r=962540316&size=c60_u60&quality=100"
		}
	}
	"""
	def _get_fs_map(self, folder='/', level=0):
		# template argument : time(long), page(int), dir(str), process(float), token(bdstoken)
		template = "http://pan.baidu.com/api/list?channel=chunlei&clienttype=0&web=1&num=100&t={time}&page={page}&dir={folder}&t={process}&order=time&desc=1&_={time}&bdstoken={token}"
		
		# get current folder all files and sub folders
		page = 1
		lists = list()
		folder = urllib.quote_plus(folder.encode('utf-8'))
		while True:
			url = template.format(time=timestamp(), page=str(page), folder=folder, process=random_float(), token=self.bdstoken)
			content = self.opener.open(url).read()
			js = json.loads(content)
			
			lists += js['list']
			if len(js['list']) < 100:
				print "total lists %d, current return lists %d" % (len(lists), len(js['list']))
				break
			page += 1
		
		# get sub folders files
		if level == -1:
			for l in lists:
				if l['isdir'] == 1:
					l['sub'] = self._get_fs_map(l['path'], level)
		elif level:
			level -= 1
			for l in lists:
				if l['isdir'] == 1:
					l['sub'] = self._get_fs_map(l['path'], level)
		
		# filter lists structure with my self format
		return lists

	def build_fs_map(self, folder='/', save=False, update=True):
		# if fs map is already exists and update = False, just return
		# else update fs map and return the last one
		# if save = True, before return save it to json formate
		
		if update == False:
			try:
				with codecs.open('fs_map.json', 'r') as f:
					fs_map = json.load(f)
			except:
				fs_map = self._get_fs_map(folder)
		else:
			fs_map = self._get_fs_map(folder)
		
		if save:
			with codecs.open('fs_map.json', 'wb', 'utf-8') as f:
				json.dump(fs_map, f)
		
		return fs_map
	
	def flat_folder(self, path, root, isroot=True):
		folder = self._get_fs_map(path) # get current folder content
		
		success = 0
		for f in folder:
			if f['isdir'] == 1:
				if self.flat_folder(f['path'], root, isroot=False):
					success += 1
				else:
					print 'flat sub folder %s fail' % f['path']
			elif isroot == False:
				if self.move(f['path'], root, f['server_filename']):
					success += 1
			else:
				success += 1
		
		if success == len(folder):
			if isroot == False:
				return self.delete(path)
			else:
				return True
		else:
			return False
	
	"""
	get pan capacity return {"used":2391150242255,"total":2429877747712}
	"""
	def get_pan_capacity(self):
		template = "http://pan.baidu.com/api/quota?channel=chunlei&clienttype=0&web=1&t={time}&bdstoken={token}"
		url = template.format(time=timestamp(), token=self.bdstoken)
		content = self.opener.open(url).read()
		js = json.loads(content)
		return js
	
	"""
	every time only one file or one folder can be opera
	
	baidu yun delete format:
		filelist:["/阿凡达(加长版).Avatar.2009.EXTENDED.MiniBD.720p.x264.AC3-CnSCG"]
		
	baidu yun rename format:
		filelist:[{"path":"/20140428","newname":"test"}]
		
	baidu yun move format:
		filelist:[{"path":"/阿凡达(加长版).Avatar.2009.EXTENDED.MiniBD.720p.x264.AC3-CnSCG/阿凡达.mkv","dest":"/六福喜事 Hello.Babies.2014.720p.WEB-DL.720p.x264.AAC-LZHD","newname":"阿凡达.mkv"}]
	"""
	def delete(self, path):
		data = json.dumps([ path ])
		return self.filemanager('delete', data)
	
	def move(self, path, dest, newname):
		data = json.dumps([ OrderedDict([('path', path), ('dest', dest), ('newname', newname)]) ])
		return self.filemanager('move', data)
	
	def rename(self, path, newname):
		data = json.dumps([ OrderedDict([('path', path), ('newname', newname)]) ])
		return self.filemanager('rename', data)
	
	def filemanager(self, opera, data):
		template = "http://pan.baidu.com/api/filemanager?channel=chunlei&clienttype=0&web=1&opera={opera}&bdstoken={token}"
		url = template.format(opera=opera, token=self.bdstoken)
		
		post = "filelist=" + urllib.quote(data)
		
		result = urllib2.Request(url, post, requestHeader)
		content = self.opener.open(result).read()
		
		js = json.loads(content)['info'][0] # only one can be opera
		
		try:
			if js['errno'] == 0:
				return True
			else:
				return False
		except KeyError:
			return False
		
	"""
	share with password
	"""
	def share(self, fid, plivate=True):
		def pwd():
			pwd_str = "abcdefghijklmnopqrstuvwxyz1234567890"
			max_random = len(pwd_str)-1
			return "".join( [pwd_str[random.randint(0, max_random)] for i in range(4)] )
		
		template = "http://pan.baidu.com/share/set?channel=chunlei&clienttype=0&web=1&bdstoken={token}"
		url = template.format(token=self.bdstoken)
		
		fid_list = "fid_list=%5B" + "%s" % fid + "%5D&"
		if plivate:
			data = OrderedDict([('schannel', 4), ('channel_list', []), ('pwd', pwd())])
		else:
			data = OrderedDict([('schannel', 4), ('channel_list', [])])
		
		post =  urllib.urlencode(data)
		post = fid_list + post
		
		result = urllib2.Request(url, post, requestHeader)
		content = self.opener.open(result).read()
		js = json.loads(content)
		
		if plivate:
			js['pwd'] = data['pwd']
		
		return js
		
	def test(self):
		self.login()
		return self.build_fs_map()
	
	# http://pan.baidu.com/share/transfer?channel=chunlei&clienttype=0&web=1&from=3930503794&shareid=4206143443&bdstoken=f1ab90fd67ea0b299dd5c9a66db82b64
	def transfer(self, ):
		template = "http://pan.baidu.com/share/transfer?channel=chunlei&clienttype=0&web=1&from={uk}&shareid={shareid}&bdstoken={token}"
		pass
	
	def fetch(self, ):
		pass
	
	# 1. 只有在链接的上下文中才会获取一个速度快的Xcode
	# 2. 估计小于1GB的文件采用http://nj.baidupcs.com/ 这个服务器，然后获取的链接只能使用一次，无法复制到外部使用。
	#    只有使用百度云的reference才可以。
	def fast_download(self, url):
		result = urllib2.Request(url, headers=requestHeader)
		opener = self.opener.open(result)
		url = opener.geturl()
		return (opener,url)
	
	def session_save(self):
		pass
	
	def session_restore(self):
		pass
