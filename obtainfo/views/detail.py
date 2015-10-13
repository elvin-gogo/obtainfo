#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import copy
import datetime
import hashlib
import logging
import os
import random
import re
import StringIO
import time
import urllib
import urlparse
from functools import wraps
from zipfile import ZipFile

import pymongo
from bson.objectid import ObjectId
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db.models import F
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.http import urlquote
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from shortuuid import uuid

from obtainfo.models import MovieInfo
from obtainfo.templatetags.obtainfo_tags import pic_tag as render_pic
from pcnile.helper import group_list, md5sum
from sendfile import sendfile

logger = logging.getLogger(__name__)
re_urn = re.compile(ur'xt=urn:btih:(\w+)')
re_file_name = re.compile(r"[\/\\\:\*\?\"\<\>\|]")
verify_oid = lambda oid: True if re.match(r'^[0-9a-fA-F]{24}$', oid) else False
re_ua = re.compile(r"android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini", re.IGNORECASE)


def used_time_tag(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        stamp = time.time()
        response = func(request, *args, **kwargs)
        logger.info('%s, %s' % (time.time() - stamp, request.path))
        return response

    return inner


def memoize(key_prefix):
    def func_wrapper(func):
        @wraps(func)
        def inner(key, *args, **kwargs):
            key = "%s_%s" % (key_prefix, key)
            response = cache.get(key)
            if response:
                return response
            else:
                response = func(*args, **kwargs)
                cache.set(key, response, timeout=60 * 60)
                return response

        return inner

    return func_wrapper


def detail_thunder(request, uid):
    if verify_oid(uid) == False:
        raise Http404

    link = "http://movie.obtainfo.com/detail/%s.zip" % uid
    thunder = "thunder://" + base64.standard_b64encode('AA' + link + 'ZZ')
    return render(request, 'thunder.html', {'thunder': thunder}, )


def detail_show(request, uid):
    if verify_oid(uid) == False:
        raise Http404

    try:
        collection = settings.MONGOINFO
        m = collection.find_one({'_id': ObjectId(uid)})
    except pymongo.errors.InvalidId:
        logger.error('get a invalid movie id %s' % uid)
        raise Http404

    if m:
        blog = get_template('show.txt')
        article = blog.render(Context({'m': m}))

        response = HttpResponse(mimetype="application/txt")
        response["Content-Disposition"] = "attachment; filename=%s.txt" % m['_id']
        response.write(article)

        return response
    else:
        raise Http404


def detail_show_zip(request, uid):
    if verify_oid(uid) == False:
        raise Http404

    try:
        collection = settings.MONGOINFO
        m = collection.find_one({'_id': ObjectId(uid)})
    except pymongo.errors.InvalidId:
        logger.error('get a invalid movie id %s' % uid)
        raise Http404

    if m:
        blog = get_template('show.txt')
        article = blog.render(Context({'m': m})).encode('utf-8')

        in_memory = StringIO.StringIO()
        zip = ZipFile(in_memory, "a")
        try:
            zip.writestr("%s.txt" % m['title'], article)
        except:
            zip.writestr("%s.txt" % m['_id'], article)

        for f in zip.filelist:
            f.create_system = 0
        zip.close()

        response = HttpResponse(mimetype="application/zip")
        response["Content-Disposition"] = "attachment; filename=%s.zip" % m['_id']

        in_memory.seek(0)
        response.write(in_memory.read())

        try:
            mi, created = MovieInfo.objects.get_or_create(id=uid, defaults={'title': m['title'],
                                                                            'timestamp': datetime.datetime.now()})
            mi.zip_visitor = F('zip_visitor') + 1
            mi.save()
        except:
            pass

        return response
    else:
        raise Http404


def build_detail_html(request, uid):
    try:
        db = settings.MONGODB
        m = db.info.find_one({'_id': ObjectId(uid)})
        m['resource'] = db.resource.find_one({'_id': ObjectId(uid)})
        del m['resource']['_id']
    except:
        raise Http404

    if m['type'] == 'tv' and len(m['resource']['online']):
        m['resource']['online_length'] = 0
        for o in m['resource']['online']:
            m['resource']['online_length'] += len(o['resource'])
            for site in o['resource']:
                site['id'] = uuid()[:4]

    """
    fix douban comment date
    """
    m['comment'] = m['comment'][:10]
    for c in m['comment']:
        c['update'] = parse_date(c['update'])

        try:
            rating = int(c['rating'])
        except ValueError:
            rating = 50

        if rating <= 10:
            c['rating'] = str(12)
        elif rating <= 20:
            c['rating'] = str(22)
        elif rating <= 30:
            c['rating'] = str(32)
        elif rating <= 40:
            c['rating'] = str(42)
        else:
            c['rating'] = str(55)

    return render(request, 'detail.html', {'m': m}, )


@used_time_tag
def detail(request, uid):
    if verify_oid(uid) == False:
        raise Http404

    if request.user.is_superuser:
        return build_detail_html(request, uid)

    try:
        mi, created = MovieInfo.objects.get_or_create(id=uid, defaults={'title': 'title_occupy',
                                                                        'timestamp': datetime.datetime.now()})
        if created:
            collection = settings.MONGOINFO
            m = collection.find_one({'_id': ObjectId(uid)}, {'title': 1})
            mi.title = m['title']

        mi.visitor = F('visitor') + 1
        mi.save()
    except Exception as e:
        logger.info('create movie info object for count fail')

    file_path = os.path.join(settings.HTML_DIR, uid)
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            return HttpResponse(f.read())
    else:
        response = build_detail_html(request, uid)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return response


@csrf_exempt
def download(request):
    try:
        if not urlparse.urlparse(request.META['HTTP_REFERER']).path.startswith("/detail/"):
            return HttpResponseRedirect("/")
    except KeyError:
        return HttpResponseRedirect("/")

    try:
        c = request.GET['c']
        k = c + '.uid'
        v = request.GET['uid']
    except KeyError as e:
        raise Http404

    try:
        collection = settings.MONGORESOURCE
        r = collection.find_one({k: v}, {'_id': 0, c: {'$elemMatch': {'uid': v}}})[c][0]
        r['magnet'] = False
    except Exception as e:
        raise Http404

    try:
        if r['link'].startswith('magnet'):
            r['magnet'] = True

            # if user_agent_parse(request.META['HTTP_USER_AGENT']).is_pc == False:
            if re_ua.findall(request.META['HTTP_USER_AGENT']):
                urn = re_urn.findall(r['link'])[0].lower()
                urn_file = os.path.join(urn[:2], urn + '.torrent')

                full_path = os.path.join(settings.TORRENT_DIR, urn_file)
                if os.path.isfile(full_path):
                    r['urn'] = urn
                    r['torrent'] = urn_file.replace("\\", '/')
    except Exception as e:
        print e

    return render(request, 'download.html', r, )


@csrf_exempt
def torrent_download(request):
    try:
        if not urlparse.urlparse(request.META['HTTP_REFERER']).path.startswith("/download/"):
            return HttpResponseRedirect("/")
    except KeyError:
        return HttpResponseRedirect("/")

    if request.method == 'POST':
        urn = request.POST.get('urn', '')
        if urn == '':
            raise Http404

        path = request.POST.get('link', None)
        if os.path.isfile(os.path.join(settings.TORRENT_DIR, path)):
            response = sendfile(request, os.path.join(settings.TORRENT_DIR, path))
        else:
            raise Http404

        try:
            name = u"【欧泊影视】%s.torrent" % re_file_name.sub("", request.POST.get('title', urn))
        except:
            name = u"【欧泊影视】电影名字未知"

        if "MSIE" in request.META['HTTP_USER_AGENT']:
            response['Content-Disposition'] = 'attachment; filename="' + urllib.quote_plus(name.encode('utf-8')) + '"'
        else:
            response['Content-Disposition'] = 'attachment; filename="' + name.encode('utf-8') + '"'

        return response

    return HttpResponseRedirect("/")
