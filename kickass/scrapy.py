#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urlparse
import random
import re, time, json, codecs, urllib, urllib2
import mechanize
import cookielib
import pymongo
import StringIO
from lxml import etree
from w3lib.encoding import html_to_unicode
from django.utils.encoding import force_unicode
from pcnile.resource import fast_resource_quality, quality_level
import smtplib, mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.Header import Header
from email.mime.image import MIMEImage
import logging

logging.basicConfig(filename='fast_scrapy.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

class Kickass(object):
    def __init__(self):

        br = mechanize.Browser()
        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)
        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.11) Gecko/20100701 Firefox/3.5.11')]
        self.br = br
        self.cj = cj
        self.start_urls = ["http://kickass.to/"] + ["http://kickass.to/movies/%d/?field=time_add&sorder=desc" % i for i in range(1, 11)]

        self.re_imdb = re.compile(r"http://www.imdb.com/title/(\w+)/?")

        db = pymongo.Connection().server
        self.fast = db.fast

    def notify(self, num):
        try:
            msg = MIMEMultipart()
            msg['From'] = "twenty_first@163.com"
            msg['To'] = '561424310@qq.com'
            msg['Subject'] = Header('最新抓取通知', charset='UTF-8')#中文主题

            txt = MIMEText("这次共有%d个新的资源" % num, _subtype='plain',  _charset='UTF-8')
            msg.attach(txt)

            smtp = smtplib.SMTP("smtp.163.com", timeout=30)
            smtp.login('twenty_first', 'Zhy1991223')
            smtp.sendmail("twenty_first@163.com", '561424310@qq.com', msg.as_string())
            smtp.quit()
        except:
            logging.error('send email to master fail')

    def get_tree(self, url, tub=False):
        try:
            page = self.br.open(url, timeout=60).read()
        except:
            logging.warn('get page from %s' % url)
            if tub == True:
                return (None,None)
            else:
                return None

        benc, ubody = html_to_unicode(page, page)

        time.sleep(random.randint(1, 3))

        if tub == True:
            return (etree.fromstring(ubody, etree.HTMLParser(encoding='utf-8')), ubody)
        else:
            return etree.fromstring(ubody, etree.HTMLParser(encoding='utf-8'))

    def filter(self, url):
        if self.fast.find({'resource.source':url}).count():
            return True
        else:
            return False

    def get_rss(self):
        url = 'http://kickass.to/movies/?rss=1'

        try:
            page = self.br.open(url, timeout=60).read()
        except:
            logging.warn('get page from %s' % url)
            return None

        time.sleep(random.randint(1, 3))

        return etree.fromstring(page, etree.XMLParser(encoding='utf-8'))

    def scrapy(self):
        items = list()
        for url in self.start_urls:
            try:
                tree = self.get_tree(url=url, tub=False)
                # need = tree.xpath('.//a[contains(text(), "Movies Torrents")]')[0].getparent().getparent()
                need = tree.xpath("//*[@class='firstr']")[0].getparent()

                for n in need.xpath('tr')[1:]:
                    try:
                        url = urlparse.urljoin(url, n.xpath("td/div[2]/a/@href")[0])
                        if not self.filter(url):
                            items.append(url)
                    except IndexError:
                        logging.warn("get item from url %s, maybe html structure changed" % url)
            except:
                logging.warn("get item from url %s" % url)

        try:
            tree = self.get_rss()
            for r in tree.findall('.//link')[1:]:
                try:
                    url = r.text
                    if not self.filter(url):
                        items.append(url)
                except:
                    logging.warn("get item from url %s, maybe html structure changed" % url)
        except:
            logging.warn("get item from url %s" % url)

        items = list(set(items))
        notify = [self.process(url) for url in items].count(True)
        if notify:
            self.notify(notify)

    """
    mongodb structure : movie title, quality level, imdb, resource{source, address, name}
    state choose(active, stop, process)
    """
    def process(self, url):
        tree, ubody = self.get_tree(url, True)

        if ubody == None:
            return False

        try:
            imdb = self.re_imdb.findall(ubody)[0]
        except IndexError:
            #logging.warn('get imdb none because IndexError %s' % url)
            imdb = ""
        except TypeError:
            #logging.warn('get imdb none because TypeError %s' % url)
            imdb = ""

        # get movie resource info
        try:
            name = tree.xpath("//*[@itemprop='name']")[0].text
        except:
            logging.warn('get movie name from %s' % url)
            return False

        try:
            address = tree.xpath("//*[@title='Download verified torrent file']/@href")[0]
        except IndexError:
            try:
                address = tree.xpath("//*[@title='Download torrent file']/@href")[0]
            except IndexError:
                logging.warn('get movie resource from %s' % url)
                return False

        level = quality_level(fast_resource_quality(name))

        # get movie title
        try:
            title = tree.xpath("//*[@class='block overauto botmarg0']/li[1]/a/span")[0].text
        except IndexError:
            title = name

        notify = False
        if imdb:
            try:
                old = self.fast.find_one({'imdb':imdb})
                if old['state'] == 'stop': # we just interest with new and hot movie
                    return False

                if level > old['level']:
                    notify = True

                old['title'] = title
                old['level'] = level
                old['resource'].append({'name':name, 'address':address, 'source':url, 'level':level})
                self.fast.save(old)
            except:
                notify = True
                new = {'title':title, 'level':level, 'imdb':imdb, 'resource':[{'name':name, 'address':address, 'source':url, 'level':level}], 'state':'active'}
                self.fast.save(new)
        else:
            notify = True
            new = {'title':title, 'level':level, 'imdb':imdb, 'resource':[{'name':name, 'address':address, 'source':url, 'level':level}], 'state':'active'}
            self.fast.save(new)

        return notify

if __name__ == '__main__':
    kick = Kickass()
    kick.scrapy()
