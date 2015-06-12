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

GLOBAL_LEVEL = 12

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
    
    tokens = list()
    for d in db.scrapy.find({'level':GLOBAL_LEVEL}):
        tokens.append( title_to_tokens(d['title']) )
    
    dictionary = corpora.Dictionary(tokens)
    
    dictionary.save('deerwester.dict')
    
    corpus = [dictionary.doc2bow(text) for text in tokens]
    corpora.MmCorpus.serialize('deerwester.mm', corpus)
    
    return dictionary, corpus

def query_same(title):
    vec_lsi = tfidf[dictionary.doc2bow(tokens)] 

dictionary, corpus = get_dict_and_corpus()

tfidf = models.TfidfModel(corpus)
index = similarities.Similarity('index', corpus, num_features=len(dictionary))

def second_stage(cur, lists, items):
    tokens = list()
    count = lists.index(cur)
    print count
    for d in lists:
        try:
            token = items[d]['tokens']
        except KeyError:
            token = title_to_tokens( items[d]['desc'] )
            items[d]['tokens'] = token
        
        tokens.append( token )
    
    sub_dictionary = corpora.Dictionary(tokens)
    sub_corpus = [sub_dictionary.doc2bow(text) for text in tokens]
    sub_index = similarities.Similarity('sub_index', sub_corpus, num_features=len(sub_dictionary))
    
    cc = 0
    for sim in sub_index:
        if cc == count:
            res = sorted([ s for s in numpy.argsort(-sim)[:30] if sim[s] > 0.8 ])
            break
        cc += 1
    
    return [lists[r] for r in res]

df_group = list()

def dumpfilter(count):
    for s in df_group:
        if count in s:
            return True
    
    return False

def dump_add(counts):
    counts = set(counts)
    
    for i in range(len(df_group)):
        if counts & df_group[i]:
            df_group[i] = df_group[i] | counts
            break
    else:
        df_group.append(counts)

if __name__ == '__main__':
    stamp = datetime.datetime.now()
    
    db = pymongo.Connection().scrapy
    titles = [d for d in db.scrapy.find({'level':GLOBAL_LEVEL})]
    
    group = list()
    single = list()
    count = 0
    
    for sim in index:
        if not dumpfilter(count):
            res = sorted([ int(s) for s in numpy.argsort(-sim)[:30] if sim[s] > 0.618 ])
            if len(res) > 1:
                #res = second_stage(count, res, titles)
                if len(res) > 1:
                    dump_add(res)
                else:
                    dump_add(res)
            else:
                dump_add(res)
        
        count += 1
    
    with codecs.open('out.txt', 'wb', 'utf-8') as f:
        for res in df_group:
            if len(res) > 1:
                f.write(",\t".join([str(r) for r in res]) + '\n')
                f.write("\t".join([str(sim[r]) for r in res]) + '\n')
                f.write("\n".join( [titles[i]['title'] for i in res] ))
                f.write('\n\n')
    
    """
    for res in df_group:
        if len(res) > 1:
            res = list(res)
            
            target = titles[res[0]]
            
            for r in res[1 : ] :
                r = titles[r]
                target['source'] += r['source']
                target['resource'] += r['resource']
                db.scrapy.remove({'_id':r['_id']})
            
            target['level'] = 888
            db.scrapy.save(target)
    """
    
    print datetime.datetime.now() - stamp
    