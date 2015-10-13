#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
from functools import update_wrapper

from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
# from mptt.admin import MPTTModelAdmin as DjangoMpttAdmin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.admin.options import csrf_protect_m
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, NoReverseMatch
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.forms import AdminAuthenticationForm

from django.conf import settings
from django.core.files.images import ImageFile

try:
    from django.contrib.admin.options import IS_POPUP_VAR
except ImportError:
    # Django 1.4 and 1.5
    from django.contrib.admin.views.main import IS_POPUP_VAR

from pcnile.http import json, JsonResponse

from obtainfo.models import SearchKey, MovieInfo, BigPoster, Series


class SeriesInline(admin.TabularInline):
    model = Series
    exclude = ('title', 'level',)


class SeriesAdmin(DjangoMpttAdmin):
    exclude = ('title', 'level',)
    raw_id_fields = ('parent',)
    inlines = [SeriesInline, ]


class SearchKeyAdmin(admin.ModelAdmin):
    pass


class BigPosterAdmin(admin.ModelAdmin):
    pass


class MovieInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'visitor', 'zip_visitor', 'recommend', 'top']
    list_filter = ['recommend', 'top'] # 下拉选择过滤列表可能很大，导致数据库全表扫描和全表下载到客户端。
    search_fields = ['id', 'title', ]
    actions = ['mark_recommend', 'mark_top']

    def mark_recommend(self, request, queryset):
        for entry in queryset:
            entry.recommend = not entry.recommend
            entry.save()
        self.message_user(request, u"设置成功")

    mark_recommend.short_description = u'把所选的项目标记为推荐'

    def mark_top(self, request, queryset):
        for entry in queryset:
            entry.top = not entry.top
            entry.save()
        self.message_user(request, u"设置成功")

    mark_top.short_description = u'把所选的项目标记为置顶'


@csrf_exempt
@never_cache
def image(request):
    try:
        fil = request.FILES["file"]
        img = ImageFile(fil)
        width, height = img.width, img.height
    except Exception as e:
        return JsonResponse({'status': 'fail', 'stage': '1', 'reason': str(e)})

    try:
        with open(os.path.join(settings.IMAGE_DIR, fil.name), 'wb') as f:
            for chunk in fil.chunks():
                f.write(chunk)

        return JsonResponse({'status': 'success', 'width': width, 'height': height})
    except Exception as e:
        return JsonResponse({'status': 'fail', 'stage': '2', 'reason': str(e)})


@csrf_protect
@never_cache
def login(request):
    from django.contrib.auth.views import login

    context = {
        'title': _('Log in'),
        'app_path': request.get_full_path(),
        REDIRECT_FIELD_NAME: request.GET.get('next', '/admin/'),
    }

    defaults = {
        'extra_context': context,
        'current_app': 'name',
        'authentication_form': AdminAuthenticationForm,
        'template_name': 'login.html',
    }

    return login(request, **defaults)


@never_cache
def logout(request):
    from django.contrib import auth

    auth.logout(request)
    return HttpResponseRedirect(reverse('login'))
