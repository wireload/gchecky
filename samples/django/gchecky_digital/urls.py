from django.conf.urls.defaults import *
from gchecky_common.models import Order

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.list_detail.object_list',
            {'queryset':Order.objects.filter(nature='digital'),
             'paginate_by':10,
             'template_name':'gchecky/digital/list.html',
             'template_object_name':'order'}),
    (r'^item/$', 'django.views.generic.simple.redirect_to',
                  {'url':'/digital/order/'}),
    (r'^item/(?P<item_id>\d+)/$', 'gchecky_digital.views.item_details',
                                  {'template':'gchecky/digital/item.html',
                                   'template_object':'item'}),
    (r'^order/$', 'gchecky_digital.views.new_order',
                  {'template':'gchecky/digital/new.html'}),
    (r'^order/confirm/$', 'gchecky_digital.views.confirm_order',
                          {'template':'gchecky/digital/confirm.html'}),
    (r'^thanks/$', 'django.views.generic.simple.direct_to_template',
                   {'template':'gchecky/thanks.html'}),
)
