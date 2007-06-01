This directory contains a simple application to be used in a django project.

To use it from within your django project do the following:

1) add the directory containing shop to your PYTHONPATH (see django installation
   instructions)
2) add shop application to your django project applications list
3) add 'shop/template/' directory to your template directory list (use absolute
   path to 'shop/template/')
4) do 'python manage.py syncdb' to create database tables for 'shop'
5) add 'gcheckout_vendor_id' and 'gcheckout_merchant_key' variables to your
   /settings.py file as descibed in /samples/shop/settings.py.
6) include shop.urls in your project urls like in:
    (r'^shop/', include('shop.urls')),
   or do it manually for every method from shop/views.py.
7) Go to Google Checkout sandbox website (http://sandbox.google.com/checkout)
   and adjust in Settings -> Integration:
   - 'API callback URL' post externally accessible url that is handled by
     shop.view.ghandler method (take a look at shop/urls.py).
   - Callback method: XML

[Optional:]
8) Go to http://groups.google.com/group/gchecky/ and post your questions there.
   :-)
9) Go to http://code.google.com/p/gchecky/ and report bug, issues, feature
   requests. It would be lovely to hear from you.

