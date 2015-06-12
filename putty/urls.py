#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings

putty_urlpatterns = patterns('putty.admin.local',
    # admin local aside
    url(r'^admin/process_image/$', 'process_image', name='process_image'),
    url(r'^admin/process_bt/$', 'process_bt', name='process_bt'),
    url(r'^admin/process_ed2k/$', 'process_ed2k', name='process_ed2k'),
    
    url(r'^admin/$', 'admin', name='list'),
    
    url(ur'^admin/selection/$', 'selection', {'work': ''}),
    url(ur'^admin/selection/(?P<work>(\w+))/$', 'selection'),
    
    url(ur'^admin/wolf/$', 'wolf'),
    url(r'^admin/(?P<collection>(\w+))/(?P<work>(\w+))/$', 'manager', name='manager'),    
)
