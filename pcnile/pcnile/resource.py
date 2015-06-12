#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import jieba
import libtorrent
import chardet
import urlparse
import urllib
import base64

from django.utils.encoding import force_unicode, force_str, DjangoUnicodeDecodeError

"""
jieba.load_userdict(os.path.join(os.path.dirname(os.path.dirname(__file__)), "pcnile", "userdict.txt"))
"""

qualities_0 = ['TS', 'CAM', 'TC',]
qualities_1 = ['HDTS', 'HDCAM', 'CAMRIP', 'HDTC', 'TC720P', 'TC720']
qualities_2 = ['R5', 'R6', '720RE', 'HDRE',]
qualities_3 = ['DVDSCR', 'DVD-RIP', 'DVDR', 'DVDRIP', 'DVD', 'HDDVD', 'PDTVRIP', 'VODRIP']
qualities_3_5 = ['WEB-DL', 'WEBDL', 'WEBRIP', 'WEB-RIP',]
qualities_4 = ['720P', '480P', '1080P', 'HR-HDTV', 'HDRIP', 'HDTVRIP', 'HD720', 'HD720P',
			   'HD1080', 'HD1080P', '1080', '720', 'HD',  'HDTV',]
qualities_4_5 = ['BDRIP', 'BRRIP', 'BLURAY', 'BD', 'BLU-RAY', 'BD1080', 'BD1080P', 'BD720', 'BD720P',]
qualities_5 = ['3D',]

qualities_table = dict()
for q in qualities_0:
	qualities_table[q] = 0
for q in qualities_1:
	qualities_table[q] = 1
for q in qualities_2:
	qualities_table[q] = 2
for q in qualities_3: # boundary
	qualities_table[q] = 3
for q in qualities_3_5:
	qualities_table[q] = 4
for q in qualities_4:
	qualities_table[q] = 5
for q in qualities_4_5:
	qualities_table[q] = 6
for q in qualities_5:
	qualities_table[q] = 7

qualities_3 += qualities_3_5
qualities_4 += qualities_4_5
qualities = set(qualities_0 + qualities_1 + qualities_2 + qualities_3 + qualities_4 + qualities_5)

re_split = re.compile(ur'[^《》」「】【\[\]\)\(/\+\._ ]+', re.U)

def fake_ordered_set(names):
	df = set()
	goods = list()
	for n in names: # fake ordered set
		if n not in df:
			df.add(n)
			goods.append(n)
	
	return goods

def quality_level(level):
    level = level.upper()
    
    if level in qualities_0:
        return 0
    elif level in qualities_1:
        return 1
    elif level in qualities_2:
        return 2
    elif level in qualities_3:
        return 3
    elif level in qualities_4:
        return 4
    elif level in qualities_5:
        return 5
    
    return 0

def fast_resource_quality(name):
    names = [ w.upper() for w in re_split.findall(name) if w.strip() != '' ]
    goods = fake_ordered_set(names)
    
    for q in qualities:
        if q in goods:
            quality = q
            break
    else:
        quality = 'DVD'
    
    return quality

def quality_rule(quality):
	if len(quality) == 1:
		return quality[0]
	else:
		quality = sorted(quality, key=lambda x : qualities_table[x])
		
		if qualities_table[quality[0]] <= 4:
			return quality[0]
		elif qualities_table[quality[-1]] > 4:
			return quality[-1]
		else:
			return quality[0]

def resource_quality(name):
	name = name.upper()
	names = set([ w for w in re_split.findall(name) if w.strip() ])
	quality = list(names & qualities)
	if len(quality):
		return quality_rule(quality)
	else:
		names = set([ w for w in jieba.cut(name) if w.strip() != '' ])
		quality = list(names & qualities)
		if len(quality):
			return quality_rule(quality)
		else:
			return 'DVD'

