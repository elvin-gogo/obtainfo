"""Urls for the demo of Zinnia"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import include
from django.conf.urls import patterns
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('kickass.views',
    url(r'^', 'kickass_list'),
)
