#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bson.objectid import ObjectId
from django.conf import settings
from django.db import models
from filebrowser.fields import FileBrowseField
from mptt.models import MPTTModel, TreeForeignKey


class MovieInfo(models.Model):
	id = models.CharField(max_length=24, primary_key=True)
	title = models.CharField(max_length=256, null=False)
	visitor = models.IntegerField(default=0, db_index=True)
	zip_visitor = models.IntegerField(default=0, db_index=True)
	top = models.BooleanField(default=False, db_index=True)
	recommend = models.BooleanField(default=False, db_index=True)
	timestamp = models.DateTimeField()
	image = FileBrowseField("Image", max_length=200,
		directory='200_92', extensions=['.jpg','.jpeg','.gif','.png'],
		blank=True, null=True)

	def __unicode__(self):
		return self.title

class SearchKey(models.Model):
	key = models.CharField(max_length=32)
	
	def __unicode__(self):
		return self.key

class BigPoster(models.Model):
	link = models.URLField(max_length=512)
	image = models.URLField(max_length=512)
	title = models.CharField(max_length=64, default='')
	timestamp = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return self.title

class Series(MPTTModel):
	title = models.CharField(max_length=256, blank=True)
	id = models.CharField(max_length=24, primary_key=True) # Mongodb _id
	sequence = models.IntegerField()
	level = models.IntegerField(default=0)
	parent = TreeForeignKey('self', null=True, blank=True, related_name='Series',)
	
	class MPTTMeta:
		order_insertion_by = ['sequence']

	def __unicode__(self):
		return self.title
	
	def save(self, *args, **kwargs):
		try:
			collection = settings.MONGOINFO
			self.title = collection.find_one({'_id':ObjectId(self.id)}, {'title':1})['title']
		except:
			raise ValueError('get movie or tv title for series fail')
		
		super(Series, self).save(*args, **kwargs)
