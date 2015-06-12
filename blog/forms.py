"""Forms for Zinnia admin"""
from django.contrib import admin
from django import forms
from django.db.models import ManyToOneRel
from django.db.models import ManyToManyRel
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

from mptt.forms import TreeNodeChoiceField

from zinnia.models.entry import Entry
from zinnia.models.category import Category
from zinnia.admin.widgets import MPTTFilteredSelectMultiple
from zinnia.admin.fields import MPTTModelMultipleChoiceField

class CustomEntryAdminForm(forms.ModelForm):
    """
    Form for Entry's Admin.
    """
    categories = MPTTModelMultipleChoiceField(
        label=_('Categories'), required=False,
        queryset=Category.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('categories'), False,
                                          attrs={'rows': '10'}))

    def __init__(self, *args, **kwargs):
        super(CustomEntryAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToManyRel(Category, 'id')
        self.fields['categories'].widget = RelatedFieldWidgetWrapper(
            self.fields['categories'].widget, rel, self.admin_site)
        self.fields['sites'].initial = [Site.objects.get_current()]
    
    def clean(self):
        cleaned_data = super(CustomEntryAdminForm, self).clean()
        featured = cleaned_data.get('featured', None)
        
        if featured == True:
            fst = cleaned_data.get('featured_short_title', None)
            fsc = cleaned_data.get('featured_short_comment', None)
            fi = cleaned_data.get('featured_image', None)
            if not fst or not fsc or not fi:
                raise forms.ValidationError("when featured=True, we must set short title and comment and image")
        
        return cleaned_data
    
    class Meta:
        """
        EntryAdminForm's Meta.
        """
        model = Entry
        fields = forms.ALL_FIELDS
