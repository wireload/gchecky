from gmodels import *
from gengine import *

# This example file shows how to interface with Google Checkout XML services
# without messing with XML. It is all being taken care of by gchecky.

# File examply_xml_messages.py provides sample notification messages from
# google checkout.

# For a working version the class gcontroller should be implemented to update
# the company database with the information recieved. It should be also hooked
# into web server to recieve the messages from google checkout xml services
# (an XML service -- will be detailed in another example).

# The script simply creates/parses/validates XML by using gchecky.
# Google checkout XML interface schema is implemented in gmodel.py.
# Have a look for any explanations.


an_order = checkout_shopping_cart_t(
        shopping_cart=shopping_cart_t(items=[
            item_t(name='Test_Item_1',
                   description='Test Item 1 for testing purposes.',
                   unit_price=price_t(value=1.55, currency='GBP'),
                   quantity=3),
            item_t(name='Test_Item_2',
                   description='Test Item 2 for testing purposes.',
                   unit_price=price_t(value=5.23, currency='GBP'),
                   quantity=2),
                   ]),
        checkout_flow_support=checkout_flow_support_t(
            continue_shopping_url='http://www.yahoo.com/',
            request_buyer_phone_number=False))

# custom version of controller
class MyController(gcontroller):
    # Helper -- dumps the recieved info
    def _dump_notification_info(self, str, notification, order_id, google_id):
        print 'NOTIFICATION: %s (%s, %s):' % (str, order_id, google_id)
        print '%s' % (notification.toxml())
        print '<<<<<<<<<<<<<<<<'

    # Override gcontroller handlers to dump the info about notifications
    def on_new_order(self, notification, order_id, google_id):
        self._dump_notification_info('on_new_order', notification, order_id, google_id)
    def on_order_state_change(self, notification, order_id, google_id):
        self._dump_notification_info('on_order_state_change', notification, order_id, google_id)
    def on_authorization_amount(self, notification, order_id, google_id):
        self._dump_notification_info('on_authorization_amount', notification, order_id, google_id)
    def on_risk_information(self, notification, order_id, google_id):
        self._dump_notification_info('on_risk_information', notification, order_id, google_id)
    def on_charge_amount(self, notification, order_id, google_id):
        self._dump_notification_info('on_charge_amount', notification, order_id, google_id)
    def on_refund_amount(self):
        self._dump_notification_info('on_refund_amount', notification, order_id, google_id)
    def on_chargeback_amount(self):
        self._dump_notification_info('on_chargeback_amount', notification, order_id, google_id)

my_controller = MyController(vendor_id='your_google_vendor_id',
                             merchant_key='your_google_merchant_key',
                             is_sandbox=True)

order_prepared = my_controller.prepare_order(an_order)

import example_xml_messages as xml_messages

# This information should be used on initial html page which shown
# the starting point for order placement: cart, google checkout button,
# and encoded XML data that describes the order.
print 'NEW ORDER:'
print '%s' % (order_prepared.xml)
print 'Cart XML base64-encoded: %s' % (order_prepared.cart)
print 'Cart signature base64-encoded: %s' % (order_prepared.signature)
print 'Url to post to: %s' % (order_prepared.url)
print 'Button url to be shown (Google checkout button): %s' % (order_prepared.button)
print '>>>>>>>>>>>>>>>'

# After the user have actually submitted an order to google checkout, the following
# notification will be send to our site by google:
input_xml = xml_messages.new_order_notification_xml
my_controller.recieve(input_xml)

# Google checkout changes the order state to 'REVIEWING'.
input_xml = xml_messages.order_state_change_notification_xml
my_controller.recieve(input_xml)

# Google checkout send risk evaluation info.
input_xml = xml_messages.risk_information_notification_xml
my_controller.recieve(input_xml)

# We are authorized to charge the user for the order.
input_xml = xml_messages.authorization_amount_notification_xml
my_controller.recieve(input_xml)

print 'The rest is yet to be written ;-)'
