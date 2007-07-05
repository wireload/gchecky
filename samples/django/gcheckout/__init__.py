import traceback

from gcheckout.models import Cart, Item, Message

from gchecky import model as gmodel
from gchecky.controller import Controller, ControllerLevel_2, ProcessingException
from gchecky.gxml import Document

# This is a helper class that should not be used directly by user code.
# Instead have a look at DjangoGController below
class DjangoGControllerImpl(Controller):
    def on_new_order(self, notification, order_id):
        # create a cart
        if Cart.objects.filter(google_id = order_id).count() > 0:
            raise Exception, ('Cart with google_id(%s) already exist' % (order_id,))
        cart = Cart(google_id = order_id,
                    xml       = notification.toxml(),
                    state     = notification.fulfillment_order_state,
                    payment   = notification.financial_order_state,
                    total     = notification.order_total.value)
        cart.save()
        # parse cart items
        items = [Item(cart        = cart,
                      name        = item.name,
                      description = item.description,
                      price       = item.unit_price.value,
                      currency    = item.unit_price.currency,
                      quantity    = item.quantity,
                      merchant_id = item.merchant_item_id,
                      merchant_data = str(item.merchant_private_item_data))
                 for item in notification.shopping_cart.items]
        for item in items:
            item.save()
        # call user event handler
        return self.handle_new_order(cart = self._get_cart(order_id),
                                     notification = notification)

    def on_order_state_change(self, notification, order_id):
        cart = self._get_cart(order_id)
        cart.state = notification.new_fulfillment_order_state
        cart.payment = notification.new_financial_order_state
        return self.handle_order_state_change(cart = cart,
                                              notification = notification,
                                              previous_state = notification.previous_fulfillment_order_state,
                                              previous_payment = notification.previous_financial_order_state)

    def on_authorization_amount(self, notification, order_id):
        cart = self._get_cart(order_id)
        cart.authorized += notification.authorization_amount.value
        cart.save()
        return self.handle_authorization_amount(cart = cart,
                                                notification = notification,
                                                amount = notification.authorization_amount.value,
                                                avs = notification.avs_response,
                                                cvn = notification.cvn_response)
    def on_risk_information(self, notification, order_id):
        cart = self._get_cart(order_id)
        return self.handle_risk_information(cart,
                                            notification = notification)
    def on_charge_amount(self, notification, order_id):
        cart = self._get_cart(order_id)
        cart.charges = float(cart.charges) + notification.latest_charge_amount.value
        if cart.charges != notification.total_charge_amount.value:
            raise AssertionError, 'Total charged amount does not match!'
        cart.save()
        return self.handle_charge_amount(cart = cart,
                                         notification = notification,
                                         latest_amount = notification.latest_charge_amount.value)

    def on_refund_amount(self, notification, order_id):
        cart = self._get_cart(order_id)
        cart.refunds += notification.latest_refund_amount.value
        if cart.refunds != notification.total_refund_amount.value:
            raise AssertionError, 'Total refunded amount does not match!'
        cart.save()
        return self.handle_refund_amount(cart = cart,
                                         notification = notification,
                                         latest_amount = notification.latest_refund_amount.value)
    def on_chargeback_amount(self, notification, order_id):
        cart = self._get_cart(order_id)
        cart.chargebacks += notification.latest_chargeback_amount.value
        if cart.chargebacks != notification.total_chargeback_amount.value:
            raise AssertionError, 'Total chargeback amount does not match!'
        cart.save()
        return self.handle_chargeback_amount(cart = cart,
                                             notification = notification,
                                             latest_amount = notification.latest_chargeback_amount.value)
    # Helper methods:
    # Retreive a cart object corresponding to order_id
    def _get_cart(self, order_id):
        # will throw an exception if no cart found with this id
        return Cart.objects.get(google_id=order_id)

    # Default implementation of the methods below is fine - add some sugar to it
    def archive_order(self, cart):
        return super(DjangoGControllerImpl, self).archive_order(cart.google_id)
    def unarchive_order(self, cart):
        return super(DjangoGControllerImpl, self).unarchive_order(cart.google_id)
    def send_buyer_message(self, cart, message):
        return super(DjangoGControllerImpl, self).send_buyer_message(cart.google_id,
                                                                 message)
    def add_merchant_order_number(self, cart, merchant_order_number):
        return super(DjangoGControllerImpl, self).add_merchant_order_number(cart.google_id,
                                                                        merchant_order_number)
    def add_tracking_data(self, cart, carrier, tracking_number):
        return super(DjangoGControllerImpl, self).add_tracking_data(cart.google_id,
                                                                carrier,
                                                                tracking_number)
    def charge_order(self, cart, amount):
        cart.charges_pending = float(cart.charges_pending) + float(amount)
        cart.save()
        return super(DjangoGControllerImpl, self).charge_order(cart.google_id,
                                                               amount)
    def refund_order(self, cart, amount, reason, comment=None):
        cart.refunds_pending = float(cart.refunds_pending) + amount
        return super(DjangoGControllerImpl, self).refund_order(cart.google_id,
                                                           amount,
                                                           reason,
                                                           comment)
    def authorize_order(self, cart, do_in_production=False):
        return super(DjangoGControllerImpl, self).authorize_order(cart.google_id,
                                                              do_in_production)
    def cancel_order(self, cart, reason, comment=None):
        return super(DjangoGControllerImpl, self).cancel_order(cart.google_id,
                                                           reason,
                                                           comment)
    def process_order(self, cart):
        # TODO ?? should not we wait for a message from GC instead?
        cart.state = 'PROCESSING'
        cart.save()
        return super(DjangoGControllerImpl, self).process_order(cart.google_id)

    def deliver_order(self, cart,
                      carrier = None, tracking_number = None,
                      send_email = None):
        # TODO ?? should not we wait for a message from GC instead?
        cart.state = 'DELIVERED'
        cart.save()
        return super(DjangoGControllerImpl, self).deliver_order(cart.google_id,
                                                            carrier,
                                                            tracking_number,
                                                            send_email)
    # Log all the messages from (and our responses to) google checkout services
    def process(self, input_xml):
        try:
            output_xml = super(DjangoGControllerImpl, self).process(input_xml)
            self.log_message_from_google(input_xml, output_xml)
            return output_xml
        except ProcessingException, exc:
            exception = exc
            error = exc.where
            print traceback.format_exc()
        except Exception, exc:
            exception = exc
            error = 'That should never happen - bug in gchecky.Controller'
        output_xml = str(exception)
        self.log_message_from_google(input_xml,
                                     output_xml,
                                     '%s\n%s' % (exception, error))
        raise exception

    # Log all our messages to (and the responses from) google checkout services
    def process_message_result(self, message_xml, response_xml):
        try:
            res = super(DjangoGControllerImpl, self).process_message_result(message_xml,
                                                                        response_xml)
            self.log_message_to_google(message_xml, response_xml)
            return res
        except ProcessingException, exc:
            exception = exc
            error = exc.where
        except Exception, exc:
            exception = exc
            error = 'That should never happen - bug in gchecky.Controller'
        self.log_message_from_google(message_xml,
                                     response_xml,
                                     '%s\n%s' % (exception, error))
        raise exception

    def log_message_to_google(self, input_xml, output_xml, error=None):
        return self.log_message('-->>', input_xml, output_xml, error)
    def log_message_from_google(self, input_xml, output_xml, error=None):
        return self.log_message('<<--', input_xml, output_xml, error)

    def log_message(self, tag, input_xml, output_xml, error=None):
        message = Message(tag        = tag,
                          input_xml  = input_xml,
                          output_xml = output_xml,
                          no_errors  = error is None,
                          comment    = error)
        try:
            log_step = 'parsing input XML'
            input_doc = Document.fromxml(input_xml)
            # message.serial_number = input_doc.serial_number
            log_step = 'looking for the corresponding cart'
            message.cart = Cart.objects.get(google_id = input_doc.google_order_number)
        except Exception, exc:
            the_error = (message.comment and (message.comment + '\n')) or ''
            log_error = 'Error in logs %s:\n%s\n%s' % (log_step,
                                                       exc,
                                                       traceback.format_exc())
            message.comment = '%s%s' % (the_error, log_error)
        message.save()


