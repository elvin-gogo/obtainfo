#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import time
import json
import codecs
import urllib
import random
import pymongo
import urllib2
import urlparse
import argparse
import StringIO
import threading
from lxml import etree
from multiprocessing.pool import ThreadPool
from pcnile.resource import format_online_resource, online_table

myear = [a.encode('utf-8') for a in [u'2005之前', u'2014',u'2013',u'2012',u'2011',u'2010',u'2009',u'2008',u'2007',u'2006', u'2005',]]

reqest_url_base = "http://v.hao123.com/commonapi/tvplay2level/"
qs_year = "?callback=spider&filter=false&type=&area=&actor=&start={0}&complete=%E6%AD%A3%E7%89%87&order=hot&pn={1}&rating=&prop=&_=1392884120245"

def get_raw_page(url, timeout=30):
    try:
        return urllib2.urlopen(url, timeout=timeout).read()
    except:
        return None

def get_json(url, timeout=30, default=None):
    raw_page = get_raw_page(url, timeout)
    if raw_page:
        try:
            return json.loads(re.findall(r"\((.+)\)", raw_page)[0])
        except:
            pass
        
    return default

def get_movie_item(url):
    js = get_json(url)
    for j in js['videoshow']['videos']:
        if j['id'] not in df:
            df.add(j['id'])
            all.append(j)

def bulid_id_map():
    urls = list()
    peer_max_film = 2000
    
    for year in myear:
        js = get_json(reqest_url_base + qs_year.format(year, 1))
        if js:
            total_num = int(js["total_num"])
            if total_num == 0:
                continue
        else:
            print 'get json fail'
            continue
        
        if total_num > peer_max_film:
            print total_num
            total_num = peer_max_film
        
        urls += [reqest_url_base + qs_year.format(year, i) for i in range(1, (total_num + 18 - 1) // 18)]
    
    return urls

def first_stage_handler(url):
    js = get_json(url, default=[])
    if js:
        return js['videoshow']['videos']
    else:
        print 'lost url %s' % url
        return []

def first_stage(urls, df=[]):
    pool = ThreadPool(10)
    items = pool.map(first_stage_handler, urls)
    pool.close()
    pool.join()
    
    a = list()
    for item in items:
        a += [{
            'id':i['id'], 'title':i['title'], 'intro':i['intro'],
            'actor':[d['name'] for d in i['actor']],
            'area':[d['name'] for d in i['area']], 'date':i['date'],
            'finish':i['finish'],
            'fresh':True,}
        for i in item]
    
    if df:
        return [i for i in a if i['id'] not in df]
    else:
        return a

def get_real_link(url, check_domain):
    try:
        ubody = get_raw_page(url)
        if ubody:
            tree = etree.fromstring(ubody, etree.HTMLParser(encoding='utf-8'))
            url = tree.xpath("//*[@id='link']/@href")[0]
            
            try:
                real = urlparse.parse_qs(urlparse.urlparse(url).query)['url'][0]
            except KeyError:
                real = url
            
            if check_domain in real:
                return real
    except:
        pass
    
    return ''

def full_site_scrapy(df=[]):
    db = pymongo.Connection().hao123
    items = first_stage(bulid_id_map(), df)
    for i in items:
        try:
            m = db.tv.find_one({'id':i['id']})
            i['_id'] = m['_id']
        except:
            pass
        
        db.tv.save(i)

def get_resource(hid):
    def get_resource_handler(site):
        need = len(site['episodes'])
        site_key = site['site_info']['site'].split('.')[0]
        info = online_table[site_key]
        
        resource = {'name':info['name'], 'logo':info['logo'], 'episode':[]}
        
        count = 0
        for episode in site['episodes']:
            times = 5
            while times:
                link = get_real_link(urlparse.urljoin(res_url, episode['url']), site['site_info']['site'])
                if link == '':
                    times -= 1
                    time.sleep(1)
                else:
                    count += 1
                    resource['episode'].append({'link':link, 'num': count})
                    break
            
            if times == 0:
                break
        
        if len(resource['episode']) == need:
            return resource
        else:
            print 'drop resource site %s' % site['site_info']['site']
            return dict()

    res_url = "http://v.hao123.com/dianshi_intro/?dtype=tvPlayUrl&e=1&service=json&id=%s&callback=spider"
    resource = get_json(res_url % hid, default=[])
    
    pool = ThreadPool( min([len(resource), 10]) )
    resource = pool.map(get_resource_handler, resource)
    pool.close()
    pool.join()
    
    #resource = [get_resource_handler(resource[0])]
    
    return [{'from':"http://v.hao123.com/dianshi/%s.htm" % hid, 'resource':[r for r in resource if r]}]

# 更新,全站更新
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", type=str)
    args = parser.parse_args()
    
    if args.target == 'update':
        db = pymongo.Connection().hao123
        ids = [d['id'] for d in db.tv.find({}, {'id':1})]
        print 'get exist id finished'
        full_site_scrapy(ids)
    elif args.target == 'initialize':
        full_site_scrapy()
        print 'get exist id finished'
        fix_resource()
        fix_resource()
    elif args.target == 'indb':
        indb()
    elif args.target == 'fix':
        db = pymongo.Connection().online
        
        for d in db.hao123.find():
            if 'resource' not in d:
                d['fresh'] = False
            else:
                d['fresh'] = True
            db.hao123.save(d)
