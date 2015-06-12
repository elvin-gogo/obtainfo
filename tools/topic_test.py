#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
import os
from disabler import cut, ratio, better, worse_filter, get_dict
from title import fast_title
import urlparse
import string
from pcnile import langconv
from pcnile.langconv import Converter
from django.utils.encoding import force_unicode
import pymongo
import datetime
import operator
from bson import ObjectId
import argparse
import numpy
from gensim import corpora, models, similarities

def Q2B(uchar):
    inside_code=ord(uchar)
    if inside_code==0x3000:
        inside_code=0x0020
    else:
        inside_code-=0xfee0
    if inside_code<0x0020 or inside_code>0x7e:
        return uchar
    return unichr(inside_code)

def stringQ2B(ustring):
    return "".join([Q2B(uchar) for uchar in ustring])

def uniform(ustring):
    return stringQ2B(ustring).lower()

stopwords = get_dict('words.txt') + [s for s in string.punctuation]
conv = Converter('zh-hans')
re_num = re.compile(ur"(^\d{2}\-\d{2}$)|(^[0-9.]+$)")
re_size = re.compile(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?(g|G|m|M|mb|Mb|MB|Mb)')
re_date = re.compile(r'(^\[\d+\-\d+\]?)|(^\[\d+\.\d+\])')

def title_to_tokens(title):
    title = fast_title(title)
    
    words = list()
    
    """
    for t in cut(title):
        t = t.strip()
        if t and t not in stopwords and not re_size.match(t) and not re_num.match(t):
            words.append(t)
    """
    
    if len(words) == 0:
        words = list()
        for t in cut(title):
            t = t.strip()
            if t and t not in stopwords and not re_size.match(t):
                words.append(t)
    else:
        return words

    if len(words) == 0:
        words = list()
        for t in cut(title):
            t = t.strip()
            if t and not re_size.match(t):
                words.append(t)
    else:
        return words
    
    if len(words) == 0:
        words = list()
        for t in cut(title):
            t = t.strip()
            if t:
                words.append(t)
    else:
        return words

def get_dict_and_corpus():
    db = pymongo.Connection().scrapy
    alls = db.scrapy.find({'level':{'$gt':4}})
    tokens = list()
    for d in [153,667,730,11760,12648,15747]:
        look = title_to_tokens( alls[d]['title'])
        tokens.append( look )
        print " | ".join(look)
    
    dictionary = corpora.Dictionary(tokens)
    corpus = [dictionary.doc2bow(text) for text in tokens]
    
    return dictionary, corpus

dictionary, corpus = get_dict_and_corpus()
tfidf = models.TfidfModel(corpus)
index = similarities.MatrixSimilarity(tfidf[corpus])

if __name__ == '__main__':
    for sim in index:
        res = sorted([ int(s) for s in numpy.argsort(-sim)[:30] if sim[s] > 0.7 ])
        print "\t".join([str(sim[r]) for r in res])
