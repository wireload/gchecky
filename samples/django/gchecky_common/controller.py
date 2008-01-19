from gchecky import model as gmodel
from gchecky.controller import Controller
from gchecky.controller import GcheckyError, LibraryError, SystemError, HandlerError, DataError
from gchecky_common.models import Order, Purchase, Message

class DjangoGController(Controller):
    """
    The custom Controller that inherits from gchecky.controller.Controller.
    It implements the required abstract methods.

    Basically it logs all the conversations between our server and GC, and
    also automatically charges new orders. Nothing fancy.
    """

    def __init__(self, automatically_charge=True, *args, **kwargs):
        """
        For the sake of the Demo we add a parameter automatically_charge
        that indicates whether or not the controller should send
        a charge command to google checkout.
        If in your Google Checkout account settings you choose
         "Automatically authorize and *charge* the buyer's credit card"
        then it would be an error to send a 'charge' command to google servers.
        """
        self.automatically_charge = automatically_charge
        return super(DjangoGController, self).__init__(*args, **kwargs)

    def on_retrieve_order(self, order_id, context=None):
        """
        Get the order object from DB that corresponds to this google order id.
        Or None if no such object.
        """
        if Order.objects.filter(google_id = order_id).count() > 0:
            return Order.objects.get(google_id=order_id)
        return None

    def handle_new_order(self, message, order_id, order, context):
        """
        Create a new Order instance in the database if everything is ok.
        """
        # First verify the currency
        from settings import gcheckout_currency
        if message.order_total.currency != gcheckout_currency:
            raise Exception("Currency mismatch! %s != %s" % (
                             message.order_total.currency,
                             gcheckout_currency
                             ))
        # Check if the order already exist in the database
        if order is not None:
            raise Exception("Order with google_id('%s') already exists" % (order_id,))

        #TODO
        from gchecky_common.models import ORDER_NATURE
        merchant_data = message.shopping_cart.merchant_private_data
        nature = 'unknown'
        for (ntag, ntitle) in ORDER_NATURE:
            if ntag == merchant_data:
                nature = ntag

        # Good to create a fresh new order in DB
        if message.buyer_billing_address.contact_name is not None:
            owner_id = message.buyer_billing_address.contact_name
        elif message.buyer_billing_address.company_name is not None:
            owner_id = message.buyer_billing_address.company_name
        else:
            owner_id = message.buyer_id
        order = Order(user_id   = owner_id,
                      nature    = nature,
                      google_id = order_id,
                      cart_xml  = message.toxml(),
                      state     = message.fulfillment_order_state,
                      payment   = message.financial_order_state,
                      currency  = message.order_total.currency,
                      total     = message.order_total.value)

        # parse cart items
        purchases = [Purchase(order       = order,
                              item_xml    = 'TODO',
                              title       = item.name,
                              brief       = item.description,
                              price       = item.unit_price.value,
                              currency    = item.unit_price.currency,
                              quantity    = item.quantity,
                              merchant_id = item.merchant_item_id,
                              merchant_data = str(item.merchant_private_item_data))
                 for item in message.shopping_cart.items]

        order.save()
        for purchase in purchases:
            purchase.order = order
            purchase.save()

        return gmodel.ok_t()

    def handle_order_state_change(self, message, order_id, order, context):
        """
        React to the order state change.
        """
        assert order is not None
        if message.new_fulfillment_order_state != message.previous_financial_order_state:
            order.state = message.new_fulfillment_order_state
        if message.new_financial_order_state != message.previous_financial_order_state:
            order.payment = message.new_financial_order_state
        order.save()

        if order.state == 'NEW':
            if order.payment == 'CHARGEABLE':
                if order.total > order.charges_pending:
                    if self.automatically_charge:
                        # Only send charge command if your account does not
                        # tell google to do it automatically.
                        amount = order.total - (order.charges + order.charges_pending)
                        order.charges_pending += amount
                        self.charge_order(order_id, amount)
                        order.save()

        return gmodel.ok_t()

    def handle_charge_amount(self, message, order_id, order, context):
        """
        GC has charged this order -- great! Save it.
        """
        assert order is not None

        order.charges = float(order.charges) + message.latest_charge_amount.value
        if order.charges != message.total_charge_amount.value:
            raise AssertionError, 'Total charged amount does not match!'
        order.save()
        if order.charges == order.total:
            if order.state == 'NEW':
                # process order
                order.state = 'PROCESSING'
                self.process_order(order_id)
                order.save()
                # deliver order
                order.state = 'DELIVERED'
                self.deliver_order(order.google_id,
                                   carrier=None,
                                   tracking_number=None,
                                   send_email=True)
                order.save()

        return gmodel.ok_t()

    def handle_chargeback_amount(self, message, order_id, order, context):
        """
        Hmm, what should this do?
        """
        pass

    def handle_notification(self, message, order_id, order, context):
        """
        Handle the rest of the messages.
        This Demostrates that it is not neccessary to override specific
        handlers -- everything could be done inside this one handler.
        """
        assert order is not None

        if message.__class__ == gmodel.authorization_amount_notification_t:
            order.authorized += message.authorization_amount.value

        elif message.__class__ == gmodel.risk_information_notification_t:
            # do nothing -- ignore the message (but process it)
            return gmodel.ok_t()

        elif message.__class__ == gmodel.refund_amount_notification_t:
            order.refunds += message.latest_refund_amount.value
            if order.refunds != message.total_refund_amount.value:
                raise AssertionError('Total refunded amount does not match!')

        elif message.__class__ == gmodel.chargeback_amount_notification_t:
            order.chargebacks += message.latest_chargeback_amount.value
            if order.chargebacks != message.total_chargeback_amount.value:
                raise AssertionError('Total chargeback amount does not match!')

        else:
            # unknown message - return None to indicate that we can't process it
            return None

        order.save()

        return gmodel.ok_t()

    def on_exception(self, context, exception):
        """
        Lets log any exception occured in gchecky. Also save the sxception
        type and a brief explanation.
        """
        try:
            raise exception
        except LibraryError, e:
            tag = 'gchecky'
            error = 'Gchecky bug'
        except SystemError, e:
            tag = 'system'
            error = 'System failure'
        except HandlerError, e:
            tag = 'handler'
            error = 'Error in user handler method'
        except DataError, e:
            tag = 'data'
            error = 'Error converting data to/from XML'
        except:
            # Should never happen...
            tag = 'unknown'
            error = 'Unknown error'

        description = "%s:\n%s\n\nOriginal Error:\n%s\n%s" % (error,
                                                              exception,
                                                              exception.origin,
                                                              exception.traceback)
        # TODO: exception trace
        self.__log(context=context, tag=tag, error=error, description=description)
        return "%s\n\n%s" % (error, description)

    def on_xml_sent(self, context):
        """
        Log all the messages we've successfully sent to GC.
        """
        self.__log(context=context, tag='to')

    def on_xml_received(self, context):
        """
        Log all the messages we've successfully received from GC.
        """
        self.__log(context=context, tag='from')

    def __log(self, context, tag, error=None, description=None):
        """
        Helper method that logs everything into DB. It stores successfull
        transaction and errors in the same way, so that it would be easy
        to display it later.
        """
        order = None
        if context.order_id is not None:
            order = self.on_retrieve_order(order_id=context.order_id,
                                           context=context)

        message = Message(order       = order,
                          serial      = context.serial,
                          tag         = tag,
                          input_xml   = context.xml,
                          output_xml  = context.response_xml,
                          error       = error,
                          description = description)
        message.save()

__controller__ = None
def get_controller():
    """
    Dummy implementation of singleton. Use get_controller() to get
    the instance of controller.
    """
    from gchecky_common.controller import __controller__
    if __controller__ is None:
        import settings
        __controller__ = DjangoGController(
            vendor_id    = settings.gcheckout_vendor_id,
            merchant_key = settings.gcheckout_merchant_key,
            currency     = settings.gcheckout_currency,
            is_sandbox   = settings.gcheckout_is_sandbox,
            # Demo gchecky account is configured so that new orders are
            # automatically charged by Google, therefore do not send these
            # command, because it would be an error. However if your GC account
            # does not automatically charge new orders, then set this to True.
            automatically_charge = False)
    return __controller__
