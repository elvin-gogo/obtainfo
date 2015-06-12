#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
import os
from disabler import cut, ratio, better, worse_filter
import urlparse
import string
from pcnile import langconv
from pcnile.langconv import Converter
from django.utils.encoding import force_unicode
import pymongo

def get_online():
    logo = list()
    name = list()
    netloc = list()
    
    db=pymongo.Connection().server
    
    for d in db.server.find():
        for o in d['resource']['online']:
            logo.append(o['logo'])
            name.append(o['name'])
            t = urlparse.urlparse(o['link']).netloc
            if t == 'video.baidu.com':
                print o
            netloc.append(t)
    
    logo=list(set(logo))
    name=list(set(name))
    netloc=list(set(netloc))
    
    with codecs.open('logo.txt', 'wb', 'utf-8') as f:
        f.write('\n'.join(logo))
       
    with codecs.open('name.txt', 'wb', 'utf-8') as f:
        f.write('\n'.join(name))

    with codecs.open('netloc.txt', 'wb', 'utf-8') as f:
        f.write('\n'.join(netloc))

def get_name():
    lists = list()
    with codecs.open('m.txt', 'rb') as f:
        for l in f:
            if l.rstrip().lstrip():
                lists.append(l)
    
    out = list()
    for l in lists:
        l = force_unicode(l)
        try:
            out.append( re.findall(ur"《(\S+)》", l)[0] )
        except IndexError:
            pass
    
    with codecs.open('out.txt', 'wb', 'utf-8') as f:
        f.write('\n'.join(out))

def merge_dict():
    words = list()
    df = set()
    for fil in os.listdir("D:\\obtainfo\\obtainfostatic\\dict\\"):
        with codecs.open(os.path.join("D:\\obtainfo\\obtainfostatic\\dict", fil), 'rb', 'utf-8') as f:
            for w in f:
                w = w.lstrip().rstrip()
                if w:
                    if w not in df:
                        df.add(w)
                        words.append(w)

    with codecs.open('words1.txt', 'wb', 'utf-8') as f:
        f.write("\n".join(words))

    words = list()
    df = set()    
    for fil in os.listdir("D:\\obtainfo\\obtainfostatic\\1\\tools\\dict\\"):
        print fil
        with codecs.open(os.path.join("D:\\obtainfo\\obtainfostatic\\1\\tools\\dict\\", fil), 'rb', 'utf-8') as f:
            for w in f:
                w = w.lstrip().rstrip()
                if w:
                    if w not in df:
                        df.add(w)
                        words.append(w)
    
    with codecs.open('words2.txt', 'wb', 'utf-8') as f:
        f.write("\n".join(words))

def make_jieba_dict():
    df = set()
    maybe = list()
    with codecs.open('words2.txt', 'rb', 'utf-8') as f:
        for l in f:
            w = l.strip().upper()
            if w and w not in df:
                df.add(w)
                maybe.append(w)
    maybe = sorted(maybe, reverse = True, key = lambda w : len(w) )
    dicts = [u"%s %d n" % ( m, len(m) * 100 ) for m in maybe]
    
    """
    maybe = list()
    with codecs.open('words1.txt', 'rb', 'utf-8') as f:
        for l in f:
            w = l.strip()
            if w and len(w) > 1 and w not in df:
                df.add(w)
                maybe.append(w)
    maybe = sorted(maybe, reverse = True, key = lambda w : len(w) )
    dicts = dicts + [u"%s %d n" % ( m, len(m) * 50 ) for m in maybe]
    """
    
    with codecs.open('userdict.txt', 'wb', 'utf-8') as f:
        f.write('\n'.join(dicts))

format_title = lambda title : re.sub(ur"【|】|\[|\]|/|_.", u' ', title).upper()

def get_server_name():
    db = pymongo.Connection().server
    conv = Converter('zh-hans')
    re_han = re.compile(ur"([\u4E00-\u9FA5a-zA-Z0-9+#&\_]+)", re.U)
    re_pure_han = re.compile(ur"([\u4E00-\u9FA5]+)", re.U)
    
    lines = list()
    for d in db.server.find():
        lines += d['title'].split()
        for aka in d['aka']:
            lines += aka.split()
    
    outs = list()
    df = set()
    for l in lines:
        for w in re_han.findall(l):
            if len(w) == 1 or re.match(r'\w+', w):
                continue
            
            w = conv.convert(w)
            if w not in df:
                df.add(w)
                outs.append(w)
            
        for w in re_pure_han.findall(l):
            if len(w) == 1:
                continue
            
            w = conv.convert(w)
            if w not in df:
                df.add(w)
                outs.append(w)
    
    with codecs.open('server_title.txt', 'wb', 'utf-8') as f:
        f.write('\n'.join(sorted(outs, reverse = True, key = lambda w : len(w) )))

def get_server_genre():
    db = pymongo.Connection().server
    conv = Converter('zh-hans')

    lines = list()
    for d in db.server.find({}, {'genre':1}):
        for genre in d['genre']:
            lines += genre.split()
    
    outs = list()
    df = set()
    re_han = re.compile(ur"([\u4E00-\u9FA5a-zA-Z0-9+#&\._]+)", re.U)
    for l in lines:
        for w in re_han.findall(l):
            w = conv.convert(w)
            if w not in df:
                df.add(w)
                outs.append(w)
    
    with codecs.open('server_genre.txt', 'wb', 'utf-8') as f:
        f.write('\n'.join( sorted(outs, reverse = True, key = lambda w : len(w) )))

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

append = [u'加长版', u'重压', u'3D版', u'全集']
conv = Converter('zh-hans')
re_han = re.compile(ur"([\u4E00-\u9FA5a-zA-Z0-9+#&\-:·]+)", re.U)
re_split = re.compile(ur'[^《》」「】【\[\]\)\(/\+_ ]+', re.U)
re_size = re.compile(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?(g|G|m|M|mb|Mb|MB|Mb)')
re_num = re.compile(ur"(^\d{2}\-\d{2}$)|(^[0-9.]+$)")
re_eng = re.compile(ur'[a-zA-Z0-9+#&\.\-_:]+$')
re_end = re.compile(ur'(%s)$' % "|".join(append))
re_title = re.compile(ur"[\u4E00-\u9FA5a-zA-Z0-9+#&\-:·]+[\u4E00-\u9FA5]?(|(i|ii|iii|iv)|\d{1, 4})")

def get_title(rawtitle):
    blocks = list()
    title = conv.convert(uniform( rawtitle ))
    for b in re_split.findall(title):
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
    
    title = re_end.sub('', title)
    
    try:
        return re_title.match(title).group()
    except AttributeError:
        return title

def get_scrapy_name():
    db = pymongo.Connection().scrapy
    
    titles = list()
    for d in db.scrapy.find():
        titles.append( get_title(d['title']) + ' | ' + d['title'] )
    
    with codecs.open('title.txt', 'wb', 'utf-8') as f:
        f.write("\n".join( titles ))

if __name__ == '__main__':
    make_jieba_dict()
