from django import forms
from .models import *
from django.conf import settings
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.forms import widgets

class RelatedFieldWidgetCanAdd(widgets.Select):

   def __init__(self, related_model, related_url=None, *args, **kw):

       super(RelatedFieldWidgetCanAdd, self).__init__(*args, **kw)

       if not related_url:
           rel_to = related_model
           info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
           related_url = 'admin:%s_%s_add' % info

       # Be careful that here "reverse" is not allowed
       self.related_url = related_url

   def render(self, name, value, *args, **kwargs):
       self.related_url = reverse(self.related_url)
       output = [super(RelatedFieldWidgetCanAdd, self).render(name, value, *args, **kwargs)]
       output.append('<a href="%s?&_popup=1" title="Add Another" class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' % \
           (self.related_url, name))
       output.append('<img src="%sadmin/img/icon-addlink.svg" width="10" height="10" alt="%s"/></a>' % (settings.STATIC_URL, 'Add Another'))
       return mark_safe(''.join(output))
