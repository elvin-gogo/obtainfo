#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings
from obtainfo.sitemap import MovieFullSitemap, index, sitemap

sitemaps = {
    'full': MovieFullSitemap,
}

urlpatterns = patterns(
    'obtainfo.views',
    # server
    url(ur'^$', 'views.main', name='home'),
    url(ur'^download/$', 'detail.download'),
    url(ur'^torrent/$', 'detail.torrent_download'),
    url(ur'^detail/(?P<uid>(\w+))/thunder/$', 'detail.detail_thunder'),
    url(ur'^detail/(?P<uid>(\w+)).txt$', 'detail.detail_show'),
    url(ur'^detail/(?P<uid>(\w+)).zip$', 'detail.detail_show_zip'),
    url(ur'^detail/(?P<uid>(\w+))/$', 'detail.detail'),
    url(ur'^force_detail/(?P<uid>(\w+))/$', 'detail.build_detail_html'),
    url(ur'^index/(?P<query>(?!_)(?!-)(?!.*?_/$)(?!.*?-/$)[\-a-zA-Z0-9_\u4e00-\u9fa5]+)/$',
        'views.index'),
    url(ur'^lazy/$', 'views.lazy'),
    url(ur'^retrieve/$', 'views.retrieve'),
    url(ur'^search/$', 'views.search'),
    url(ur'^selection/(?P<sid>(\w+))/$', 'views.selection'),
    url(ur'^sindex/$', 'views.sindex'),

    url(r'^kickass', include('kickass.urls')),

    # single page
    (r'^sitemap.xml$', index, {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+).xml$', sitemap, {'sitemaps': sitemaps}),
)

urlpatterns += patterns(
    'obtainfo.admin.common',
    # login logout
    url(r'^login/', 'login', name='login'),
    url(r'^logout/', 'logout', name='logout'),
    url(r'^poster/', 'image', name='poster'),
)

urlpatterns += patterns(
    'obtainfo.admin.server',
    # common
    url(r'^admin/top/$', 'mark_top', name='mark_top'),
    url(r'^admin/recommend/$', 'mark_recommend', name='mark_recommend'),
)

if settings.LOCATION == 'LOCAL':
    from putty.urls import putty_urlpatterns

    urlpatterns += putty_urlpatterns

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT})
    )