def format_bt(fil):
	metadata = libtorrent.bdecode(fil.read())
	info = libtorrent.torrent_info(metadata)
	
	try:
		name = force_unicode(metadata['info']['name'])
	except DjangoUnicodeDecodeError:
		try:
			name = force_unicode(metadata['info']['name'], 'gbk')
		except DjangoUnicodeDecodeError:
			try:
				name = force_unicode(metadata['info']['name'], 'gb2312')
			except DjangoUnicodeDecodeError:
				print 'force_unicode fail'
	
	size = "%s G" % str(round(float(info.total_size()) / 1024 / 1024 / 1024, 2))
	quality = resource_quality(name)
	link = u"magnet:?xt=urn:btih:%s&dn=%s" % (info.info_hash(), u"【www.obtainfo.com】" + name )
	
	return {'link':link.encode('utf-8'), 'name':name.encode('utf-8'), 'size':size , 'quality':quality}

def format_bt_by_content(content):
	metadata = libtorrent.bdecode(content)
	info = libtorrent.torrent_info(metadata)
	
	try:
		name = force_unicode(metadata['info']['name'])
	except DjangoUnicodeDecodeError:
		try:
			name = force_unicode(metadata['info']['name'], 'gbk')
		except DjangoUnicodeDecodeError:
			try:
				name = force_unicode(metadata['info']['name'], 'gb2312')
			except DjangoUnicodeDecodeError:
				print 'force_unicode fail'
	
	size = "%s G" % str(round(float(info.total_size()) / 1024 / 1024 / 1024, 2))
	quality = resource_quality(name)
	link = u"magnet:?xt=urn:btih:%s&dn=%s" % (info.info_hash(), u"【www.obtainfo.com】" + name )
	
	return {'link':link.encode('utf-8'), 'name':name.encode('utf-8'), 'size':size , 'quality':quality}

def format_ed2k(link):
	if link.startswith('ed2k'):
		ed2k = link.split('|')
		
		name = ed2k[2]
		try:
			name = str(name)
		except UnicodeEncodeError:
			name = force_str(name)
		name = force_unicode(urllib.unquote_plus(name))
		
		quality = resource_quality(name)
		size = "%.2f G" % (int(ed2k[3]) / 1024 / 1024 / 1024.0)
		
		return {'link':link, 'name':name.encode('utf-8'), 'size':size , 'quality':quality}

def format_thunder(link):
    Thunder=link[10:]
    Thunder=base64.decodestring(Thunder)
    Thunder=Thunder[2:len(Thunder)-2]
    
    scheme = urlparse.urlparse(Thunder).scheme
    
    if scheme == 'ed2k':
        info = format_ed2k(Thunder)
        info['link'] = link
        return info
    
    try:
        name = urllib.unquote_plus( urlparse.urlparse(Thunder).path.split('/')[-1] )
        name = force_unicode(name)
    except DjangoUnicodeDecodeError:
        try:
            name = force_unicode(name, 'gbk')
        except DjangoUnicodeDecodeError:
            try:
                name = force_unicode(name, 'gb2312')
            except UnicodeEncodeError:
                name = name

    quality = resource_quality(name)
    size = "0.0 G"
    
    return {'link':link, 'name':name.encode('utf-8'), 'size':size , 'quality':quality}

