#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re, time, json, codecs, urllib, urllib2, codecs
import mechanize
import cookielib
from multiprocessing import Pool
from lxml import etree
import urlparse
import pymongo

# first fast check id is in our db
# genrate two txt, one for id not our db, one for rating list

db = pymongo.Connection().server
cdb = pymongo.Connection().scrapy


class browser(object):
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()

    def __init__(self):
        self.br.set_cookiejar(self.cj)
        self.br.set_handle_equiv(True)
        self.br.set_handle_gzip(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        #self.br.set_debug_http(True)
        self.br.addheaders = [('User-agent',
                               'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.11) Gecko/20100701 Firefox/3.5.11')]


def dumps(title, data):
    with codecs.open('%s.json' % title, 'wb', 'utf-8') as f:
        json.dump(data, f)

    with codecs.open('%s.txt' % title, 'wb', 'utf-8') as f:
        f.write('\n'.join(data))


if __name__ == '__main__':
    if not sys.argv[1:]:
        print "Usage: python douban_rating.py http://movie.douban.com/doulist/240962/\n"
        sys.exit(0)

    start = str(sys.argv[1])
    ids = list()
    while start:
        page = browser.br.open(start).read()
        tree = etree.fromstring(page, etree.HTMLParser())

        ids += [urlparse.urlparse(i).path.split('/')[-2] for i in tree.xpath("//*[@class='doulist_item']/td/a/@href")]

        try:
            start = tree.xpath("//*[@class='next']/link/@href")[0]
        except IndexError:
            start = None

    dids = []
    titles = []
    fetchs = []
    # ids = list(set(ids))
    for i in ids:
        try: # already exist in our db
            title = db.server.find({'douban.id': i}, {'title': 1})[0]['title']
            dids.append(i)
            titles.append(title)
        except IndexError:
            try:
                atemplate = u"http://api.douban.com/v2/movie/subject/%s"
                vtemplate = u"http://movie.douban.com/subject/%s/"
                js = json.loads(urllib2.urlopen(atemplate % i, timeout=30).read())
                title = js['title']

                titles.append(title)

                desc = " / ".join([title] + js['aka'] + js['genres'] + js['countries'] + [js['year']])
                desc += js['summary']

                todb = {'source': [vtemplate % i], 'title': i, 'desc': desc, 'resource': [], 'track': 'scrapy',
                        'level': 999}

                fetchs.append(todb)
            except:
                pass

    for i in fetchs:
        cdb.scrapy.insert(i)

    dumps('ranking', titles)
    # dumps('fetch', fetchs)
    dumps('dids', dids)
