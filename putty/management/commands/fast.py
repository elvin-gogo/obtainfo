#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
import urlparse
import json
import string
import datetime

from django.conf import settings
from django.utils.encoding import force_unicode
from django.core.management.base import BaseCommand, CommandError
from obtainfo.sync import Client
from pcnile.resource import atom_download_resource
from obtainfo.search import Search

import pymongo
import jieba
from bson import ObjectId

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False

def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar<=u'\u0039':
        return True
    else:
        return False

def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False

def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False

def B2Q(uchar):
    """半角转全角"""
    inside_code=ord(uchar)
    if inside_code<0x0020 or inside_code>0x7e: #不是半角字符就返回原来的字符
        return uchar
    if inside_code==0x0020: #除了空格其他的全角半角的公式为:半角=全角-0xfee0
        inside_code=0x3000
    else:
        inside_code+=0xfee0
    return unichr(inside_code)

def Q2B(uchar):
    """全角转半角"""
    inside_code=ord(uchar)
    if inside_code==0x3000:
        inside_code=0x0020
    else:
        inside_code-=0xfee0
    if inside_code<0x0020 or inside_code>0x7e: #转完之后不是半角字符返回原来的字符
        return uchar
    return unichr(inside_code)

def stringQ2B(ustring):
    """把字符串全角转半角"""
    return "".join([Q2B(uchar) for uchar in ustring])

def uniform(ustring):
    """格式化字符串，完成全角转半角，大写转小写的工作"""
    return stringQ2B(ustring).lower()

RE_PUNCTUATION = re.compile(u'[^· %s]+' % string.punctuation)

# check whether content in desc
def inside(content, desc):
    content = list(set(content + RE_PUNCTUATION.findall( uniform( " ".join(content) ) )))
    content = [uniform(c) for c in content]
    
    match_num = 0
    for c in content:
        if c in desc:
            match_num += 1
    
    return match_num

search = Search(settings)

class Command(BaseCommand):
    def get_matched_item(self, db, title, r):
        matches = [ m for m in db.server.find( {'$or':[{'title':title}, {'aka':title} ]} ) ]
        
        if len(matches) == 0:
            matches = search.query(title)
        
        if len(matches) > 50:
            self.stdout.write( 'current is %d, title %s, oid %s' % (len(matches), title, str(r['_id'])) )
            return None
            
        if len(matches):
            repeat = 0
            matched = list()
            for m in matches:
                names = m['director'] + m['writer'] + m['actor']
                area = m['area']
                imdb = m['imdb']
                try:
                    year = int(m['year'])
                    years = [str(year-1), str(year), str(year+1)]
                except:
                    years = []
                
                if imdb in r['desc']: # good
                    repeat += 1
                    return m
                else:                    
                    desc = r['title'] + '\n' + r['desc'] + '\n' + '\n'.join([n['name'] for n in r['resource']])                    
                    desc = uniform(desc)
                    
                    match_name = inside(names, desc)
                    match_year = inside(years, desc)
                    match_area = inside(area, desc)
                    
                    # must match name level
                    if match_name and match_year and match_area:
                        repeat += 1
                        matched.append({'r':m, 'n':match_name, 'y':match_year, 'a':match_area})
                    elif match_name and match_year:
                        repeat += 1
                        matched.append({'r':m, 'n':match_name, 'y':match_year, 'a':match_area})
                    elif match_name and match_area:
                        repeat += 1
                        matched.append({'r':m, 'n':match_name, 'y':match_year, 'a':match_area})
                    
            if repeat == 1:
                return matched[0]['r']
            elif repeat > 1:
                good = max(matched, key=lambda m : m['n'])
                if good['y'] or good['a']:
                    return good['r']
        return None
    
    def match_system_record(self, level=-1):
        db = pymongo.Connection().server
        cdb = pymongo.Connection().scrapy
        
        if level == -1:    
            rs = [r for r in cdb.scrapy.find({"$and":[{'track':'scrapy'}, {'level':{"$ne":999}}]})]
        else:
            rs = [r for r in cdb.scrapy.find({'level':level})]
        
        record = list()
        for r in rs:
            m = self.get_matched_item(db, r['title'], r)
            matched = m
            if m:
                self.stdout.write('matched %s' % str(m['_id']))
                source = r['title'] + ' | ' + matched['title'] + ' | ' + "\\".join(matched['aka'] + matched['area']) 
                target = str(matched['_id']) + ' | ' + r['source']
                record.append(source + '\t' + target)
        
        with codecs.open('record.txt', 'wb', 'utf-8') as f:
            f.write('\n'.join(record))
        
    def match_system(self, level=-1):
        db = pymongo.Connection().server
        cdb = pymongo.Connection().scrapy
        
        if level == -1:    
            rs = [r for r in cdb.scrapy.find({"$and":[{'track':'scrapy'}, {'level':{"$ne":999}}]})]
        else:
            rs = [r for r in cdb.scrapy.find({'level':level})]
        
        update = list()
        for r in rs:
            try:
                m = self.get_matched_item(db, r['title'], r)
            except TypeError:
                print r['_id']
                raise
            
            if m:
                self.stdout.write('matched %s' % str(m['_id']))
                m = db.server.find_one({'_id':m['_id']})
                m['resource']['download'] = atom_download_resource(r['resource'] + m['resource']['download'])
                m['samesite'] = list(set(m['samesite'] + r['source']))
                db.server.save(m)
                cdb.scrapy.remove({'_id': r['_id']})
                
                update.append( {'_id':str(m['_id']), 'resource':m['resource'], 'samesite':m['samesite']} )
        
        with codecs.open('resource.json', 'wb', 'utf-8') as f:
            json.dump(update, f)
    
    def handle(self, level=-1, *args, **options):
        timestamp = datetime.datetime.now()
        
        level = int(level)
        
        self.stdout.write('start match system for level %d' % level )
        
        self.match_system(level)
        
        self.stdout.write('Successfully update server item use time "%s"' % str((datetime.datetime.now() - timestamp)) )
