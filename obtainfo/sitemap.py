#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings
import datetime
from functools import wraps

from django.contrib.sites.models import get_current_site
from django.core import urlresolvers
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils import six

from django.conf import settings
from django.contrib.sitemaps.views import x_robots_tag
from django.contrib.sitemaps import Sitemap
from django.contrib.sites.models import Site
from django.views.decorators.cache import cache_page

from pcnile.paginator import JuncheePaginator

class MovieFullSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    limit = 500
    
    def _get_paginator(self):
        return JuncheePaginator(self.items(), self.limit)
    paginator = property(_get_paginator)
    
    def items(self):
        info = settings.MONGOINFO
        return info.find({}, {'_id':1, 'addtime':1})

    def lastmod(self, obj):
        return obj['addtime']
    
    def location(self, obj):
        return "/detail/%s/" % str(obj["_id"])

class MovieNewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    limit = 500
    
    def items(self):
        info = settings.MONGOINFO
        return [d for d in info.find({}, {'_id':1, 'addtime':1})]

    def lastmod(self, obj):
        return obj['addtime']
    
    def location(self, obj):
        return "/detail/%s/" % str(obj["_id"])

class SelectionSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    limit = 500
    
    def items(self):
        db = settings.MONGODB
        return [d for d in db.selection.find({''}, {'_id':1, 'addtime':1})]

    def lastmod(self, obj):
        return obj['addtime']
    
    def location(self, obj):
        return "/selection/%s/" % str(obj["_id"])

@cache_page(60 * 60 * 24)
@x_robots_tag
def index(request, sitemaps,
          template_name='sitemap_index.xml', content_type='application/xml',
          sitemap_url_name='obtainfo.sitemap.sitemap',
          mimetype=None):

    if mimetype:
        warnings.warn("The mimetype keyword argument is deprecated, use "
            "content_type instead", DeprecationWarning, stacklevel=2)
        content_type = mimetype

    req_protocol = 'https' if request.is_secure() else 'http'
    req_site = get_current_site(request)
    req_site = Site(name='movie', domain='movie.' + req_site.domain)
    
    sites = []
    for section, site in sitemaps.items():
        if callable(site):
            site = site()
        protocol = req_protocol if site.protocol is None else site.protocol
        sitemap_url = urlresolvers.reverse(
                sitemap_url_name, kwargs={'section': section})
        absolute_url = '%s://%s%s' % (protocol, req_site.domain, sitemap_url)
        sites.append(absolute_url)
        for page in range(2, site.paginator.num_pages + 1):
            sites.append('%s?p=%s' % (absolute_url, page))

    return TemplateResponse(request, template_name, {'sitemaps': sites},
                            content_type=content_type)

@cache_page(60 * 60 * 3)
@x_robots_tag
def sitemap(request, sitemaps, section=None,
            template_name='sitemap.xml', content_type='application/xml',
            mimetype=None):

    if mimetype:
        warnings.warn("The mimetype keyword argument is deprecated, use "
            "content_type instead", DeprecationWarning, stacklevel=2)
        content_type = mimetype

    req_protocol = 'https' if request.is_secure() else 'http'
    req_site = get_current_site(request)
    req_site = Site(name='movie', domain='movie.' + req_site.domain)
    
    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps = [sitemaps[section]]
    else:
        maps = list(six.itervalues(sitemaps))
    page = request.GET.get("p", 1)

    urls = []
    for site in maps:
        try:
            if callable(site):
                site = site()
            urls.extend(site.get_urls(page=page, site=req_site,
                                      protocol=req_protocol))
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)
    return TemplateResponse(request, template_name, {'urlset': urls},
                            content_type=content_type)
