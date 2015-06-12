"""Callable Queryset mixins for Zinnia views"""
from django.core.exceptions import ImproperlyConfigured

from zinnia.models.entry import Entry

class CallableQuerysetMixin(object):
    """
    Mixin for handling a callable queryset,
    which will force the update of the queryset.
    Related to issue http://code.djangoproject.com/ticket/8378
    """
    queryset = None

    def get_context_data(self, **kwargs):
        context = super(CallableQuerysetMixin, self).get_context_data(**kwargs)
        context['special_flag'] = self.request.GET.get('special', '')
        return context
    
    def get_queryset(self):
        """
        Check that the queryset is defined and call it.
        """
        special = self.request.GET.get('special', None)
        
        if special == 'hot':
            self.queryset = Entry.published.all().filter(comment_count__gt=0)
        elif special == 'featured':
            self.queryset = Entry.published.all().filter(featured=True)
        else:
            self.queryset = Entry.published.all()
            
        if self.queryset is None:
            raise ImproperlyConfigured(
                "'%s' must define 'queryset'" % self.__class__.__name__)
        
        return self.queryset
