from django.conf.urls.defaults import *

import settings

urlpatterns = patterns('',
    (r'^admin/', include('django.contrib.admin.urls')),

    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/path/to/media'}),

    (r'^google/checkout/$',      'gchecky_common.views.process_google_message'),
    (r'^google/checkout/test/$', 'gchecky_common.views.test_processing_message',
                                 {'template':'gchecky/test.html'}),

    (r'^common/', include('gchecky_common.urls')),

    (r'^digital/', include('gchecky_digital.urls')),

    (r'^donation/', include('gchecky_donation.urls')),

    (r'^$', 'django.views.generic.simple.direct_to_template',
            {'template':'gchecky/base.html'}),
)

