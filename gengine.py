from gxml import *
from gmodels import *

URL = 'https://%s.google.com/checkout/cws/v2/Merchant/%s/checkout'
BUTTON = 'http://%s.google.com/checkout/buttons/checkout.gif?merchant_id=%s&w=180&h=46&style=white&variant=text&loc=en_US'

class gcontroller:
    # Create the controller, specify all the needed information
    # such as merchant account credentials:
    #   - sandbox or production
    #   - google vendor ID
    #   - google merchant key
    def __init__(self, vendor_id, merchant_key, is_sandbox=True):
        self.vendor_id = vendor_id
        self.merchant_key = merchant_key
        self.is_sandbox = is_sandbox
        self.www_prefix = (is_sandbox and 'sandbox') or 'www'

    def write_message(self, msg):
        pass

    def read_message(self, something):
        pass

    def create_HMAC_SHA_signature(self, xml_text):
        import hmac, sha
        return hmac.new(self.merchant_key, xml_text, sha).digest()

    # Specify order_id to track the order
    # The order_id will be send back to us by google with order verification
    def prepare_order(self, order, order_id=None):
        from base64 import b64encode

        cart = order.toxml()

        cart64 = b64encode(cart)
        signature64 = b64encode(self.create_HMAC_SHA_signature(cart))
        html = html_order()
        html.cart = cart64
        html.signature = signature64
        html.url = URL % (self.www_prefix, self.vendor_id)
        html.button = BUTTON % (self.www_prefix, self.vendor_id)
        html.xml = cart
        return html
    
    def is_of_class(self, doc, cls):
        return doc.__class__ == cls

    MESSAGE_HANDLERS = {
        new_order_notification_t:            'on_new_order',
        order_state_change_notification_t:   'on_order_state_change',
        authorization_amount_notification_t: 'on_authorization_amount',
        risk_information_notification_t:     'on_risk_information',
        charge_amount_notification_t:        'on_charge_amount',
        refund_amount_notification_t:        'on_refund_amount',
        chargeback_amount_notification_t:    'on_chargeback_amount',
        # Message(s) that we can't possibly recieve. Handle it anyway.
        checkout_redirect_t:                 'on_checkout_redirect',
        }
    def recieve(self, input_xml):
        input = Document.fromxml(input_xml)
        on_handler = None
        if self.MESSAGE_HANDLERS.has_key(input.__class__):
            handler = self.MESSAGE_HANDLERS[input.__class__]
            on_handler = self.__class__.__dict__[handler]
            res = on_handler(self, input, input.google_order_number, input.serial_number)
        else:
            res = 'Method for %s is not implemented yet' % (input.__class__,)
        return res

    # Google sends a new order notification when a buyer places an order through Google Checkout.
    # Before shipping the items in an order, you should wait until you have also received
    # the risk information notification for that order as well as
    # the order state change notification informing you that the order's financial state
    # has been updated to CHARGEABLE.
    def on_new_order(self, new_order_notification, order_id, google_id):
        return 'on_new_order'
    def on_order_state_change(self, new_order_notification, order_id, google_id):
        return 'on_order_state_change'
    def on_authorization_amount(self, new_order_notification, order_id, google_id):
        return 'on_authorization_amount'
    # Google Checkout sends a risk information notification to provide financial information
    # that helps you to ensure that an order is not fraudulent.
    def on_risk_information(self, new_order_notification, order_id, google_id):
        return 'on_risk_information'
    def on_charge_amount(self, new_order_notification, order_id, google_id):
        return 'on_charge_amount'
    def on_refund_amount(self):
        return 'on_refund_amount'
    def on_chargeback_amount(self):
        return 'on_chargeback_amount'

    def on_checkout_redirect(self, new_order_notification, order_id, google_id):
        raise Exception('We should not recieve this method... Please report this bug.')

    def on_failed_recieve(self, input_xml, error_message):
        pass

class html_order:
    cart = None
    signature = None
    url = None
    button = None
    xml = None

def create_order():
    return checkout_shopping_cart_t(
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

if __name__ == '__main__':
    gc = gcontroller(vendor_id='your_google_sandbox_vendor_id',
                     merchant_key='your_google_merchant_key',
                     is_sandbox=True)
    order = create_order()
    html = gc.prepare_order(order)
    
    print "Input: %s" % (html.xml)
    print "--------------------"
    print gc.recieve(html.xml)


