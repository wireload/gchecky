from base64 import b64encode
import urllib2

from gchecky import gxml
from gchecky import model as gmodel

HTML = """
<form method="POST" action="%s">
    <input type="hidden" name="cart" value="%s" />
    <input type="hidden" name="signature" value="%s" />
    <input type="image" src="%s" border="0" alt="Google Checkout" /> 
</form>
"""

class ProcessingException(Exception):
    def __init__(self, message, where=''):
        self.where = where
        return Exception.__init__(self, message)

class html_order(object):
    cart = None
    signature = None
    url = None
    button = None
    xml = None
    html = None

class ControllerLevel_1(object):
    SANDBOX_URLS    = {'CHECKOUT_BUTTON': 'https://sandbox.google.com/checkout/buttons/checkout.gif?merchant_id=%s&w=180&h=46&style=white&variant=text',
                       'CLIENT_POST_CART':'https://sandbox.google.com/checkout/api/checkout/v2/checkout/Merchant/%s',
                       'SERVER_POST_CART':'https://sandbox.google.com/checkout/api/checkout/v2/merchantCheckout/Merchant/%s',
                       'ORDER_PROCESSING':'https://sandbox.google.com/checkout/api/checkout/v2/request/Merchant/%s'
                       }
    PRODUCTION_URLS = {'CHECKOUT_BUTTON': 'https://checkout.google.com/buttons/checkout.gif?merchant_id=%s&w=180&h=46&style=white&variant=text',
                       'CLIENT_POST_CART':'https://checkout.google.com/api/checkout/v2/checkout/Merchant/%s',
                       'SERVER_POST_CART':'https://checkout.google.com/api/checkout/v2/merchantCheckout/Merchant/%s',
                       'ORDER_PROCESSING':'https://checkout.google.com/api/checkout/v2/request/Merchant/%s'
                       }
    # Specify all the needed information such as merchant account credentials:
    #   - sandbox or production
    #   - google vendor ID
    #   - google merchant key
    def __init__(self, vendor_id, merchant_key, is_sandbox=True):
        self.vendor_id = vendor_id
        self.merchant_key = merchant_key
        self.is_sandbox = is_sandbox

    def get_url(self, tag):
        urls = (self.is_sandbox and self.SANDBOX_URLS
                              ) or self.PRODUCTION_URLS
        if urls.has_key(tag):
            return urls[tag]
        raise Exception('Unknown url tag "' + tag + '"')

    def get_client_post_cart_url(self):
        return self.get_url('CLIENT_POST_CART_URL') % (self.vendor_id,)
    get_cart_post_url = get_client_post_cart_url

    def get_server_post_cart_url(self):
        return self.get_url('SERVER_POST_CART_URL') % (self.vendor_id,)

    def get_checkout_button_url(self):
        return self.get_url('CHECKOUT_BUTTON') % (self.vendor_id,)
    get_cart_post_button = get_checkout_button_url

    def create_HMAC_SHA_signature(self, xml_text):
        import hmac, sha
        return hmac.new(self.merchant_key, xml_text, sha).digest()

    # Specify order_id to track the order
    # The order_id will be send back to us by google with order verification
    def prepare_order(self, order, order_id=None):
        cart = order.toxml()

        cart64 = b64encode(cart)
        signature64 = b64encode(self.create_HMAC_SHA_signature(cart))
        html = html_order()
        html.cart = cart64
        html.signature = signature64
        html.url = self.get_cart_post_url()
        html.button = self.get_checkout_button_url()
        html.xml = cart
        html.html = HTML % (html.url, html.cart, html.signature, html.button)
        return html

