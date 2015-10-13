#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db.models import Q
from django.conf import settings
from django.shortcuts import render
from django.core import serializers
from django.forms.models import model_to_dict
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.utils.encoding import force_unicode

from detail import used_time_tag
from obtainfo.models import SearchKey, MovieInfo, BigPoster, Series
from obtainfo.templatetags.obtainfo_tags import pic as render_pic

from pcnile.search import FullTextSearchClient
from pcnile.http import json, JsonResponse
from pcnile.paginator import get_page_part
from pcnile.helper import md5sum, group_list

from bson.objectid import ObjectId

import re
import os
import base64
import random
import datetime
import pymongo
import time
import logging

re_imdb = re.compile(r"tt\d+")
re_douban = re.compile(r"dd\d+")
logger = logging.getLogger(__name__)
verify_oid = lambda oid: True if re.match(r'^[0-9a-fA-F]{24}$', oid) else False
index_field = {'type': 1, 'bigpic': 1, 'title': 1, 'language': 1, 'year': 1, 'douban': 1, 'genre': 1, 'resource': 1,
               'area': 1, 'director': 1, 'actor': 1, 'plot': 1, 'finish': 1}


def get_request_page(request_dict, default=1):
    try:
        return int(request_dict['page'])
    except:
        return default


def search(request):
    if request.method == "POST":
        raise Http404

    try:
        key = request.GET['search'].strip()
    except:
        return HttpResponseRedirect("/")

    page = get_request_page(request.GET)

    if key == '':
        errors = u"请输入搜索的关键词哦！"
        m = {'results': [], 'errors': errors, 'search': key}
    elif len(key) > 25:
        errors = u"不好意思！您的关键词太长了......"
        m = {'results': [], 'errors': errors, 'search': key}
    elif re_imdb.match(key):
        key = re_imdb.match(key).group()
        collection = settings.MONGOINFO
        results = collection.find({'imdb': key}, index_field)
        contacts = get_page_part(results, request.GET.get('page'))
        m = {'results': contacts, 'pages': contacts, 'search': key}
    elif re_douban.match(key):
        key = re_douban.match(key).group()
        collection = settings.MONGOINFO
        results = collection.find({'douban.id': key[2:]}, index_field)
        contacts = get_page_part(results, request.GET.get('page'))
        m = {'results': contacts, 'pages': contacts, 'search': key}
    else:
        client = FullTextSearchClient(settings.MONGOINFO)
        (contacts, results) = client.query_page(key, page)

        if results.count() == 0:
            try:
                sk = SearchKey(key=force_unicode(key).encode('utf-8'))
            except:
                sk = SearchKey(key=key)
            sk.save()

            results = []
            errors = u"对不起！我们目前还没有您要的资源......"
        else:
            errors = ''

        m = {'results': results, 'pages': contacts, 'errors': errors, 'search': key}

    return render(request, 'search.html', {"m": m}, )


@cache_page(60 * 60)
@used_time_tag
def index(request, query):
    # generate query string
    try:
        k, v = query.split('_')[0].split('-')
        if k == 'genre':
            query_obj = {k: v}
        else:
            return HttpResponseRedirect("/")
    except:
        return HttpResponseRedirect("/")

    collection = settings.MONGOINFO
    results = collection.find(query_obj).sort("year", -1)
    contacts = get_page_part(results, get_request_page(request.GET))

    return render(request, 'search.html', {"m": {'results': contacts, 'pages': contacts, 'search': ''}}, )


@cache_page(60 * 60)
def sindex(request): # selection index
    db = settings.MONGODB
    results = db.selection.find().sort("addtime", -1)
    contacts = get_page_part(results, get_request_page(request.GET))

    results = list()
    collection = settings.MONGOINFO
    for c in contacts:
        c['pic'] = collection.find_one({'_id': ObjectId(c['list'][0])}, {'stdpic': 1})['stdpic']
        results.append(c)

    m = {'results': results, 'pages': contacts, 'search': ''}

    return render(request, 'sindex.html', {"m": m}, )


