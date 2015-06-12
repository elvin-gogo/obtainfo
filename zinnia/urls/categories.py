"""Urls for the Zinnia categories"""
from django.conf.urls import url
from django.conf.urls import patterns
from django.views.decorators.cache import cache_page

from zinnia.urls import _
from zinnia.views.categories import CategoryList
from zinnia.views.categories import CategoryDetail


urlpatterns = patterns(
    '',
    url(_(r'^(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$'),
        cache_page(60 * 60)(CategoryDetail.as_view()),
        name='zinnia_category_detail_paginated'),
    url(r'^(?P<path>[-\/\w]+)/$',
        cache_page(60 * 60)(CategoryDetail.as_view()),
        name='zinnia_category_detail'),
)
