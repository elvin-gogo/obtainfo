#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from zinnia.models.entry import Entry
from zinnia.admin.entry import EntryAdmin

from .forms import CustomEntryAdminForm

class EntryGalleryAdmin(EntryAdmin):
    form = CustomEntryAdminForm
    
    fieldsets = (
        (_('Featured'), {
            'fields': ('featured', 'featured_short_title', 'featured_image', 'featured_short_comment')}),
        (_('Content'), {
            'fields': (('title', 'slug'), 'status', 'image', 'excerpt', 'content', 'authors', 'related')}),
        (None, {'fields': ('categories', 'tags')}),
        (_('Publication'), {
            'fields': (('start_publication', 'end_publication'),
                       'creation_date', 'sites'),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Discussions'), {
            'fields': ('comment_enabled', 'pingback_enabled',
                       'trackback_enabled'),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Privacy'), {
            'fields': ('login_required', 'password'),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Templates'), {
            'fields': ('content_template', 'detail_template'),
            'classes': ('collapse', 'collapse-closed')}))

    def mark_featured(self, request, queryset):
        """
        Mark selected as featured post.
        """
        failed = list()
        for entry in queryset:
            if entry.featured_short_title and entry.featured_short_comment and entry.featured_image:
                entry.update(featured_date=datetime.datetime.now(), featured=True)
            else:
                failed.append(entry.title)
        
        self.message_user(
            request, _('Selected entries are now marked as featured. but these failed %s.' % "\n".join(failed)))
    mark_featured.short_description = _('Mark selected entries as featured')

admin.site.unregister(Entry)
admin.site.register(Entry, EntryGalleryAdmin)
