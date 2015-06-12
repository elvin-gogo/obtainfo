#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.views.generic.dates import BaseArchiveIndexView
from django.views.generic.detail import DetailView

from zinnia.models.entry import Entry
from zinnia.views.archives import EntryArchiveMixin
from zinnia.views.mixins.entry_preview import EntryPreviewMixin
from zinnia.views.mixins.entry_protection import EntryProtectionMixin
from zinnia.views.mixins.templates import EntryQuerysetArchiveTodayTemplateResponseMixin

class EntryHotIndex(EntryArchiveMixin,
                 EntryQuerysetArchiveTodayTemplateResponseMixin,
                 BaseArchiveIndexView):
    """
    View returning the archive index.
    """
    template_name = 'zinnia/entry_list.html'
    context_object_name = 'entry_list'

class EntryFeaturedIndex(EntryArchiveMixin,
                 EntryQuerysetArchiveTodayTemplateResponseMixin,
                 BaseArchiveIndexView):
    """
    View returning the archive index.
    """
    template_name = 'zinnia/entry_list.html'
    context_object_name = 'entry_list'

class EntryDetail(EntryPreviewMixin,
                  EntryProtectionMixin,
                  DetailView):
    queryset = Entry.published.on_site()
    template_name_field = 'template'
