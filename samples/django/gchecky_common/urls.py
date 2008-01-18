from django.conf.urls.defaults import *
from gchecky_common.models import Order

urlpatterns = patterns('',
    (r'^order/(?P<order_id>\d+)/$', 'gchecky_common.views.order_details',
                                    {'template':'gchecky/order.html',
                                     'template_object':'order'}),
)

