#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
import os
import json
from disabler import cut, ratio, better, worse_filter, area, genre, quality_block, rule_filter
import urlparse
import string
from pcnile import langconv
from pcnile.langconv import Converter
from django.utils.encoding import force_unicode
import pymongo
from bson import ObjectId
import argparse

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

downloadwords = [ u"720P下载", u"720下载", u"1080P下载", u"1080下载", u"高清下载", u"迅雷下载", u'BT下载', u'3D下载', u"下载" ]

torrentwords = [ u"BT种子", u"电影BT种子", u"电影种子", u"免费电影种子", u"最新电影种子", u"最新BT种子", u'免费电影BT种子', u'高清种子', u'快播种子' ]

append = [u'加长版', u'重压', u'3D版', u'全集', u'完整版', u'未剪辑版'] + downloadwords + torrentwords

conv = Converter('zh-hans')
re_han = re.compile(ur"([\u4E00-\u9FA5a-zA-Z0-9+#&\-:·]+)", re.U)
re_split = re.compile(ur'[^《》」「】【\[\]\)\(/\+_ ]+', re.U)
re_size = re.compile(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?(g|G|m|M|mb|Mb|MB|Mb)')
re_num = re.compile(ur"(^\d{2}\-\d{2}$)|(^[0-9.]+$)")
re_eng = re.compile(ur'[a-zA-Z0-9+#&\.\-_:]+$')
re_end = re.compile(ur'(%s)$' % "|".join(append))
re_title = re.compile(ur"[\u4E00-\u9FA5a-zA-Z0-9+#&\-:·]+[\u4E00-\u9FA5]?(|(i|ii|iii|iv)|\d{1, 4})")

re_date = re.compile(r'(^\[\d+\-\d+\])|(^\[\d+\.\d+\])')

pre_area = "|".join(area)
re_country = re.compile(ur"^\[(((%s)/(%s)/(%s)/(%s))|((%s)/(%s)/(%s))|((%s)/(%s))|(%s))\]" %
    (pre_area, pre_area, pre_area, pre_area, pre_area, pre_area, pre_area, pre_area, pre_area, pre_area))

pre_genre = "|".join(genre)
re_genre = re.compile(ur"^\[(((%s)/(%s)/(%s)/(%s))|((%s)/(%s)/(%s))|((%s)/(%s))|(%s))\]" %
    (pre_genre, pre_genre, pre_genre, pre_genre, pre_genre, pre_genre, pre_genre, pre_genre, pre_genre, pre_genre))

def fast_title(rawtitle):
    rawtitle = rawtitle.replace(u'【', u'[').replace(u'】', u']')
    title = conv.convert(uniform(rawtitle)).strip()
    title = re_date.sub('', title).strip()
    title = re_country.sub('', title).strip()
    title = re_genre.sub('', title).strip()
    
    return title

def format_title(rawtitle):
    blocks = list()
    #title = fast_title(rawtitle)
    #for b in re_split.findall(title):
    title = " ".join(rawtitle)
    for b in rawtitle:
        block = b.strip()
        if block and not worse_filter( block ):
            blocks.append(block)
    
    block_size = len(blocks)
    if block_size == 0:
        print 'zero block size in %s' % rawtitle
    elif block_size == 1:
        title = blocks[0]
    else:
        words = list()
        for block in blocks:
            if not re_num.match(block) and not re_size.match(block):
                words.append(block)
        
        word_size = len(words)
        if word_size == 0:
            title = " ".join(blocks)
        elif word_size == 1:
            title = words[0]
        else:
            result = [{'w':w, 'r':ratio(w)} for w in words]
            result = [ r for r in sorted(result, key=lambda w : w['r'])[:2] ]
            if len(result) == 1:
                title = result[0]['w']
            else:
                if result[1]['r'] < 0.2:
                    title = " ".join([r['w'] for r in result])
                else:
                    title = result[0]['w']
    
    if not re_eng.match(title):
        for t in title.split('.'):
            if t.strip():
                title = t
                break
    
    title = re_end.sub('', title.upper())
    
    try:
        return re_title.match(title).group()
    except AttributeError:
        return title

re_num = re.compile(ur"(^\d{1,2}\-\d{1,2}$)|(^\d{1,2}\.\d{1,2}$)|(^\d+mb$)|(^\d+m$)")
stopwords = [s for s in string.punctuation] + [ ']', '[', u'—', u'“', u'”', u'·', u'·' ]
def word_block(word):
    word = word.strip()
    if word == "":
        return True
    elif re_num.match(word):
        return True
    elif word in stopwords:
        return True
    else:
        return False

with codecs.open('tf.json', 'rb', 'utf-8') as f:
    tf = json.load(f)

def cal_tf_block(words):
    tf_count = 0.0
    for w in words:
        try:
            tf_count += tf[w]
        except KeyError:
            pass
    
    return tf_count

"""
parts = ''
max_tf = 0.0
for t in titles:
    tf_value = cal_tf_block([w for w in cut(t) if not word_block(w)])
    if tf_value > max_tf:
        parts = t
        max_tf = tf_value

f.write("%s %f %s\n" % (parts, max_tf, title))
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", type=str)
    parser.add_argument("-l", "--level", type=int, default=-1)
    args = parser.parse_args()
    
    if args.target == 'l':
        goods = list()
        with codecs.open('title.txt', 'rb', 'utf-8') as f:
            for l in f:
                l = l.split('|')
                goods.append({'_id':ObjectId(l[0].strip()), 'title':l[1].strip()})
        
        look = [g['title'] for g in goods]
        with codecs.open('look.txt', 'wb', 'utf-8') as f:
            f.write("\n".join( look ))
    
    elif args.target == 'rl':
        db = pymongo.Connection().scrapy
        
        goods = list()
        with codecs.open('title.txt', 'rb', 'utf-8') as f:
            for l in f:
                l = l.split('|')
                goods.append({'_id':ObjectId(l[0].rstrip().lstrip()), 'title':l[1].rstrip().lstrip()})
        
        for g in goods:
            try:
                m = db.scrapy.find_one({'_id':g['_id']})
                if g['title']:
                    m['old_title'] = m['title']
                    m['title'] = g['title']
                    db.scrapy.save(m)
            except:
                pass
    
    elif args.target == 'rd':
        db = pymongo.Connection().scrapy
        
        goods = []
        if args.level == -1:
            items = db.scrapy.find()
        else:
            items = db.scrapy.find({'level':args.level})
        
        for d in items:
            d['maybe'] = format_title(d['title'])
            goods.append(d)
        
        with codecs.open('title.txt', 'wb', 'utf-8') as f:
            f.write("\n".join( ["%s | %s | %s" % (str(g['_id']), g['maybe'], g['title']) for g in goods] ))
    
    elif args.target == 'd':        
        db = pymongo.Connection().scrapy
        with codecs.open('title.txt', 'wb', 'utf-8') as f:
            if args.level == -1:
                # f.write("\n".join( [d['title']for d in db.scrapy.find()] ))
                for d in db.scrapy.find():
                    title = d['title'].replace(u'【', u'[').replace(u'】', u']')
                    title = re.sub(ur" +\[|\] +", '', title.strip()) # 去除[]前后的空格
                    title = uniform(title)
                    if re.findall(ur"国家地理|合集|bbc", title):
                        continue
                    
                    #try:
                    titles = re.findall("\[(.+?)\]", title)
                    if re.sub(ur"\[|\]", '', title) == "".join(titles):
                        #titles = [t for t in titles if not worse_filter(t)]
                        # parts = ['/'.join([w for w in cut(t) if not word_block(w)]) for t in titles]
                        processed = [ t for t in titles if not quality_block(t) and not rule_filter(t)]
                        #rule_filter(processed)
                        processed = " / ".join(processed)
                        f.write("%s %s\n" % (processed, ''))
                    #except:
                    #    pass
            else:
                f.write("\n".join( [d['title']for d in db.scrapy.find({'level':args.level})] ))

    elif args.target == 'fd':
        db = pymongo.Connection().scrapy
        with codecs.open('title.txt', 'wb', 'utf-8') as f:
            if args.level == -1:
                f.write("\n".join( [fast_title(d['title']) for d in db.scrapy.find()] ))
            else:
                f.write("\n".join( [fast_title(d['title']) for d in db.scrapy.find({'level':args.level})] ))
    
    elif args.target == 'rollback':
        db = pymongo.Connection().scrapy
        for d in db.scrapy.find():
            try:
                d['title'] = d['old_title']
                del d['old_title']
                db.scrapy.save(d)
            except KeyError:
                pass
