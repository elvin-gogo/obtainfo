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
from pcnile.resource import format_online_resource

marea = [a.encode('utf-8') for a in [u'内地',u'美国',u'韩国',u'香港',u'日本',u'台湾',u'法国',u'英国',u'德国',u'泰国',u'印度',u'欧洲地区',u'东南亚地区',u'其他地区']]
myear = [a.encode('utf-8') for a in [u'2014',u'2013',u'2012',u'2011',u'2010',u'00年代',u'90年代',u'80年代']]

reqest_url_base = "http://v.hao123.com/commonapi/movie2level/"
qs_year = "?callback=spider&filter=true&type=&area=&actor=&start={0}&complete=%E6%AD%A3%E7%89%87&order=hot&pn={1}&rating=&prop=&_=1392884120245"
qs_year_area = "?callback=spider&filter=true&type=&area={0}&actor=&start={1}&complete=%E6%AD%A3%E7%89%87&order=hot&pn={2}&rating=&prop=&_=1392884120245"

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
            continue
        
        if total_num > peer_max_film:
            for area in marea:
                js = get_json(reqest_url_base + qs_year_area.format(area, year, 1))
                if js:
                    total_num = int(js["total_num"])
                    if total_num == 0:
                        continue
                else:
                    continue
                
                if total_num > peer_max_film:
                    total_num = peer_max_film
                
                urls += [reqest_url_base + qs_year_area.format(area, year, i) for i in range(1, (total_num + 18 - 1) // 18)]
        else:
            urls += [reqest_url_base + qs_year.format(year, i) for i in range(1, (total_num + 18 - 1) // 18)]
    
    return urls

def first_stage_handler(url):
    js = get_json(url, default=[])
    if js:
        return js['videoshow']['videos']
    else:
        return []

def first_stage(urls, df=[]):
    pool = ThreadPool(10)
    items = pool.map(first_stage_handler, urls)
    pool.close()
    pool.join()
    
    a = list()
    for item in items:
        a += [{
            'id':i['id'], 'title':i['title'], 'intro':i['intro'], 'date':i['date'],
            'director':[d['name'] for d in i['director']], 'actor':[d['name'] for d in i['actor']],
            'area':[d['name'] for d in i['area']], 'fresh':True}
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

def get_doc(item):
    # 豆瓣ID
    try:
        template = "http://v.hao123.com/dianying/%s.htm"
        item['douban'] = re.findall("douban_url: \'(\S+)\',", get_raw_page(template % item['id']))[0].split('/')[-2]
    except:
        item['douban'] = ""
    
    if item['douban']:
        rev_url = "http://v.hao123.com/movie_intro/?dtype=commentCombine&service=json&id=%s&callback=spider"
        try:
            data = re.findall(r"\((.+)\)", get_raw_page(rev_url % item['id']))[0]
            item['comment'] = json.loads(data)
        except:
            item['comment'] = []
        
        res_url = "http://v.hao123.com/dianying_intro/?dtype=playUrl&e=1&service=json&id=%s&callback=spider"
        item['resource'] = get_json(res_url % item['id'], default=[])
        for i in item['resource']:
            i['real'] = get_real_link(urlparse.urljoin(res_url, i['link']), i['site'])
        
        return item
    
def second_stage(items):
    df = set()
    atom_items = list()
    for i in items:
        if i['id'] not in df:
            df.add(i['id'])
            atom_items.append(i)
    
    pool = ThreadPool(20)
    items = pool.map(get_doc, atom_items)
    pool.close()
    pool.join()
    
    return items

def full_site_scrapy(df=[]):
    db = pymongo.Connection().online
    items = second_stage( first_stage(bulid_id_map(), df) )
    for i in items:
        if isinstance(i, dict) and i['douban'] != '':
            try:
                m = db.hao123.find_one({'id':i['id']})
                i['_id'] = m['_id']
            except:
                pass
            
            db.hao123.save(i)

def fix_resource():
    count = 0
    db = pymongo.Connection().online
    for item in db.hao123.find():
        fix = False
        if len(item['resource']) == 0:
            res_url = "http://v.hao123.com/dianying_intro/?dtype=playUrl&e=1&service=json&id=%s&callback=spider"
            item['resource'] = get_json(res_url % item['id'], default=[])
            for i in item['resource']:
                i['real'] = get_real_link(urlparse.urljoin(res_url, i['link']), i['site'])
                fix = True
        
        for i in item['resource']:
            if i['real'] == '':
                print item['title'], item['id']
                i['real'] = get_real_link(urlparse.urljoin(res_url, i['link']), i['site'])
                fix = True
        
        if fix:
            count += 1
            db.hao123.save(item)
            
    print 'fix count %d' % count

def indb():
    template = "http://v.hao123.com/dianying/%s.htm"
    odb = pymongo.Connection().online
    sdb = pymongo.Connection().server
    
    count = 0
    for h in odb.hao123.find({'fresh':True}):
        try:
            m = sdb.server.find({'douban.id':h['douban']})[0]
        except:
            continue
        
        if m:
            m['samesite'] = list(set(m['samesite'] + [template % h['id']]))
            
            if not m['comment']:
                try:
                    if h['comment']['douban']['comments']:
                        m['comment'] = h['comment']['douban']['comments']
                except:
                    pass
            
            resource = [r for r in h['resource'] if r['real']]
            for r in resource:
                r['link'] = r['real']
            if resource:
                resource += m['resource']['online']
                resource = [ r['link'] for r in resource ]
                m['resource']['online'] = format_online_resource(resource, printf=True)
            
            count += 1
            
            sdb.server.save(m)
            
            h = {'_id':h['_id'], 'id':h['id'], 'douban':h['douban'], 'fresh':False}
            odb.hao123.save(h)
    
    print count

# 更新,全站更新
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", type=str)
    args = parser.parse_args()
    
    if args.target == 'update':
        db = pymongo.Connection().online
        ids = [d['id'] for d in db.hao123.find({}, {'id':1})]
        print 'get exist id finished'
        full_site_scrapy(ids)
        fix_resource()
        fix_resource()
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
