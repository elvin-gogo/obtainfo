#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core import paginator
from django.core.paginator import EmptyPage, PageNotAnInteger

class Page(paginator.Page):
	def __init__(self, object_list, number, paginator):
		object_list = list(object_list)
		super(Page, self).__init__(object_list, number, paginator)
	
	def __len__(self):
		try:
			return super(Page, self).__len__()
		except TypeError:
			return self.object_list.count(True)
	
	def __getitem__(self, index):
		return self.object_list[index]

class MPaginator(paginator.Paginator):
	def __len__(self):
		try:
			return super(Paginator, self).__len__()
		except TypeError:
			return self.object_list.count()
	
	def page(self, number):
		"Returns a Page object for the given 1-based page number."
		number = self.validate_number(number)
		bottom = (number - 1) * self.per_page
		top = bottom + self.per_page
		if top + self.orphans >= self.count:
			top = self.count
		return Page(self.object_list[bottom:top], number, self)

class JuncheePaginator(MPaginator):
	def __init__(self, object_list, per_page, range_num=5, orphans=0, allow_empty_first_page=True):
		MPaginator.__init__(self, object_list, per_page, orphans, allow_empty_first_page)
		self.range_num = range_num

	def page(self, number):
		if isinstance(number, str):
			self.page_num = int(number)
		else:
			self.page_num = number
		return super(JuncheePaginator, self).page(number)

	def _page_range_ext(self):
		num_count = 2 * self.range_num + 1
		if self.num_pages <= num_count:
			return range(1, self.num_pages + 1)
		
		page_num = int( self.page_num )
		num_list = []
		num_list.append(page_num)
		
		for i in range(1, self.range_num + 1):
			if page_num - i <= 0:
				num_list.append( num_count + page_num - i )
			else:
				num_list.append( page_num - i )

			if page_num + i <= self.num_pages:
				num_list.append( page_num + i )
			else:
				num_list.append( page_num + i - num_count )
		num_list.sort()
		return num_list
	page_range_ext = property(_page_range_ext)

def get_page_part(results, page=1, length=15):
	# Show 15 contacts per page
	paginator = JuncheePaginator(results, length)
	
	try:
		contacts = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		contacts = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		contacts = paginator.page(paginator.num_pages)
		
	return contacts
