#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import json
import codecs
import string
import pymongo
import urlparse
import argparse
from bson import ObjectId
from bson.json_util import dumps, loads

stdpic = "http://img03.taobaocdn.com/imgextra/i3/495498642/T21.RuX5XXXXXXXXXX_!!495498642.jpg"
bigpic = "http://img02.taobaocdn.com/imgextra/i2/495498642/T2A7VqX0laXXXXXXXX_!!495498642.jpg"
filter_pic = [stdpic, bigpic]

def url_to_name(folder):
    names = set(os.listdir(folder))
    db = pymongo.Connection().server
    
    pics = list()
    for d in db.info.find():
        update = False
        if d['stdpic'].startswith('http') and d['stdpic'] not in filter_pic:
            fn = urlparse.urlparse(d['stdpic']).path.lstrip('/')
            if fn in names:
                d['stdpic'] = fn
                update = True
        
        if d['bigpic'].startswith('http') and d['bigpic'] not in filter_pic:
            fn = urlparse.urlparse(d['bigpic']).path.lstrip('/')
            if fn in names:
                d['bigpic'] = fn
                update = True
        
        if update:
            pics.append({'_id':d['_id'], 'stdpic':d['stdpic'], 'bigpic':d['bigpic']})
            
            db.info.save(d)
    
    with open('pics.json', 'wb') as f:
        f.write(dumps(pics))

def restore(folder):
    with open(os.path.join(folder, 'pics.json'), 'rb') as f:
        pics = loads(f.read())
    
    db = pymongo.Connection().server
    
    for p in pics:
        try:
            m = db.info.find_one({'_id':p['_id']})
        except:
            print 'get document fail'
            continue
        
        try:
            m['stdpic'] = p['stdpic']
            m['bigpic'] = p['bigpic']
        except TypeError:
            print 'type error', p['_id']
            continue
        
        db.info.save(m)
    
    print len(pics)

def look(folder):
    db = pymongo.Connection().server
    
    urls = list()
    for d in db.info.find():
        if d['stdpic'].startswith('http') and d['stdpic'] not in filter_pic:
            urls.append(d['stdpic'])
        if d['bigpic'].startswith('http') and d['bigpic'] not in filter_pic:
            urls.append(d['bigpic'])
    
    urls = list(set(urls))
    with open('pic.txt', 'wb') as f:
        f.write('\n'.join(urls))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", type=str)
    parser.add_argument("-f", "--folder", type=str, default="")
    args = parser.parse_args()
    
    if args.target == 'look':
        look(args.folder)
    elif args.target == 'process':
        url_to_name(args.folder)
    elif args.target == 'restore':
        restore(args.folder)
