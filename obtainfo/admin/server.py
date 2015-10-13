#!/usr/bin/env python
# -*- coding: utf-8 -*-

# system lib
import re
import datetime

# framework include
from django.conf import settings
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext as _
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.cache import never_cache
from django.utils.encoding import force_unicode

# project include
from obtainfo.models import SearchKey, MovieInfo

# third lib include
from bson.objectid import ObjectId


@login_required(login_url='/login/')
def mark_recommend(request):
    oid = request.GET.get('oid', '')
    if re.match(r'^[0-9a-fA-F]{24}$', oid):
        try:
            collection = settings.MONGOINFO
            m = collection.find_one(ObjectId(oid))
            mi, created = MovieInfo.objects.get_or_create(
                id=oid,
                defaults={'title': m['title'], 'timestamp': datetime.datetime.now(), 'recommend': True}
            )
            if not created:
                if mi.recommend == False:
                    mi.timestamp = datetime.datetime.now()
                mi.recommend = not mi.recommend
            mi.save()
        except Exception as e:
            print e

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404


@login_required(login_url='/login/')
def mark_top(request):
    oid = request.GET.get('oid', '')
    if re.match(r'^[0-9a-fA-F]{24}$', oid):
        try:
            collection = settings.MONGOINFO
            m = collection.find_one(ObjectId(oid))
            mi, created = MovieInfo.objects.get_or_create(id=oid,
                                                          defaults={'title': m['title'],
                                                                    'timestamp': datetime.datetime.now(), 'top': True}
                                                          )
            if not created:
                if mi.top == False:
                    mi.timestamp = datetime.datetime.now()
                mi.top = not mi.top
            mi.save()
        except Exception as e:
            print e

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        raise Http404
