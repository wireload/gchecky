from django.conf.urls.defaults import *
from gchecky_common.models import Order

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.list_detail.object_list',
            {'queryset':Order.objects.filter(nature='digital'),
             'paginate_by':10,
             'template_name':'gchecky/digital/list.html',
             'template_object_name':'order'}),
    (r'^order/$', 'gchecky_digital.views.new_order',
                  {'template':'gchecky/digital/new.html'}),
    (r'^order/confirm/$', 'gchecky_digital.views.confirm_order',
                          {'template':'gchecky/digital/confirm.html'}),
    (r'^thanks/$', 'django.views.generic.simple.direct_to_template',
                   {'template':'gchecky/thanks.html'}),
)
