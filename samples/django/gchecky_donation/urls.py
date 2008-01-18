from django.conf.urls.defaults import *
from gchecky_common.models import Order

from gchecky_donation import donations

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.list_detail.object_list',
            {'queryset':Order.objects.filter(nature='donation'),
             'paginate_by':10,
             'template_name':'gchecky/donation/list.html',
             'template_object_name':'order',
             'extra_context':{'donations':donations.get_available_donations()}}),
    (r'^continue/$', 'django.views.generic.simple.direct_to_template',
            {'template':'gchecky/thanks.html'}),
)
