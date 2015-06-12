#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import urlparse

from django import template
from django.core.cache import get_cache
from django.utils.safestring import mark_safe
from django.conf import settings
from django.db.models import Q

from obtainfo.models import MovieInfo, BigPoster

register = template.Library()

@register.filter(name='oid')
def oid(m):
	try:
		return str(m['_id'])
	except:
		return m['_id']
	
@register.filter(name='nbsp')
def nbsp(value):
	return mark_safe("\n\n".join(["&nbsp;&nbsp;&nbsp;&nbsp;" + s for s in value.split('\n')]))

@register.filter(name='pic')
def pic(name):
	if name.startswith('http'):
		return name
	
	template = "http://%s.qiniudn.com/%s"
	buckets = ['obtainfo', 'pcnile', 'putty']
	index = random.randint(0, len(buckets)-1)
	
	return template % (buckets[index], name)

@register.simple_tag
def pic_tag(name, local=False):
	if name.startswith('http'):
		return name
	else:
		return urlparse.urljoin('http://movie.obtainfo.com/pic/', name)

@register.inclusion_tag('tags/dummy.html')
def big_poster(number=10, template='tags/big_poster.html'):
	return {'template':template, 'big_poster':BigPoster.objects.all().order_by("-timestamp"),}

@register.inclusion_tag('tags/dummy.html')
def recommand(number=10, template='tags/rank.html'):
	recommends = MovieInfo.objects.filter(recommend=True)
	return {'template':template,
		'title':u"编辑墙裂推荐",
		'first':recommends.filter(Q(image__isnull=False)&~Q(image='')).order_by("-timestamp")[0],
		'second':recommends.filter(Q(image__isnull=True)|Q(image='')).order_by("-timestamp")[:number - 1]
	}

@register.inclusion_tag('tags/dummy.html')
def hot_stats(number=10, template='tags/rank.html'):
	recommands = MovieInfo.objects
	return {'template':template,
		'title':u"大家都在看",
		'first':recommands.filter(Q(image__isnull=False)&~Q(image='')).order_by("-visitor")[0],
		'second':recommands.filter(Q(image__isnull=True)|Q(image='')).order_by("-visitor")[:number - 1]
	}

@register.inclusion_tag('tags/dummy.html')
def mark_recommend(oid, template='tags/mark_recommend.html'):
	try:
		recommend = MovieInfo.objects.filter(id=oid).values('top', 'recommend')[0]['recommend']
	except Exception as e:
		recommend = False
	
	return {'template':template, 'recommend':recommend, 'oid':oid}

@register.inclusion_tag('tags/dummy.html')
def mark_top(oid, template='tags/mark_top.html'):
	try:
		top = MovieInfo.objects.filter(id=oid).values('top', 'recommend')[0]['top']
	except Exception as e:
		top = False
	
	return {'template':template, 'top':top, 'oid':oid}
