#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
import os
import json
from disabler import cut, ratio, better, worse_filter, area, genre
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

re_num = re.compile(ur"(^\d{1,2}\-\d{1,2}$)|(^\d{1,2}\.\d{1,2}$)|(^\d+mb$)|(^\d+m$)")
re_han = re.compile(ur"([\u4E00-\u9FA5a-zA-Z0-9+#&\._]+)", re.U)
stopwords = [s for s in string.punctuation] + [ ']', '[', u'—', u'“', u'”', u'·', u'·' ]
def word_block(word):
    word = word.strip()
    if word == "":
        return True
    elif re_num.match(word):
        return True
    elif word in stopwords:
        return True
    elif re_han.match(word):
        return False
    else:
        return True

db = pymongo.Connection().server
titles = list()
for d in db.server.find():
    titles += d['aka'] + [d['title']]
titles = list(set(titles))

texts  = [[w for w in cut(uniform(title)) if not word_block(w)] for title in titles]
all_tokens = sum(texts, [])
tokens_count = float(len(all_tokens))
tokens = list(set(all_tokens))
tf = dict()
for t in tokens:
    tf[t] = all_tokens.count(t) / tokens_count

with codecs.open('tf.json', 'wb', 'utf-8') as f:
    json.dump(tf, f)
