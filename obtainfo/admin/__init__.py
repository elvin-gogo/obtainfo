#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin

from obtainfo.models import SearchKey, MovieInfo, BigPoster, Series
from obtainfo.admin.common import MovieInfoAdmin, SearchKeyAdmin, BigPosterAdmin, SeriesAdmin

admin.site.register(Series, SeriesAdmin)
admin.site.register(SearchKey, SearchKeyAdmin)
admin.site.register(BigPoster, BigPosterAdmin)
admin.site.register(MovieInfo, MovieInfoAdmin)
