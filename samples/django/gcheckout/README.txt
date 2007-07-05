This directory contains a simple application to be used in a django project.

To use it from within your django project do the following:

1) add the directory containing shop to your PYTHONPATH (see django installation
   instructions)
2) add gcheckout' application to your django project applications list
3) do 'python manage.py syncdb' to create database tables for 'shop'
4) add 'gcheckout_vendor_id' and 'gcheckout_merchant_key' variables to your
   /settings.py file as descibed in /samples/django/settings.py.
5) derive from gcheckout.DjangoGController class and override its methods
   to implement your application logic.
6) setup an url to serve as an entry-point for google Checkout callbacks.
   Direct (through your /urls.py) the incoming requests
   to gcheckout.views.process_google_message.
7) Go to Google Checkout sandbox website (http://sandbox.google.com/checkout)
   and adjust in Settings -> Integration:
   - 'API callback URL' post externally accessible url from the step (6)
   - Callback method: XML

[Optional:]
8) test your installation by invoking 'python manage.py test'
9) go to http://groups.google.com/group/gchecky/ and post your questions there.
   :-)
*) go to http://code.google.com/p/gchecky/ and report bug, issues, feature
   requests. It would be lovely to hear from you.

Sample usage (create anapplication my_app in your project):
/my_app/__init__.py file:
========================
    from settings import gcheckout_vendor_id, gcheckout_merchant_key, gcheckout_is_sandbox
    from gcheckout import DjangoGController
    
    class MyGController(DjangoGController):
        def handle_order_state_change(self, cart, notification, previous_state, previous_payment):
            if cart.state == 'NEW':
                if cart.payment == 'CHARGEABLE':
                    if cart.total > cart.charges_pending:
                        self.charge_order(cart, cart.total - cart.charges_pending)
        def handle_charge_amount(self, cart, notification, latest_amount):
            if cart.charges == cart.total:
                if cart.state == 'NEW':
                    self.process_order(cart)
                    self.deliver_order(cart, send_email=True)
    
    my_controller = None
    def get_my_controller():
        from my_app import my_controller
        if my_controller is None:
            my_controller = MyGController(gcheckout_vendor_id,
                                          gcheckout_merchant_key,
                                          gcheckout_is_sandbox)
        return my_controller

/urls.py file:
=============
    from django.conf.urls.defaults import *
    
    from my_app import get_my_controller
    
    urlpatterns = patterns('',
        # setup Google Checkout entry point
        (r'^google/checkout/$', 'gcheckout.views.process_google_message',
                                {'controller':get_my_controller()}),
        ...
    )