online_table = {
	'hunantv':{'name':u'芒果TV', 'logo':'http://img04.taobaocdn.com/imgextra/i4/495498642/TB2APdnaFXXXXXZXXXXXXXXXXXX_!!495498642.gif'},
	'bilibili':{'name':u'哔哩哔哩', 'logo':'http://img03.taobaocdn.com/imgextra/i3/495498642/TB2KTnNXVXXXXa1XXXXXXXXXXXX-495498642.jpg'},
	'kankan':{'name':u'迅雷看看', 'logo':"http://img04.taobaocdn.com/imgextra/i4/495498642/TB2qYTbXVXXXXcvXXXXXXXXXXXX-495498642.gif"},
	'sina':{'name':u'新浪视频', 'logo':'http://img04.taobaocdn.com/imgextra/i4/495498642/TB2GwzbXVXXXXc.XXXXXXXXXXXX-495498642.png'},
	'youtube':{'name':u'YouTube', 'logo':'http://img01.taobaocdn.com/imgextra/i1/495498642/TB2WknbXVXXXXbpXXXXXXXXXXXX-495498642.jpg'},
	'ku6':{'name':u'酷6网', 'logo':'http://img01.taobaocdn.com/imgextra/i1/495498642/TB2JQTbXVXXXXXuXpXXXXXXXXXX-495498642.gif'},
	'funshion':{'name':u'风行网', 'logo':'http://img02.taobaocdn.com/imgextra/i2/495498642/TB2IffbXVXXXXaLXXXXXXXXXXXX-495498642.gif'},
	'fun':{'name':u'风行网', 'logo':'http://img02.taobaocdn.com/imgextra/i2/495498642/TB2IffbXVXXXXaLXXXXXXXXXXXX-495498642.gif'},
	'wasu':{'name':u'华数TV', 'logo':'http://img03.taobaocdn.com/imgextra/i3/495498642/TB2zU6aXVXXXXX9XpXXXXXXXXXX-495498642.gif'},
	'pptv':{'name':u'PPTV', 'logo':'http://img03.taobaocdn.com/imgextra/i3/495498642/TB2dfDbXVXXXXavXXXXXXXXXXXX-495498642.gif'},
	'tudou':{'name':u'土豆', 'logo':'http://img01.taobaocdn.com/imgextra/i1/495498642/TB2HaLbXVXXXXXvXpXXXXXXXXXX-495498642.gif'},
	'baofeng':{'name':u'暴风', 'logo':'http://img04.taobaocdn.com/imgextra/i4/495498642/TB2aIHbXVXXXXb0XXXXXXXXXXXX-495498642.gif'},
	'pps':{'name':u'PPS', 'logo':'http://img04.taobaocdn.com/imgextra/i4/495498642/TB2.bvbXVXXXXcUXXXXXXXXXXXX-495498642.gif'},
	'letv':{'name':u'乐视', 'logo':'http://img04.taobaocdn.com/imgextra/i4/495498642/TB28frbXVXXXXaAXXXXXXXXXXXX-495498642.gif'},
	'm1905':{'name':u'电影网', 'logo':'http://img03.taobaocdn.com/imgextra/i3/495498642/TB2uxvbXVXXXXXsXXXXXXXXXXXX-495498642.gif'},
	'qq':{'name':u'腾讯', 'logo':'http://img04.taobaocdn.com/imgextra/i4/495498642/TB2LdvbXVXXXXbDXXXXXXXXXXXX-495498642.gif'},
	'cntv':{'name':u'CNTV', 'logo':'http://img02.taobaocdn.com/imgextra/i2/495498642/TB2SgrbXVXXXXX2XXXXXXXXXXXX-495498642.gif'},
	'sohu':{'name':u'搜狐', 'logo':'http://img01.taobaocdn.com/imgextra/i1/495498642/TB2Yt2bXVXXXXaaXXXXXXXXXXXX-495498642.gif'},
	'iqiyi':{'name':u'爱奇艺', 'logo':'http://img01.taobaocdn.com/imgextra/i1/495498642/TB26ozaXVXXXXa6XpXXXXXXXXXX-495498642.gif'},
	'kumi':{'name':u'酷米', 'logo':'http://img02.taobaocdn.com/imgextra/i2/495498642/TB2QVHbXVXXXXadXpXXXXXXXXXX-495498642.gif'},
	'youku':{'name':u'优酷', 'logo':'http://img02.taobaocdn.com/imgextra/i2/495498642/TB2jdTbXVXXXXa1XXXXXXXXXXXX-495498642.gif'},
	'56':{'name':u'56我乐', 'logo':'http://img03.taobaocdn.com/imgextra/i3/495498642/TB2ErLbXVXXXXclXXXXXXXXXXXX-495498642.gif'},
	'61':{'name':u'淘米视频', 'logo':'http://img04.taobaocdn.com/imgextra/i4/495498642/TB2SY_bXVXXXXcfXXXXXXXXXXXX-495498642.gif'},
}

