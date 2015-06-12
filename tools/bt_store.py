#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import json
import codecs
import random
import pymongo
import sqlite3
import libtorrent
import chardet
import datetime
from pony.orm import *
from django.utils.encoding import force_unicode, DjangoUnicodeDecodeError

re_urn = re.compile(ur'xt=urn:btih:(\w+)')
re_pass = re.compile(r'^_____padding_file')
re_file_name = re.compile(r"[\/\\\:\*\?\"\<\>\|]")

prefix = ["[www.obtainfo.com]", "www.obtainfo.com_"]

db = Database('sqlite', 'obtainfo.sqlite', create_db=True)

class Torrent(db.Entity):
	id = PrimaryKey(str, 40)
	upload = Required(bool, default=False, index=True)
	netdisk = Required(bool, default=False, index=True)
	torrent = Required(buffer, lazy=True)

db.generate_mapping(create_tables=True)

is_exist_urn = lambda urn : db.exists("* from Torrent where id = $urn")

def unicode_name(name):
	for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1', 'big5']:
		try:
			return force_unicode(name, encoding)
		except DjangoUnicodeDecodeError:
			continue
	else:
		try:
			return force_unicode(name, chardet.detect(name)['encoding'])
		except DjangoUnicodeDecodeError:
			raise

@db_session
def save_torrent_to_db(urn, blob):
	torrent = Torrent(id=urn, torrent=blob)
	commit()

# check torrent file for get urn
def check_torrent(content):
	try:
		metadata = libtorrent.bdecode(content)
		info = libtorrent.torrent_info(metadata)
		urn = str(info.info_hash()).lower()
		return urn
	except:
		return None

# content is torrent raw bin data, 校验是否已经存在
@db_session
def save_torrent(content):
    urn = check_torrent(content)
    if urn:
        if not is_exist_urn(urn):
            save_torrent_to_db(urn, sqlite3.Binary(content))
        else:
            print 'dumplate urn %s' % urn
        return True
    else:
        print 'check urn %s fail' % urn
        return False

@db_session
def get_server_magnet(num=5000):
    server = pymongo.Connection().server
    
    count = 0
    urns = list()
    magnets = list()
    max_urns = 0
    df = set(db.select("id from Torrent"))

    for d in server.server.find():
        for m in d['resource']['download']:
            try:
                urn = re.findall(ur'xt=urn:btih:(\w+)', m['link'])[0].lower()
                if len(urn) > max_urns:
                    max_urns = len(urn)
                
                if urn not in df:
                    magnets.append(m['link'])
                    urns.append(urn)
                    
                    count += 1
                    if count >= num:
                        print max_urns
                        return (magnets, urns)
            except IndexError:
                pass
    
    print max_urns
    return (magnets, urns)

# rules = ['full', 'upload', 'netdisk']
@db_session
def dump_urn(where, rule='upload', status=False, update=False, num=1000):
	torrents = select(t.id for t in Torrent)
	urn = [t.lower() for t in torrents]
	with codecs.open(os.path.join(where, 'urn.json'), 'wb', 'utf-8') as f:
		json.dump(urn, f)

@db_session
def dump_torrent(where, rule='upload', status=False, update=False, num=1000):
    if rule == 'upload':
        torrents = Torrent.select(lambda t: t.upload == status)
    elif rule == 'netdisk':
        torrents = Torrent.select(lambda t: t.netdisk == status)
    else:
        torrents = select(t for t in Torrent)
    
    if num != -1:
        torrents = torrents[ : num]
    
    for t in torrents:
        src = os.path.join(where, t.id[:2], "%s.torrent" % t.id)
        if not os.path.exists(os.path.join(where, t.id[:2])):
            os.mkdir(os.path.join(where, t.id[:2]))
        with open(src, 'wb') as f:
            bin_data = t.torrent
            if bin_data:
                f.write(bin_data)
            else:
                f.write(t.torrent)
        if update == True:
            if rule == 'upload':
                t.set(upload = not status)
            elif rule == 'netdisk':
                t.set(netdisk = not status)

# 从外部文件夹加载种子文件到数据库中
def load_torrent(directory):
	for name in os.listdir(directory):
		src = os.path.join(directory, name)
		
		if os.path.isdir(src):
			load_torrent(src)
		else:
			with open(src, 'rb') as source:
				content = source.read()
				save_torrent(content)

def rename_torrent(directory, newfolder=None):
	for name in os.listdir(directory):
		src = os.path.join(directory, name)
		
		with open(src, 'rb') as source:
			meta = libtorrent.bdecode(source.read())
			try:
				torrent_name = unicode_name(meta['info']['name'])
			except:
				continue
		
		if not newfolder:
			new = os.path.join(directory, re_file_name.sub('', torrent_name) + '.torrent' )
		else:
			new = os.path.join(newfolder, re_file_name.sub('', torrent_name) + '.torrent' )
		
		os.rename(src, new)

@db_session
def stats_torrent(rule='upload', status=False):
	if rule == 'upload':
		return select(t for t in Torrent if t.upload == status).count()
	elif rule == 'netdisk':
		return select(t for t in Torrent if t.netdisk == status).count()
	else:
		return select(t for t in Torrent).count()