"""
build selection block
"""


@cache_page(60 * 60)
def selection(request, sid):
    try:
        db = settings.MONGODB
        s = db.selection.find_one({'_id': ObjectId(sid)})
        if s == None:
            raise Http404
    except pymongo.errors.InvalidId:
        logger.error('get an unused selection id %s' % sid)
        raise Http404

    contacts = get_page_part(s['list'], get_request_page(request.GET))
    collection = settings.MONGOINFO
    results = collection.find({'_id': {'$in': [ObjectId(oid) for oid in contacts]}})
    m = {'results': results, 'pages': contacts}

    return render(request, 'selection.html', {"m": m, 'title': s['title']}, )


@csrf_exempt
def retrieve(request):
    genre = {
        'title': u'类型：',
        'name': 'genre',
        'k': [u'全部', u'剧情', u'喜剧', u'爱情', u'科幻', u'动作', u'惊悚', u'恐怖', u'冒险', u'奇幻', u'家庭', u'记录片', u'古装', u'战争', u'历史',
              u'西部', u'悬疑', u'奇幻'],
        'v': [u'', u'剧情', u'喜剧', u'爱情', u'科幻', u'动作', u'惊悚', u'恐怖', u'冒险', u'奇幻', u'家庭', u'记录片', u'古装', u'战争', u'历史',
              u'西部', u'悬疑', u'奇幻']
    }

    area = {
        'title': u'地区：',
        'name': 'area',
        'k': [u'全部', u'内地', u'美国', u'英国', u'韩国', u'日本', u'香港', u'台湾', u'印度', u'英国', u'法国', u'意大利', u'德国', u'泰国', u'西班牙',
              u'瑞典', u'俄罗斯'],
        'v': [u'', u'中国', u'美国', u'英国', u'韩国', u'日本', u'香港', u'台湾', u'印度', u'英国', u'法国', u'意大利', u'德国', u'泰国', u'西班牙',
              u'瑞典', u'俄罗斯']
    }

    year = {
        'title': u'年代：',
        'name': 'year',
        'k': [u'全部', u'2014', u'2013', u'2012', u'2011', u'2010', u'2009', u'2008', u'2007', u'2006', u'2005', u'2004',
              u'2003', u'2002', u'2001', u'2000', u'1999', u'1998'],
        'v': [u'', u'2014', u'2013', u'2012', u'2011', u'2010', u'2009', u'2008', u'2007', u'2006', u'2005', u'2004',
              u'2003', u'2002', u'2001', u'2000', u'1999', u'1998']
    }

    resource = {
        'title': u'资源：',
        'name': 'resource',
        'k': [u'不限', u'在线', u'网盘', u'3D高清', u'高清', u'普清', u'尝鲜'],
        'v': [u'', {'resource.online': {'$gt': 0}}, {'resource.netdisk': {'$gt': 0}}, {'resource.stereo': {'$gt': 0}},
              {'resource.hd': {'$gt': 0}}, {'resource.dvd': {'$gt': 0}}, {'resource.cam': {'$gt': 0}}]
    }

    sub_type = {
        'title': u'主题：',
        'name': 'type',
        'k': [u'不限', u'电影', u'电视剧'],
        'v': [u'', 'movie', 'tv']
    }

    order = {
        'title': u'排序：',
        'name': 'order',
        'k': [u'默认', u'热门', u'经典', u'最新上映', u'添加时间'],
        'v': [
            [('year', pymongo.ASCENDING), ('addtime', pymongo.ASCENDING)],
            {'year': -1, 'douban.ranking.count': -1, 'douban.ranking.score': -1},
            [("douban.ranking.count", -1), ("douban.ranking.score", -1)],
            [("showtime", pymongo.DESCENDING)],
            [("addtime", pymongo.DESCENDING)]
        ]
    }

    table = {'genre': genre, 'area': area, 'year': year, 'resource': resource, 'type': sub_type}

    if request.method == 'POST':
        try:
            js = json.loads(request.body)
        except:
            return JsonResponse({'status': 'fail'})

        qs = list()
        sort_key = order['v'][js['order']]
        for k, v in table.items():
            v = v['v'][js[k]]
            if v:
                if k == 'resource':
                    qs.append(v)
                else:
                    qs.append({k: v})

        collection = settings.MONGOINFO
        if len(qs):
            results = collection.find({'$and': qs}, {'title': 1, 'stdpic': 1, 'actor': 1}).limit(3500)
        else:
            results = collection.find({}, {'title': 1, 'stdpic': 1, 'actor': 1}).limit(3500)

        contacts = get_page_part(results, js['page'], 20)

        for c in contacts.object_list:
            c['stdpic'] = render_pic(c['stdpic'])
            try:
                c['actor'] = c['actor'][0]
            except IndexError:
                pass

        page = {
            'has_previous': contacts.has_previous(), 'has_next': contacts.has_next(),
            'current': str(contacts.number), 'range': contacts.paginator.page_range_ext,
        }

        if page['has_previous']:
            page['previous_page_number'] = contacts.previous_page_number()
        if page['has_next']:
            page['next_page_number'] = contacts.next_page_number()

        return JsonResponse({'status': 'success', 'results': contacts.object_list, 'page': page})

    return render(request, 'retrieve.html', {'table': [genre, area, year, resource, sub_type, order]}, )