def format_online_resource(online, printf=False):
	table = online_table
	domain = [
		'bilibili', 'kankan', 'sina', 'youtube', 'ku6', 'funshion', 'fun', 'wasu',
		'pptv', 'tudou', 'baofeng', 'pps', 'letv', 'm1905', 'qq', 'cntv', 'sohu',
		'iqiyi', 'kumi', 'youku', '56', '61', 'hunantv'
	]
	
	out = list()
	df = set()
	for o in online:
		
		try:
			o = urlparse.parse_qs(urlparse.urlparse(o).query)['url'][0]
		except KeyError:
			pass
		
		netloc = urlparse.urlparse(o).netloc
		for d in domain:
			if d in netloc:
				name = table[d]['name']
				logo = table[d]['logo']
				break
		else:
			print o
			raise
		
		if o not in df:
			df.add(o)
			out.append({'name':name, 'logo':logo, 'link':o})
	
	return out

def format_netdisk_resource(netdisk):
	table = {
		'letv':{'name':u'乐视云盘', 'logo':''},
		'baidu':{'name':u'百度云', 'logo':''},
		'115':{'name':u'115礼包', 'logo':''},
		'qq':{'name':u'QQ旋风', 'logo':''},
		'xunlei':{'name':u'迅雷快传', 'logo':''},
	}
	
	domain = ['letv', 'baidu', '115', 'xunlei']
	
	out = list()
	df = set()
	for net in netdisk:
		netloc = urlparse.urlparse(net['link']).netloc
		for d in domain:
			if d in netloc:
				name = table[d]['name']
				logo = table[d]['logo']
				break
		else:
			raise ValueError(net)
		
		if net['link'] not in df:
			df.add(net['link'])
			out.append({'name':name, 'logo':logo, 'link':net['link'], 'code':net['code']})
	
	return out

def atom_magnet(magnet):
    df = set()
    out = list()
    
    for m in magnet:
        try:
            urn = re.findall(ur'xt=urn:btih:(\w+)', m['link'])[0].lower()
            if urn not in df:
                df.add(urn)
                out.append(m)
        except IndexError:
            out.append(m) # just use it resource, not filter it
            continue
    
    return out

def atom_ed2k(ed2k):
    df = set()
    out = list()
    
    for e in ed2k:
        if e['link'].split('|')[4].lower() not in df:
            df.add(e['link'])
            out.append(e)
    
    return out

def atom_http(http):
    df = set()
    out = list()
    
    for h in http:
        if h['link'] not in df:
            df.add(h['link'])
            out.append(h)
        
    return out

def atom_download_resource(downloads):	
	other = list()
	ed2k = list()
	magnet = list()
	fail = list()
	
	for d in downloads:
		try:
			scheme = urlparse.urlparse(d['link']).scheme
			if scheme == 'magnet':
				magnet.append(d)
			elif scheme == 'ed2k':
				ed2k.append(d)
			else:
				other.append(d)
		except:
			fail.append(other)
	
	try:
		magnet = atom_magnet(magnet)
		ed2k = atom_ed2k(ed2k)
		other = atom_http(other)
	except:
		return downloads
	
	resources = magnet + ed2k + other
	
	for r in resources:
		if r['quality'] == "unknow":
			r['quality'] = "DVD"
	
	return resources

if __name__ == '__main__':
    print format_thunder(u'thunder://QUFmdHA6Ly93d3c6cGlhb2h1YS5jb21AZHkxMjUucGlhb2h1YS5jb206MTEzMjMvJUU5JUEzJTk4JUU4JThBJUIxJUU3JTk0JUI1JUU1JUJEJUIxcGlhb2h1YS5jb20lRTUlQjglOTUlRTYlQjQlOUIlRTclOEUlOUIlRTQlQjklOEIlRTYlOTclODVCRDEyODAlRTklQUIlOTglRTYlQjglODUlRTQlQjglQUQlRTglOEIlQjElRTUlOEYlOEMlRTUlQUQlOTcucm12Ylpa')
