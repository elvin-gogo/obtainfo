#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
import urlparse
import pymongo
from bson import ObjectId
import sqlite3
import urllib
import urllib2
from collections import OrderedDict
import cookielib
import mechanize
import uuid
import time
import random
import sys
import json

class DoubanBrowser(object):
    def __init__(self, email='pczhaoyun@gmail.com', password='zhy1991223'):
        
        br = mechanize.Browser()
        cj = cookielib.CookieJar()
        br.set_cookiejar(cj)
        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        
        br.addheaders = [
                            ('User-agent', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'),
                            ('Accept', "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
                        ]
            
        self.br = br
        self.cj = cj
        self.url = 'http://www.douban.com/accounts/login'
        
        self.data = {
            "form_email":email,
            "form_password":password,
            "source":"index_nav"
        }
        
        self.response = self.br.open(self.url, urllib.urlencode(self.data))
    
    def login_douban(self):
        success = False
        
        if self.response.geturl() == self.url:
            html = self.response.read()
            
            regex = re.compile(r'<img id="captcha_image" src="(.+?)" alt="captcha" class="captcha_image"/>')
            imgurl = regex.findall(html)
            res = urllib.urlretrieve(imgurl[0], 'gg.jpg')
            
            captcha = re.search('<input type="hidden" name="captcha-id" value="(.+?)"/>' ,html)
            if captcha: # 验证码验证
                vcode = raw_input(u'please input captcha from gg.jpg : ')
                self.data["captcha-solution"] = vcode
                self.data["captcha-id"] = captcha.group(1)
                self.data["user_login"] = "登录"
                self.response = self.br.open(self.url, urllib.urlencode(self.data))
                
                if urlparse.urljoin(self.response.geturl(), '/') == "http://www.douban.com/":
                    success = True
            else: # 不需要输入验证码
                success = True
        else:
            print 'login first step fail ' + self.response.geturl()
        
        if success:
            success = False
            for c in self.cj:
                if c.name == 'ck':
                    success = True
                    self.ck = str(c.value)
                    print 'ck = ' + self.ck
                    break
        
        return success

"""
sid:1300282
comment:http://www.obtainfo.com/detail/5379ce9d3faf8617f19cafec/
sync_to_mb:
ck:QL-U
"""
def add_doulist(br, doulist, item, comment, ck="QL-U"):
    did = doulist.rstrip('/').split('/')[-1]
    sid = item.rstrip('/').split('/')[-1]
    
    post_url = "http://movie.douban.com/j/doulist/%s/additem" % did
    post_data = urllib.urlencode({'sid' : sid}) + '&' + urllib.urlencode({'comment' : comment}) + '&sync_to_mb=&ck=aO4a'
    
    response = br.open(post_url, post_data).read()
    
    js = json.loads(response)
    if js['err'] == '' and js['r'] == 0:
        return True
    else:
        return False

# input selection id and doulist url
if __name__ == '__main__':
    try:
        sid = ObjectId(sys.argv[1])
        doulist = sys.argv[2]
    except IndexError:
        sys.exit()
    
    douban = DoubanBrowser()
    if douban.login_douban():
        db = pymongo.Connection().server
        selection = db.selection.find_one({'_id':sid})
        for l in selection['list']:
            try:
                m = db.server.find_one({'_id':ObjectId(l)})
            except:
                continue
            
            murl = "http://movie.douban.com/subject/%s/" % m['douban']['id']
            ourl = "http://www.obtainfo.com/detail/%s/" % str(m['_id'])
            if add_doulist(douban.br, doulist, murl, ourl, douban.ck):
                print ourl + '\t add success'
                time.sleep(random.randint(3, 8))
            else:
                print 'add_doulist fail'
                break
        else:
            print 'success add doulist full'
    else:
        print 'login fail'

    