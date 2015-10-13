#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
import pymongo
import hashlib
import jieba
import argparse
import re
import json
from pcnile.resource import format_bt, atom_magnet

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", type=str,
                        help="load downloaded resource to server or dump magnet url from server")
    args = parser.parse_args()

    # load downloaded and process it to magnet structure, then load it back
    if args.target == 'l':
        with codecs.open('magnet.json', 'rb', 'utf-8') as f:
            js = json.load(f)

        count = 0
        db = pymongo.Connection().scrapy
        for d in db.scrapy.find():
            goods = list()
            news = list()
            for r in d['resource']:
                if not isinstance(r, dict):
                    try:
                        key = re.findall(ur'xt=urn:btih:(\w+)', r)[0].lower()
                        news.append(js[key])
                    except:
                        pass
                else:
                    goods.append(r)

            if len(news):
                count += 1
                d['resource'] = atom_magnet(goods + news)
                db.scrapy.save(d)

        print 'success merge resource %d' % count

    # process torrent to json structure
    elif args.target == 'p':
        urn = dict()
        for f in os.listdir('torrent'):
            try:
                with open(os.path.join('torrent', f), 'rb') as fil:
                    info = format_bt(fil)
                    key = re.findall(ur'xt=urn:btih:(\w+)', info['link'])[0].lower()
                    urn[key] = info
            except:
                pass

        with codecs.open('magnet.json', 'wb', 'utf-8') as f:
            json.dump(urn, f)

        print 'success process magnet count %d' % len(urn.keys())

    # dump magnet link from scrpay collection for outside download
    elif args.target == 'd':
        db = pymongo.Connection().scrapy

        magent = list()
        for d in db.scrapy.find():
            for r in d['resource']:
                if not isinstance(r, dict):
                    magent.append(r)

        print 'need to download %d' % len(magent)
        with codecs.open('magent.txt', 'wb', 'utf-8') as f:
            f.write("\n".join(magent))

    # clear magnet link resource
    elif args.target == 'c':
        db = pymongo.Connection().scrapy

        bads = list()
        for d in db.scrapy.find():
            goods = [r for r in d['resource'] if isinstance(r, dict)]
            if len(goods):
                d['resource'] = goods
                db.scrapy.save(d)
            else:
                bads.append(d['_id'])

        for b in bads:
            db.scrapy.remove({'_id': b})