# The class to be overwritten by user to handle various messages
# from Google Checkout API.
class DjangoGController(DjangoGControllerImpl):
    def __init__(self, vendor_id, merchant_key, is_sandbox=True):
        return DjangoGControllerImpl.__init__(self, vendor_id, merchant_key, is_sandbox)

    def handle_new_order(self, cart, notification):
        pass
    def handle_order_state_change(self, cart, notification, previous_state, previous_payment):
        if cart.state == 'NEW':
            if cart.payment == 'CHARGEABLE':
                if cart.total > cart.charges_pending:
                    self.charge_order(cart, cart.total - cart.charges_pending)
    def handle_authorization_amount(self, cart, notification, amount, avs, cvn):
        pass
    def handle_risk_information(self, cart, notification):
        pass
    def handle_charge_amount(self, cart, notification, latest_amount):
        if cart.charges == cart.total:
            if cart.state == 'NEW':
                self.process_order(cart)
                self.deliver_order(cart, send_email=True)
    def handle_refund_amount(self, cart, notification, latest_amount):
        pass
    def handle_chargeback_amount(self, cart, notification, latest_amount):
        pass
#        # Message(s) that we can't possibly recieve. Handle it anyway.
#        gmodel.checkout_redirect_t:                 'on_checkout_redirect',

