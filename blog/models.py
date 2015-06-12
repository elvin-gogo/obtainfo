"""Base entry models for Zinnia"""
from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from zinnia.settings import UPLOAD_TO
from zinnia.models_bases.entry import CoreEntry, ContentEntry, DiscussionsEntry, \
    RelatedEntry, ExcerptEntry, ImageEntry, FeaturedEntry, AuthorsEntry, CategoriesEntry, \
    TagsEntry, LoginRequiredEntry, PasswordRequiredEntry, ContentTemplateEntry, DetailTemplateEntry
from filebrowser.fields import FileBrowseField

class CustomContentEntry(ContentEntry):
    """
    Abstract model class to mark entries as featured.
    """
    access = models.IntegerField(_('access'), default=0)
    access_total = models.IntegerField(_('access toal'), default=0)
    access_year = models.IntegerField(_('access last year'), default=0)
    access_month = models.IntegerField(_('access last month'), default=0)
    access_week = models.IntegerField(_('access last week'), default=0)
    
    class Meta:
        abstract = True

class CustomFeaturedEntry(FeaturedEntry):
    """
    Abstract model class to mark entries as featured.
    """
    featured_short_title = models.CharField(
        _('short name'), max_length=50,
        blank=True, null=True,
        help_text=_('short title for featured entry.'))
    
    featured_short_comment = models.CharField(
        _('short comment'), max_length=150,
        blank=True, null=True,
        help_text=_('short comment for featured entry.'))
    
    featured_date = models.DateTimeField(
        _('last update'), default=timezone.now)
    
    featured_image = FileBrowseField("Image", max_length=200,
        directory='featured_image', extensions=['.jpg','.jpeg','.gif','.png'],
        blank=True, null=True,
        help_text=_('Used for illustration. image size : 300 x 200'))
    
    class Meta:
        abstract = True

class CustomExcerptEntry(models.Model):
    """
    Abstract model class to add an excerpt to the entries.
    """
    excerpt = models.TextField(
        _('excerpt'), blank=True, null=True,
        help_text=_('Used for search and SEO.'))

    class Meta:
        abstract = True

class CustomImageEntry(models.Model):
    """
    Abstract model class to add an image to the entries.
    """
    image = FileBrowseField("Image", max_length=200, directory='banner',
        blank=True, null=True,
        extensions=['.jpg','.jpeg','.gif','.png'],
        help_text=_('Used for illustration. hoped size 650 x 130'))
    
    class Meta:
        abstract = True

class AbstractEntry(
        CoreEntry,
        CustomContentEntry,
        DiscussionsEntry,
        RelatedEntry,
        CustomExcerptEntry,
        CustomImageEntry,
        CustomFeaturedEntry,
        AuthorsEntry,
        CategoriesEntry,
        TagsEntry,
        LoginRequiredEntry,
        PasswordRequiredEntry,
        ContentTemplateEntry,
        DetailTemplateEntry):
    @property
    def short_url(self):
        return reverse('zinnia_entry_detail', args=[self.slug])
    
    @models.permalink
    def get_absolute_url(self):
        return ('zinnia_entry_detail', (), {'slug': self.slug})
    
    class Meta(CoreEntry.Meta):
        abstract = True