class ControllerLevel_2(ControllerLevel_1):
    def get_order_processing_url(self):
        return self.get_url('ORDER_PROCESSING') % (self.vendor_id,)
    get_api_level2_url = get_order_processing_url

    def send_xml(self, msg):
        req = urllib2.Request(url=self.get_order_processing_url(),
                              data=msg)
        req.add_header('Authorization',
                       'Basic %s' % (b64encode('%s:%s' % (self.vendor_id,
                                                          self.merchant_key)),))
        req.add_header('Content-Type', ' application/xml; charset=UTF-8')
        req.add_header('Accept', ' application/xml; charset=UTF-8')
        try:
            response = urllib2.urlopen(req).read()
        except urllib2.HTTPError, error:
            response = error.fp.read()
        return response

    def send_message(self, message):
        message_xml = message.toxml()
        response_xml = self.send_xml(message_xml)
        return self.process_message_result(message_xml, response_xml)

    def process_message_result(self, message_xml, response_xml):
        doc = gxml.Document.fromxml(response_xml)
        if doc.__class__ != gmodel.request_received_t:
            if doc.__class__ != gmodel.error_t:
                # OMG! Unknown message!
                raise Exception, 'SEVERE ERROR! THE GCHECKY LIBRARY DOES NOT FUNCTION PROPERLY'
            msg = 'Error message from GCheckout API:\n%s' % (doc.error_message, )
            if doc.warning_messages:
                tmp = ''
                for warning in doc.warning_messages:
                    tmp += '\n%s' % (warning,)
                msg += ('Additional warnings:%s' % (tmp,))
            raise Exception(msg)
        if doc.__class__ != gmodel.request_received_t:
            raise Exception("%s" % (doc.serial_number,))

    def archive_order(self, order_id):
        self.send_message(
            gmodel.archive_order_t(google_order_number=order_id))
    def unarchive_order(self, order_id):
        self.send_message(
            gmodel.unarchive_order_t(google_order_number=order_id))

    def send_buyer_message(self, order_id, message):
        self.send_message(gmodel.send_buyer_message_t(
            google_order_number = order_id,
            message = message,
            send_email = True
            ))

    def add_merchant_order_number(self, order_id, merchant_order_number):
        self.send_message(gmodel.add_merchant_order_number_t(
            google_order_number = order_id,
            merchant_order_number = merchant_order_number
            ))

    def add_tracking_data(self, order_id, carrier, tracking_number):
        self.send_message(gmodel.add_tracking_data_t(
            google_order_number = order_id,
            tracking_data = gmodel.tracking_data_t(carrier         = carrier,
                                                   tracking_number = tracking_number)
            ))

    def charge_order(self, order_id, amount):
        self.send_message(gmodel.charge_order_t(
            google_order_number = order_id,
            amount = gmodel.price_t(value = amount, currency = 'GBP')
            ))

    def refund_order(self, order_id, amount, reason, comment=None):
        self.send_message(gmodel.refund_order_t(
            google_order_number = order_id,
            amount = gmodel.price_t(value = amount, currency = 'GBP'),
            reason = reason,
            comment = comment or None
            ))

    def authorize_order(self, order_id, do_in_production=False):
        if do_in_production or self.is_sandbox:
            self.send_message(gmodel.authorize_order_t(
                google_order_number = order_id
            ))

    def cancel_order(self, order_id, reason, comment=None):
        self.send_message(gmodel.cancel_order_t(
            google_order_number = order_id,
            reason = reason,
            comment = comment or None
            ))

    def process_order(self, order_id):
        self.send_message(gmodel.process_order_t(
            google_order_number = order_id
            ))

    def deliver_order(self, order_id,
                      carrier = None, tracking_number = None,
                      send_email = None):
        tracking = None
        if carrier or tracking_number:
            tracking = gmodel.tracking_data_t(carrier         = carrier,
                                              tracking_number = tracking_number)
        self.send_message(gmodel.deliver_order_t(
            google_order_number = order_id,
            tracking_data = tracking,
            send_email = send_email or None
            ))

    def is_of_class(self, doc, cls):
        return doc.__class__ == cls

    MESSAGE_HANDLERS = {
        gmodel.new_order_notification_t:            'on_new_order',
        gmodel.order_state_change_notification_t:   'on_order_state_change',
        gmodel.authorization_amount_notification_t: 'on_authorization_amount',
        gmodel.risk_information_notification_t:     'on_risk_information',
        gmodel.charge_amount_notification_t:        'on_charge_amount',
        gmodel.refund_amount_notification_t:        'on_refund_amount',
        gmodel.chargeback_amount_notification_t:    'on_chargeback_amount',
        # Message(s) that we can't possibly recieve. Handle it anyway.
        gmodel.checkout_redirect_t:                 'on_checkout_redirect',
        }
    # This method gets a string and resturns a string
    # TODO ?? what about iterators, etc?
    def process(self, input_xml):
        try:
            input = gxml.Document.fromxml(input_xml)
            on_handler = None
            if self.MESSAGE_HANDLERS.has_key(input.__class__):
                handler = self.MESSAGE_HANDLERS[input.__class__]
                on_handler = getattr(self, handler)
                res = on_handler(input, input.google_order_number)
            else:
                res = 'Method for %s is not implemented yet' % (input.__class__,)
            return str(res or gmodel.ok_t())
        except Exception, exc:
            xml_text = gmodel.error_t(serial_number = 'error',
                                      error_message = str(exc)).toxml()
            import traceback
            raise ProcessingException(xml_text, where=traceback.format_exc())

    # Google sends a new order notification when a buyer places an order through Google Checkout.
    # Before shipping the items in an order, you should wait until you have also received
    # the risk information notification for that order as well as
    # the order state change notification informing you that the order's financial state
    # has been updated to CHARGEABLE.
    def on_new_order(self, notification, order_id):
        return 'on_new_order'
    def on_order_state_change(self, notification, order_id):
        return 'on_order_state_change'
    def on_authorization_amount(self, notification, order_id):
        return 'on_authorization_amount'
    # Google Checkout sends a risk information notification to provide financial information
    # that helps you to ensure that an order is not fraudulent.
    def on_risk_information(self, notification, order_id):
        return 'on_risk_information'
    def on_charge_amount(self, notification, order_id):
        return 'on_charge_amount'
    def on_refund_amount(self, notification, order_id):
        return 'on_refund_amount'
    def on_chargeback_amount(self, notification, order_id):
        return 'on_chargeback_amount'
    def on_checkout_redirect(self, notification, order_id):
        raise Exception('We should never recieve this... this is a bug.')

# Just an alias with a shorter name.
Controller = ControllerLevel_2
