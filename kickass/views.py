#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import get_cache
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.views.decorators.http import condition
from django.template.loader import get_template
from django.template import Context
from django.utils.encoding import force_unicode, DjangoUnicodeDecodeError

from bson.objectid import ObjectId
import base64
import random
import datetime
import json
import re
import logging
import StringIO

db = settings.MONGODB

@login_required(login_url='/login/')
@csrf_exempt
def kickass_list(request):
    if request.method == 'POST':
        js = json.loads(request.body)
        if js['method'] == 'down':
            oids = [ObjectId(oid) for oid in js['data']]
            db.fast.update({'_id':{"$in":oids}}, {"$set":{"state":"process"}}, multi=True)
            
        elif js['method'] == 'discard':
            oids = [ObjectId(oid) for oid in js['data']]
            db.fast.update({'_id':{"$in":oids}}, {"$set":{"state":"stop"}}, multi=True)
            
        elif js['method'] == 'merge':
            new = {'title':'', 'level':0, 'imdb':'', 'resource':[], 'state':'active'}
            for oid in js['data']:
                try:
                    m = db.fast.find_one({'_id':ObjectId(oid)})
                    if m['title']:
                        new['title'] = m['title']
                    if m['level'] > new['level']:
                        new['level'] = m['level']
                    if m['imdb']:
                        new['imdb'] = m['imdb']
                    new['resource'] += m['resource']
                    
                    db.fast.remove({'_id':ObjectId(oid)})
                except:
                    pass
            
            if len(new['resource']):
                db.fast.save(new)
            
        return HttpResponse(json.dumps({'status':'success'}), content_type="application/json")
    
    items = list(db.fast.find({'state':'active'}).limit(100))
    for i in items:
        i['resource'] = [r for r in i['resource'] if r['level'] == i['level']]
        i['num'] = len(i['resource'])
        i['resource'] = reversed(i['resource'])
        
    return render(request, 'kickass.html',  {'items':items, 'total':db.fast.find({'state':'active'}).count()})
