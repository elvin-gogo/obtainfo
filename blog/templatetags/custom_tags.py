#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Template tags and filters for Zinnia"""
import re
from hashlib import md5
from datetime import date
from datetime import timedelta
try:
    from urllib.parse import urlencode
except ImportError:  # Python 2
    from urllib import urlencode

from django.db.models import Q
from django.db.models import Count
from django.conf import settings
from django.utils import timezone
from django.template import Library
from django.utils.encoding import smart_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.html import conditional_escape
from django.template.defaultfilters import stringfilter
from django.contrib.auth import get_user_model
from django.contrib.comments.models import CommentFlag
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments import get_model as get_comment_model

from tagging.models import Tag
from tagging.utils import calculate_cloud

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.managers import DRAFT
from zinnia.managers import tags_published
from zinnia.flags import PINGBACK, TRACKBACK
from zinnia.settings import PROTOCOL
from zinnia.comparison import VectorBuilder
from zinnia.comparison import pearson_score
from zinnia.calendar import Calendar
from zinnia.breadcrumbs import retrieve_breadcrumbs

register = Library()

@register.inclusion_tag('zinnia/tags/dummy.html')
def hot_tab(number=8, template='zinnia/tags/hot_tab.html'):
    """
    Return the published hot_tab content.
    今年热门，当月热门，最新文章，大家都在看，当月热评，今年热评
    """
    today = date.today()
    year = today.year - 1
    if today.month == 1:
        month = 12
    else:
        month = today.month - 1
    
    year_hot = Entry.published.filter(creation_date__gte=str(date(year, 1, 1))).order_by('-access')[:number]
    
    month_hot = Entry.published.filter(creation_date__gte=str(date(year, month, 1))).order_by('-access')[:number]
    
    recent = Entry.published.all()[:number]
    
    access = Entry.published.filter(creation_date__gte=str(today - timedelta(days=14))).order_by('-access')[:number]
    
    year_hot_comment = Entry.published.filter(creation_date__gte=str(date(year, 1, 1))).order_by('-comment_count')[:number]
    
    month_hot_comment = Entry.published.filter(creation_date__gte=str(date(year, month, 1))).order_by('-comment_count')[:number]
    
    tab = [
        {'id':'year_hot', 'name':u'%d年热门' % today.year, 'entries':year_hot},
        {'id':'month_hot', 'name':u'%d月热门' % today.month, 'entries':month_hot},
        {'id':'recent', 'name':u'最新文章', 'entries':recent},
        {'id':'access', 'name':u'大家都在看', 'entries':access},
        {'id':'year_hot_comment', 'name':u'%d年热门评论' % today.year, 'entries':year_hot_comment},
        {'id':'month_hot_comment', 'name':u'%d月热门评论' % today.month, 'entries':month_hot_comment},
    ]
    
    return {'template': template, 'entries': tab}

@register.inclusion_tag('zinnia/tags/dummy.html')
def hot_player(number=10, template='zinnia/tags/hot_player.html'):
    """
    编辑推荐的滚轮
    """
    
    return {'template': template, 'entries': Entry.published.filter(featured=True)[:number]}
