from django.conf.urls.defaults import *

urlpatterns = patterns('shop.views',
    # Example:
    (r'^$', 'index'),
    (r'^notify/$', 'ghandler'),
    (r'^do/$', 'gdo'),
)
