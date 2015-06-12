#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
import os
import jieba
import urlparse
import string
from pcnile import langconv
from pcnile.langconv import Converter
from django.utils.encoding import force_unicode
import pymongo

#jieba.load_userdict("..\\obtainfo\\userdict.txt")

def get_dict(fil):
    out = list()
    df = set()
    with codecs.open(fil, 'rb', 'utf-8') as f:
        for l in f:
            w = l.strip().lower()
            if w not in df:
                df.add(w)
                out.append(w)
        del df
    return out

language = get_dict( os.path.join('dict', 'language.txt') )    
area = get_dict( os.path.join('dict', 'area.txt') )    
genre = get_dict( os.path.join('dict', 'genre.txt') )
desc = get_dict( os.path.join('dict', 'desc.txt') )
quality = get_dict( os.path.join('dict', 'quality.txt') )
name = get_dict( os.path.join('dict', 'name.txt') )
movies = set( get_dict( os.path.join('dict', 'server_title.txt') ) )

stopwords = [s for s in string.punctuation] + [ ']', '[' ]
worse_dict = set(language + genre + desc + quality)
block_dict = set(language + area + genre + desc + quality + name)
cut = jieba.cut

# from title filter get sequeue string
# if only one, jieba cut
# if two, filter obvious block
def worse_filter(block):
    block = block.lower()
    if block in block_dict or ratio(block) == 1.0:
        return True
    else:
        return False

log = codecs.open('log.log', 'wb', 'utf-8')
re_size = re.compile(ur"(\d+mb)|(\d+m)|(\d+g)|(\d+gb)|(\d+.\d+g)|(\d+.\d+gb)")
def quality_block(block): # quality language size
    blocks = list()
    block = re_size.sub("", block)
    if len(block) == 0:
        return True
    
    for w in cut(block.lower()):
        w = w.strip()
        if w not in ['-', '.', '/']:
            blocks.append(w)
    
    same = set(blocks) & set(quality + language)
    ratio = float(len(same)) / float(len(blocks))
    if ratio > 0.5:
        return True
    else:
        return False

s = set(area + genre)
def rule_filter(block):
    if re.match(ur"^\d{2}|\d{4}年|\d{4}", block) and set(list(cut(block))) & s:
        return True
    elif re.match(ur"^精彩|高分|火爆|爆笑|获奖", block) and set(list(cut(block))) & s:
        return True
    else:
        return False

badwords = [
    u"无任何水印", u'狂人之家出品', u'飞鸟影视scm组', u'听译中字', u'国语无字版'
            u'酷艺网www.kuyi.tv', u'无对白无字幕', u'3e无水印', u'飞鸟老狼字幕组']
def better(block):
    block = block.lower()
    if block in movies:
        return True
    else:
        return False

re_num = re.compile(ur"(^\d+年$)|(^\d{2}\-\d{2}$)|(^[0-9.]+$)")

def ratio(block):
    block = block.lower()
    words = [w for w in cut(block, HMM=False)]
    if len(words) == 0:
        return 0.0
    
    count = 0
    for w in words:
        if w in block_dict:
            count += 1
        elif w in stopwords:
            count += 1
        elif re_num.match(w):
            count += 1
    
    return count / float(len(words))

if __name__ == '__main__':
    words = list( cut("3D豪情") )
    print ' | '.join(words)
    
    for w in words:
        print ratio(w)
    
    print ratio(u"3D豪情")