@cache_page(10 * 60)
def lazy(request):
    sidebar = request.GET.get('s', 'recommend')

    try:
        number = abs(int(request.GET.get('n', 30)))
        if number not in xrange(10, 60):
            number = 30
    except:
        number = 30

    oid = request.GET.get('o', '')
    if verify_oid(oid):
        try:
            series = [{'id': s.id, 'no': s.sequence, 'title': s.title} for s in
                      Series.objects.get(id=oid).get_root().get_descendants(include_self=True)]
        except:
            series = []
    else:
        series = []

    if sidebar == 'hot':
        title = u"大家都在看"
        recommands = MovieInfo.objects
        first = recommands.filter(Q(image__isnull=False) & ~Q(image='')).order_by("-visitor")[0]
        second = recommands.filter(Q(image__isnull=True) | Q(image='')).order_by("-visitor")[:number - 1]
    else:
        title = u"编辑墙裂推荐"
        recommends = MovieInfo.objects.filter(recommend=True)
        first = recommends.filter(Q(image__isnull=False) & ~Q(image='')).order_by("-timestamp")[0]
        second = recommends.filter(Q(image__isnull=True) | Q(image='')).order_by("-timestamp")[:number - 1]

    ranking = dict()
    ranking['title'] = title
    ranking['first'] = {'id': first.id, 'title': first.title, 'image': first.image.url}
    ranking['second'] = [{'id': s.id, 'title': s.title, 'no': c + 2} for c, s in enumerate(second)]

    return JsonResponse({'ranking': ranking, 'series': series, 'status': 'success'})


@cache_page(10 * 60)
@used_time_tag
def main(request):
    page = get_request_page(request.GET)
    if page == 1 and 'page' in request.GET:
        return HttpResponseRedirect('/')

    collection = settings.MONGOINFO
    oids = [ObjectId(o.id) for o in MovieInfo.objects.filter(top=True)]
    results = collection.find({"_id": {"$nin": oids}}, index_field).sort('updatetime', -1).limit(3500)
    contacts = get_page_part(results, page)
    m = {'results': contacts, 'pages': contacts, 'index': False}

    if page == 1:
        # fill big poster content
        db = settings.MONGODB

        m['ontop'] = collection.find({"_id": {"$in": oids}}, index_field)
        m['big_poster'] = True
        m['selection'] = group_list([d for d in db.selection.find().sort('addtime', -1).limit(21)], 7)
        m['index'] = True

    return render(request, 'index.html', {"m": m}, )
