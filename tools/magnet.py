#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import json
import argparse
import pymongo
from bson import ObjectId
from pcnile.resource import atom_download_resource, format_online_resource, \
	format_netdisk_resource, format_bt, format_ed2k, format_thunder, \
	qualities_0, qualities_1, qualities_2, qualities_3, qualities_4, qualities_5

quality_CAM = qualities_0 + qualities_1 + qualities_2
quality_DVD = qualities_3
quality_HD = qualities_4 + qualities_5

def max_resource_level(resource):
	level = 0
	for d in resource:
		temp_level = 0
		
		if d['quality'] in quality_CAM:
			temp_level = 1
		elif d['quality'] in quality_DVD:
			temp_level = 2
		elif d['quality'] in quality_HD:
			return 3
		
		if temp_level > level:
			level = temp_level
	
	return level

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", type=str, help="load resource to server or dump resource from server")
    parser.add_argument("-f", "--file", type=str, help="file full path", default='')
    args = parser.parse_args()
    
    if args.target == 'l':
        db = pymongo.Connection().server
        with codecs.open(args.file, 'rb', 'utf-8') as f:
            js  = json.load(f)
        for j in js: # {"$set":{"track":"scrapy"}}
            db.server.update( {'_id':ObjectId(j['_id'])}, {'$set':{'resource':j['resource']}} )
        
    elif args.target == 'd':
        db = pymongo.Connection().server
        resources = [{'_id':str(d['_id']), 'resource':d['resource']} for d in db.server.find() ]
        with codecs.open(args.file, 'wb', 'utf-8') as f:
            json.dump(resources, f)
    
    elif args.target == 'n':
        db = pymongo.Connection().server
        links = list()
        for d in db.server.find():
            for r in d['resource']['download']:
                if r['name'] == '':
                    links.append(r['link'])
        
        with codecs.open(args.file, 'wb', 'utf-8') as f:
            f.write('\n'.join(links))
        
    elif args.target == 'np':
        db = pymongo.Connection().server
        for d in db.server.find():
            goods = list()
            save = False
            for r in d['resource']['download']:
                if r['name'] == '':
                    goods.append(format_thunder(r['link']))
                    save = True
                else:
                    goods.append(r)
            
            if save:
                d['resource']['download'] = goods
                db.server.save(d)
                
        db = pymongo.Connection().scrapy
        for d in db.scrapy.find():
            goods = list()
            save = False
            for r in d['resource']:
                if r['name'] == '':
                    goods.append(format_thunder(r['link']))
                    save = True
                else:
                    goods.append(r)
            
            if save:
                d['resource'] = goods
                db.scrapy.save(d)
    
    elif args.target == 'atom':
        db = pymongo.Connection().server
        count = 0
        for d in db.server.find():
            downloads = atom_download_resource(d['resource']['download'])
            if len(downloads) != len(d['resource']['download']):
                count += 1
                d['resource']['download'] = downloads
                db.server.save(d)
        print count
        
    elif args.target == 'rollback':
        db = pymongo.Connection().server
        dump_db = pymongo.Connection().dump
        
        netdisk = []
        count = 0
        for d in dump_db.server.find():
            if len(d['resource']['netdisk']):
                netdisk.append(d)
                count += 1
        
        print count
        
        for n in netdisk:
            m = db.server.find_one({'_id':n['_id']})
            if len(m['resource']['netdisk']) == 0:
                m['resource']['netdisk'] = n['resource']['netdisk']
                db.server.save(m)
        
    elif args.target == 'level':
        db = pymongo.Connection().server
        
        for d in db.server.find():
            level = [u'', u'尝鲜', u'普清', u'高清'][max_resource_level(d['resource']['download'])]
            d['resource']['level'] = level
            db.server.save(d)
