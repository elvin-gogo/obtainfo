#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import json
import argparse
import pymongo
import re
from pcnile.resource import atom_download_resource

"""
# 合并抓取数据库中的magnet
if __name__ == '__main__':
    db = pymongo.Connection().scrapy
    
    df = set()
    out = dict()
    
    count = 0
    alls = [d for d in db.scrapy.find()]
    for d in alls:
        d['resource'] = atom_download_resource(d['resource'])
        for m in d['resource']:
            try:
                urn = re.findall(ur'xt=urn:btih:(\w+)', m['link'])[0].lower()
                if urn not in df:
                    df.add(urn)
                    out[urn] = d
                else:
                    target = out[urn]
                    target['source'] = list(set( target['source'] + d['source'] ))
                    target['resource'] = atom_download_resource(target['resource'] + d['resource'])
                    
                    db.scrapy.remove({'_id':d['_id']})
                    db.scrapy.save(target)
                    count += 1
                    break
            except IndexError:
                pass
    
    print count
"""

"""
#全局数据库中清除抓取数据库中的数据
if __name__ == '__main__':
    con = pymongo.Connection()
    cdb = con.server
    db = con.scrapy
    
    df = set()
    for d in cdb.server.find():
        for m in d['resource']['download']:
            try:
                urn = re.findall(ur'xt=urn:btih:(\w+)', m['link'])[0].lower()
                if urn not in df:
                    df.add(urn)
            except IndexError:
                pass
    
    count = 0
    block = 0
    alls = [d for d in db.scrapy.find()]
    for d in alls:
        d['resource'] = atom_download_resource(d['resource'])
        resource = list()
        for m in d['resource']:
            try:
                urn = re.findall(ur'xt=urn:btih:(\w+)', m['link'])[0].lower()
                if urn not in df:
                    resource.append(m)
            except IndexError:
                resource.append(m)
        
        if len(resource) != len(d['resource']):
            d['resource'] = resource
            
            count += 1
            if len(resource) == 0:
                block += 1
                db.scrapy.remove({'_id':d['_id']})
                db.filter.insert({'source':d['source']})
            else:
                db.scrapy.save(d)
    
    print count, block
"""

"""
if __name__ == '__main__':
    con = pymongo.Connection()
    cdb = con.server
    db = con.scrapy
    
    df = set()
    out = dict()
    title = dict()
    for d in cdb.server.find():
        for m in d['resource']['download']:
            try:
                urn = re.findall(ur'xt=urn:btih:(\w+)', m['link'])[0].lower()
                if urn not in df:
                    df.add(urn)
                    title[urn] = m['name']
                    out[urn] = [d]
                else:
                    out[urn].append(d)
            except IndexError:
                pass
    
    show = list()
    for k,v in out.items():
        if len(v) > 1:
            show.append("%s %s" % (title[k], " / ".join([t['title'] for t in v])))
            
    with codecs.open('text.txt', 'wb', 'utf-8') as f:
        f.write('\n'.join(show))
"""

"""
if __name__ == '__main__':
    con = pymongo.Connection()
    cdb = con.server
    db = con.scrapy
    
    df = set()
    out = dict()
    title = dict()
    for d in cdb.server.find():
        did = d['douban']['id']
        if did:
            if did not in df:
                df.add(did)
                out[did] = [d]
            else:
                out[did].append(d)
    
    show = list()
    for k,v in out.items():
        if len(v) > 1:
            show.append("%s %s" % (k, " / ".join([t['title'] for t in v])))
            
    with codecs.open('text.txt', 'wb', 'utf-8') as f:
        f.write('\n'.join(show))
"""
